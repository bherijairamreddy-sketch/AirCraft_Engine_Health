from __future__ import annotations

import io
from typing import Any

import pandas as pd
import pandasql as psql
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm_integration import get_bi_response


app = FastAPI(title="Jive Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASET: dict[str, Any] = {"df": None, "context": "", "files": []}

C_MAPSS_COLUMNS = (
    ["unit", "cycle"]
    + [f"setting_{i}" for i in range(1, 4)]
    + [f"sensor_{i}" for i in range(1, 22)]
)


class AskRequest(BaseModel):
    question: str
    history: str = ""


def _read_table(raw: bytes, filename: str) -> pd.DataFrame | None:
    suffix = filename.lower().rsplit(".", 1)[-1]
    if suffix not in {"csv", "txt", "tsv"}:
        return None

    if suffix == "csv":
        last_error: Exception | None = None
        for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                df = pd.read_csv(io.BytesIO(raw), encoding=encoding, on_bad_lines="skip", engine="python")
                break
            except Exception as exc:
                last_error = exc
        else:
            raise ValueError(f"Could not read {filename}: {last_error}")
    else:
        text = raw.decode("utf-8", errors="ignore")
        df = pd.read_csv(io.StringIO(text), sep=r"\s+", header=None)
        if df.shape[1] == len(C_MAPSS_COLUMNS):
            df.columns = C_MAPSS_COLUMNS

    df = df.dropna(axis=1, how="all")
    df["source_file"] = filename
    return df


def _make_context(df: pd.DataFrame, files: list[str]) -> str:
    lines = [
        "### Uploaded files",
        *[f"- {name}" for name in files],
        "",
        "### DataFrame Schema",
    ]
    for col, dtype in df.dtypes.items():
        lines.append(f"- `{col}`: {dtype}")

    sample = df.head(5).to_string(index=False)
    return "\n".join(lines) + f"\n\n### First 5 Rows\n```\n{sample}\n```"


def _health_stage(row: pd.Series, rul_col: str | None) -> str:
    if rul_col:
        rul = row.get(rul_col)
        if pd.notna(rul):
            if rul <= 25:
                return "Critical"
            if rul <= 60:
                return "Moderate"
            if rul <= 110:
                return "Early"
            return "Healthy"
    return "Healthy"


def _dashboard_payload(df: pd.DataFrame, files: list[str]) -> dict[str, Any]:
    numeric_cols = df.select_dtypes("number").columns.tolist()
    unit_col = "unit" if "unit" in df.columns else None
    cycle_col = "cycle" if "cycle" in df.columns else None
    rul_col = "RUL" if "RUL" in df.columns else ("rul" if "rul" in df.columns else None)
    sensor_cols = [c for c in numeric_cols if str(c).startswith("sensor_")]

    engines = int(df[unit_col].nunique()) if unit_col else int(df["source_file"].nunique())
    max_cycle = int(df[cycle_col].max()) if cycle_col else len(df)
    missing_pct = round(float(df.isna().mean().mean() * 100), 1)

    working = df.copy()
    if rul_col:
        working["health_stage"] = working.apply(lambda row: _health_stage(row, rul_col), axis=1)
    elif cycle_col and unit_col:
        max_by_unit = working.groupby(unit_col)[cycle_col].transform("max")
        ratio = working[cycle_col] / max_by_unit
        working["health_stage"] = pd.cut(
            ratio,
            bins=[0, 0.45, 0.7, 0.88, 1.01],
            labels=["Healthy", "Early", "Moderate", "Critical"],
            include_lowest=True,
        ).astype(str)
    else:
        working["health_stage"] = "Healthy"

    latest = working
    if unit_col and cycle_col:
        latest = working.sort_values(cycle_col).groupby(unit_col, as_index=False).tail(1)

    stage_counts = (
        latest["health_stage"]
        .value_counts()
        .reindex(["Healthy", "Early", "Moderate", "Critical"], fill_value=0)
        .reset_index()
    )
    stage_counts.columns = ["stage", "count"]

    warning_count = int(stage_counts.loc[stage_counts["stage"].isin(["Early", "Moderate"]), "count"].sum())
    critical_count = int(stage_counts.loc[stage_counts["stage"].eq("Critical"), "count"].sum())
    healthy_count = int(stage_counts.loc[stage_counts["stage"].eq("Healthy"), "count"].sum())

    trend_col = sensor_cols[0] if sensor_cols else (numeric_cols[-1] if numeric_cols else None)
    trend = []
    if trend_col and cycle_col:
        trend_df = working.groupby(cycle_col, as_index=False)[trend_col].mean().tail(80)
        stride = max(len(trend_df) // 12, 1)
        trend = [
            {"cycle": str(int(row[cycle_col])), "value": round(float(row[trend_col]), 2)}
            for _, row in trend_df.iloc[::stride].iterrows()
        ]

    bar_data = stage_counts.to_dict("records")
    sensor_summary = []
    for col in sensor_cols[:6]:
        sensor_summary.append(
            {
                "name": col,
                "mean": round(float(working[col].mean()), 2),
                "max": round(float(working[col].max()), 2),
            }
        )

    return {
        "files": files,
        "summary": {
            "rows": int(len(df)),
            "columns": int(df.shape[1]),
            "engines": engines,
            "maxCycle": max_cycle,
            "missingPct": missing_pct,
        },
        "kpis": [
            {"label": "Engines Monitored", "value": str(engines), "note": f"{len(files)} files uploaded", "accent": True},
            {"label": "Healthy Engines", "value": str(healthy_count), "note": "Latest cycle status"},
            {"label": "Warning States", "value": str(warning_count), "note": "Early or moderate degradation"},
            {"label": "Critical Alerts", "value": str(critical_count), "note": "Maintenance review needed"},
        ],
        "trend": trend,
        "stages": bar_data,
        "sensorSummary": sensor_summary,
        "maintenance": latest.tail(5)[[c for c in [unit_col, cycle_col, "health_stage"] if c]].to_dict("records"),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)) -> dict[str, Any]:
    frames: list[pd.DataFrame] = []
    names: list[str] = []

    for file in files:
        raw = await file.read()
        df = _read_table(raw, file.filename)
        if df is not None and not df.empty:
            frames.append(df)
            names.append(file.filename)

    if not frames:
        raise HTTPException(status_code=400, detail="No readable CSV, TXT, or TSV files were uploaded.")

    df = pd.concat(frames, ignore_index=True, sort=False)
    DATASET["df"] = df
    DATASET["files"] = names
    DATASET["context"] = _make_context(df, names)
    return _dashboard_payload(df, names)


@app.post("/ask")
def ask(payload: AskRequest) -> dict[str, Any]:
    df = DATASET.get("df")
    if df is None:
        raise HTTPException(status_code=400, detail="Upload a dataset folder first.")

    config = get_bi_response(payload.question, DATASET["context"], payload.history)
    sql = config.get("sql")
    result_rows: list[dict[str, Any]] = []
    if sql and sql != "ERROR":
        try:
            result_df = psql.sqldf(sql, {"df": df})
            result_rows = result_df.head(100).where(pd.notna(result_df), None).to_dict("records")
        except Exception as exc:
            config = {
                "sql": "ERROR",
                "chart_type": "none",
                "x_axis": "",
                "y_axis": "",
                "insight": f"Could not execute generated SQL: {exc}",
            }

    return {"answer": config, "rows": result_rows}
