import streamlit as st
import pandas as pd
import json
import re
import time
import google.generativeai as genai
import os
from llm_integration import get_bi_response, _SYSTEM_PROMPT
from visualization import execute_and_plot

# Configure Gemini for test generation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
_test_gen_model = genai.GenerativeModel("gemini-2.5-flash")

def _parse_json_array(raw_text: str) -> list:
    """Safely extracts a JSON array from LLM output."""
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        st.error(f"Failed to parse JSON array from Gemini: {raw_text[:500]}")
        return []

def generate_dynamic_tests(dataset_context: str, difficulty: str, num_tests: int) -> list:
    """Asks Gemini to generate test cases based on the dataset schema."""
    hallucination_instruction = ""
    if difficulty == "Hallucination/Edge Case":
        hallucination_instruction = "CRITICAL: Generate questions about columns or data that DO NOT exist in the provided schema. The expected_sql_keywords MUST be exactly ['ERROR']. The expected_chart MUST be 'none'."
    else:
        hallucination_instruction = f"Generate {difficulty} difficulty questions based strictly on the provided schema. The expected_sql_keywords should be a list of 2-4 critical SQL keywords or column names needed to answer the question."

    prompt = f"""
You are an expert QA Engineer building an automated test suite for an AI Data Analyst.
Your task is to generate {num_tests} test cases based on this dataset schema:

--- DATASET CONTEXT ---
{dataset_context}
-----------------------

{hallucination_instruction}

You MUST return a STRICT JSON array with NO markdown formatting. Format exactly like this:
[
  {{
    "question": "The natural language question a user would ask.",
    "expected_sql_keywords": ["SUM", "GROUP BY", "ColumnName"],
    "expected_chart": "bar" // or "line", "pie", "scatter", "none", "ERROR"
  }}
]
"""
    try:
        response = _test_gen_model.generate_content(prompt)
        return _parse_json_array(response.text)
    except Exception as e:
        st.error(f"Testing generation failed: {e}")
        return []

def run_test_case(test_case: dict, dataset_context: str) -> dict:
    """Runs a single test case through the main pipeline and grades it."""
    question = test_case.get("question", "")
    expected_keywords = test_case.get("expected_sql_keywords", [])
    expected_chart = test_case.get("expected_chart", "none")
    
    # Run through the core AI pipeline
    result = get_bi_response(question, dataset_context, "")
    
    generated_sql = result.get("sql", "ERROR")
    generated_chart = result.get("chart_type", "none")
    
    # Grading logic & Failure Reason
    reasons = []
    chart_passed = (generated_chart.lower() == expected_chart.lower())
    if not chart_passed:
        reasons.append(f"Chart Mismatch: Expected '{expected_chart}', got '{generated_chart}'")
    
    sql_passed = True
    if "ERROR" in expected_keywords:
        if generated_sql != "ERROR":
            sql_passed = False
            reasons.append("Expected an ERROR response for this hallucination test, but Gemini generated SQL.")
    else:
        missing_kw = []
        for kw in expected_keywords:
            if kw.upper() not in generated_sql.upper():
                sql_passed = False
                missing_kw.append(kw)
        if missing_kw:
            reasons.append(f"SQL Missing Keywords: {', '.join(missing_kw)}")
                
    passed = chart_passed and sql_passed
    failure_reason = "; ".join(reasons) if not passed else "N/A"
    
    return {
        "Question": question,
        "Expected Chart": expected_chart,
        "Generated Chart": generated_chart,
        "Expected Keywords": ", ".join(expected_keywords),
        "Generated SQL": generated_sql,
        "Generated Insight": result.get("insight", ""),
        "Result": "Passed ✅" if passed else "Failed ❌",
        "Failure Reason": failure_reason,
        "Full Details": result
    }

def render_admin_dashboard(df: pd.DataFrame, dataset_context: str):
    """Renders the Admin Testing Dashboard UI in Streamlit."""
    st.markdown(
        """
        <div class="panel-header">
            <span class="panel-title">🤖 &nbsp; LLM-as-a-Judge Admin Dashboard</span>
        </div>
        <p style="color: #888; font-size: 0.9rem; margin-top: -10px; margin-bottom: 20px;">
            Dynamically generate test cases based on the current dataset schema, run them through the AI pipeline, and automatically grade the accuracy.
        </p>
        """,
        unsafe_allow_html=True
    )
    
    # --- AUTO-TEST INPUT ---
    st.markdown("### 🤖 Automated Dynamic Testing")
    with st.container(border=True):
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard", "Hallucination/Edge Case"])
        with col_t2:
            num_tests = st.number_input("Number of Tests to Generate", min_value=1, max_value=5, value=2)
        
        if st.button("Generate & Run Tests", use_container_width=True, type="primary"):
            with st.spinner(f"Generating {num_tests} {difficulty} test cases..."):
                tests = generate_dynamic_tests(dataset_context, difficulty, num_tests)
                
            if tests:
                results = []
                progress_text = "Running AI tests and grading..."
                my_bar = st.progress(0, text=progress_text)
                
                for i, t in enumerate(tests):
                    res = run_test_case(t, dataset_context)
                    res["Difficulty"] = difficulty
                    results.append(res)
                    my_bar.progress((i + 1) / len(tests), text=f"Executed Test {i+1}/{len(tests)}")
                
                time.sleep(0.5)
                my_bar.empty()
                st.session_state["test_results"] = results

    # --- RESULTS DISPLAY ---
    if "test_results" in st.session_state and st.session_state["test_results"]:
        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        # Preview Window Logic (shown at the top if active)
        if "preview_test_idx" in st.session_state and st.session_state["preview_test_idx"] is not None:
            idx = st.session_state["preview_test_idx"]
            if idx < len(st.session_state["test_results"]):
                res = st.session_state["test_results"][idx]
                
                # Floating-like container for preview
                st.markdown("""
                    <style>
                    .preview-window {
                        background: #141414;
                        border: 2px solid #F97316;
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 30px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                with st.container():
                    st.markdown('<div class="preview-window">', unsafe_allow_html=True)
                    col_h1, col_h2 = st.columns([0.9, 0.1])
                    col_h1.markdown(f"### 🔍 Gemini Test Preview: Case #{idx+1}")
                    if col_h2.button("✖️", key="close_preview_btn"):
                        st.session_state["preview_test_idx"] = None
                        st.rerun()
                    
                    # Simulated Chat UI
                    with st.chat_message("user"):
                        st.markdown(f"**Question:** {res['Question']}")
                        st.markdown(f"*Difficulty: {res.get('Difficulty', 'N/A')}*")
                    
                    with st.chat_message("assistant"):
                        # Re-visualize if needed (or we could have stored fig, but visualization needs data df)
                        # For simplicity in this admin view, we'll show the key components
                        st.markdown(res["Generated Insight"])
                        
                        if res["Generated SQL"] != "ERROR":
                            with st.expander("🛠️ View Generated SQL Query"):
                                st.code(res["Generated SQL"], language="sql")
                            
                            # Try to render the chart
                            if res["Generated Chart"] != "none":
                                fig, _insight, _result_df = execute_and_plot(res["Full Details"], df)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        # Compare with expected
                        st.markdown(f"**Status:** {res['Result']}")
                        if "Failed" in res['Result']:
                            st.error(f"**Failure Reason:** {res.get('Failure Reason', 'Unknown error')}")
                        
                        st.markdown(f"**Expected Keywords:** `{res['Expected Keywords']}`")
                        st.markdown(f"**Expected Chart:** `{res['Expected Chart']}` | **Actual Chart:** `{res['Generated Chart']}`")
                    
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 📊 Test Execution Results & Reports")
        
        results_df = pd.DataFrame(st.session_state["test_results"])
        passed_count = len(results_df[results_df["Result"] == "Passed ✅"])
        total_count = len(results_df)
        accuracy = (passed_count / total_count) * 100
        acc_color = "#22C55E" if accuracy >= 80 else ("#F59E0B" if accuracy >= 50 else "#EF4444")
        
        st.markdown(
            f"""
            <div style="background: #1A1A1A; border: 1px solid #333; border-radius: 10px; padding: 20px; text-align: center; margin-bottom: 25px;">
                <h4 style="color: #888; margin: 0; font-weight: 500;">System Accuracy Score</h4>
                <h1 style="color: {acc_color}; margin: 5px 0 0 0; font-size: 3rem;">{accuracy:.1f}%</h1>
                <p style="color: #666; margin: 0;">{passed_count} out of {total_count} tests passed successfully</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Interactive List instead of just dataframe
        st.markdown("#### 📋 Detailed Report Logs")
        
        # Header Row
        hcol1, hcol2, hcol3, hcol4 = st.columns([3, 1, 1, 1])
        hcol1.markdown("**Test Question**")
        hcol2.markdown("**Status**")
        hcol3.markdown("**Metric**")
        hcol4.markdown("**Action**")
        
        for idx, row in results_df.iterrows():
            with st.container():
                rcol1, rcol2, rcol3, rcol4 = st.columns([3, 1, 1, 1])
                rcol1.write(f"#{idx+1}: {row['Question']}")
                if "Failed" in row['Result']:
                    rcol1.markdown(f"<p style='color: #888; font-size: 0.75rem; margin-top: -10px;'>{row.get('Failure Reason', '')}</p>", unsafe_allow_html=True)
                
                status_color = "#22C55E" if "Passed" in row['Result'] else "#EF4444"
                rcol2.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{row['Result']}</span>", unsafe_allow_html=True)
                
                # Show some quick metric info
                rcol3.write(f"{row['Expected Chart']}")
                
                if rcol4.button("🔍 View Report", key=f"view_test_{idx}", use_container_width=True):
                    st.session_state["preview_test_idx"] = idx
                    st.rerun()
                
                st.markdown("<hr style='margin: 5px 0; opacity: 0.1;'>", unsafe_allow_html=True)
        
        if st.button("🗑️ Clear All Test Results", type="secondary"):
            del st.session_state["test_results"]
            if "preview_test_idx" in st.session_state:
                del st.session_state["preview_test_idx"]
            st.rerun()
