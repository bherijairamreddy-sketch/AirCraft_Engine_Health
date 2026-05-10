import json
import re
import google.generativeai as genai

import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini with the project API key from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_gemini_model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_model = genai.GenerativeModel("gemini-2.5-flash")


def _missing_api_key_response() -> dict:
    return {
        "sql": "ERROR",
        "chart_type": "none",
        "x_axis": "",
        "y_axis": "",
        "insight": (
            "Gemini AI is not configured yet. Add GEMINI_API_KEY to a .env "
            "file in the project folder to enable Talk to Data."
        ),
    }

# ── System Prompt ─────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """
You are an expert Data Analyst. You are given a user's question, the context of
previous questions (chat history), and the schema of a dataset (column names,
types, and sample rows).

Your job is to return a STRICT, valid JSON object with NO markdown formatting,
NO backticks, and NO extra text.

The JSON must have these exact keys:
- "sql": A valid SQLite query to answer the user's question. The table name is ALWAYS `df`.
- "chart_type": Choose the best visualization. Must be one of: ["bar", "line", "pie", "scatter", "none"]. Use "none" if the answer is just a single number or text.
- "x_axis": The exact column name from the SQL result to use for the X-axis (or labels for pie charts). Empty string if none.
- "y_axis": The exact column name from the SQL result to use for the Y-axis (or values for pie charts). Empty string if none.
- "insight": A 1-2 sentence business insight answering the user's question.

CRITICAL HALLUCINATION RULE: If the user's question CANNOT be answered using
the provided dataset schema, set "sql" to "ERROR" and politely explain why in
the "insight" field. Do NOT make up data.
"""


def _parse_gemini_response(raw_text: str) -> dict:
    """
    Cleans and parses the raw Gemini response into a Python dict.
    Strips any accidental ```json ... ``` or ``` ... ``` fences,
    then runs json.loads().
    Returns the parsed dict, or an error dict if parsing fails.
    """
    # Strip markdown code fences (```json\n...\n``` or ```...```)
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Return a safe error dict so the caller can always .get() the keys
        return {
            "sql": "ERROR",
            "chart_type": "none",
            "x_axis": "",
            "y_axis": "",
            "insight": (
                f"⚠️ Gemini returned an unexpected format and could not be parsed. "
                f"Raw error: {e}. Raw response snippet: {raw_text[:300]}"
            ),
        }


def get_bi_response(user_query: str, dataset_context: str, chat_history: str = "") -> dict:
    """
    Sends the user query + dataset schema + chat history to Gemini
    and returns a parsed dict with keys:
      sql, chart_type, x_axis, y_axis, insight
    """
    if _gemini_model is None:
        return _missing_api_key_response()

    prompt = f"""
{_SYSTEM_PROMPT}

--- DATASET CONTEXT ---
{dataset_context}

--- CHAT HISTORY ---
{chat_history if chat_history else "(No prior conversation)"}

--- USER QUESTION ---
{user_query}
"""
    try:
        response = _gemini_model.generate_content(prompt)
        raw = response.text
    except Exception as e:
        return {
            "sql": "ERROR",
            "chart_type": "none",
            "x_axis": "",
            "y_axis": "",
            "insight": f"⚠️ Gemini API error: {e}",
        }

    return _parse_gemini_response(raw)

def generate_dashboard_overview(dataset_context: str) -> dict:
    """
    Generates a brief summary of the dataset and 2 meaningful chart configurations
    for the main dashboard view.
    """
    if _gemini_model is None:
        return {
            "summary": (
                "AI overview unavailable because GEMINI_API_KEY is not set. "
                "Add it to a .env file in the project folder to enable Gemini-powered insights."
            ),
            "chart1": None,
            "chart2": None,
        }

    prompt = f"""
You are an expert Data Analyst. Given this dataset context, provide:
1. A summary (2-3 sentences) of what the data represents.
2. Two JSON objects for the most insightful charts (bar, line, or pie).
3. A list of 3-4 key business metrics (KPIs) relevant to the dataset (e.g., Total Profit, Campaign Spending, Loss, Revenue, Total Orders, etc.) along with the SQL to calculate them.

Return ONLY a valid JSON object with this structure:
{{
  "summary": "...",
  "metrics": [
    {{ "label": "Revenue", "sql": "SELECT SUM(amount) FROM df", "prefix": "$", "suffix": "" }},
    ...
  ],
  "chart1": {{ "sql": "...", "chart_type": "...", "x_axis": "...", "y_axis": "...", "insight": "..." }},
  "chart2": {{ "sql": "...", "chart_type": "...", "x_axis": "...", "y_axis": "...", "insight": "..." }}
}}

Constraint: Table name must be `df`. Do NOT include any text outside the JSON.

Dataset Context:
{dataset_context}
"""
    try:
        response = _gemini_model.generate_content(prompt)
        raw_text = response.text
        # More robust JSON extraction: find the first { and last }
        start_idx = raw_text.find("{")
        end_idx = raw_text.rfind("}")
        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON object found in response.")
        
        json_str = raw_text[start_idx:end_idx+1]
        data = json.loads(json_str)
        
        return data
        
    except Exception as e:
        return {
            "summary": f"AI Summary unavailable. (Error: {e})",
            "chart1": None,
            "chart2": None
        }
