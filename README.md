# 🚀 Prompt BI: Queryless Business Intelligence

## Where Conversation Meets Data

[![GitHub Workflow Status](https://img.shields.io/badge/Status-Hackathon%20Project-brightgreen)](https://github.com/CMKarth1kRaj/Prompt-BI)
[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Built-FF4B4B)](https://streamlit.io)

---

## ✨ 1. Introduction & The Problem

In today's data-rich environment, extracting timely insights is critical, yet often bottlenecked by technical barriers. Business executives need answers now, but relying on data teams for every report leads to delays and missed opportunities. Traditional BI tools are complex, requiring SQL or deep configuration knowledge.

**Prompt BI** is here to change that. We empower non-technical users to generate fully functional, interactive data dashboards using **only natural language prompts**. Think of it as having a dedicated data analyst, powered by AI, always at your fingertips.

---

## 💡 2. Our Solution: Prompt BI

Prompt BI transforms plain English questions into dynamic business intelligence dashboards in real-time. By leveraging the power of Large Language Models (LLMs) and a robust backend, we bridge the gap between business questions and data answers, making data accessible to everyone.

**Key Features:**
*   **Queryless BI:** Ask questions like "Show me monthly sales revenue for Q3 broken down by region."
*   **Real-time Dashboards:** Instantly generated, interactive Plotly charts.
*   **Data Agnostic:** Upload your own CSV files and immediately start querying.
*   **Conversational Memory:** Ask follow-up questions to refine your analysis.
*   **AI Data Summaries:** Get automated descriptions and insights about your uploaded data.
*   **LLM-as-a-Judge Testing:** A unique Admin Dashboard that uses AI to generate and evaluate test cases with detailed failure diagnostics.

---

## ⚙️ 3. Architecture Overview

Prompt BI is built on a streamlined, Python-centric architecture designed for rapid deployment and powerful insights.

### 3.1. Core Pipeline: Text to Dashboard
```mermaid
graph TD
    A["User Prompt"] --> B("Streamlit Chat UI")
    B --> C{"Context Engine:<br>CSV Schema & Chat History"}
    C --> D["Google Gemini API"]
    D -- "Generates JSON: SQL + Chart Config" --> E{"JSON Parser & Validator"}
    E --> F["PandasQL <br>(SQL on DataFrame)"]
    F --> G["Plotly Express <br>(Interactive Charts)"]
    G --> H["Streamlit <br>Dashboard Display"]
    H -- "Updates Chat History" --> B
```

**Components:**
*   **Frontend & Framework:** Streamlit provides a powerful, Python-native framework for building interactive web applications quickly.
*   **LLM Integration:** Google Gemini API (`gemini-2.5-flash`) is the brain, translating natural language into structured queries and visualization instructions.
*   **Data Engine:** Pandas for data manipulation, paired with `pandasql` to execute SQL queries directly on DataFrames, ensuring flexibility with uploaded CSVs.
*   **Visualization:** Plotly Express delivers rich, interactive, and aesthetically pleasing charts out-of-the-box.

### 3.2. Admin Testing Suite: LLM-as-a-Judge (Innovation Highlight!)
Our `admin_test.py` module introduces a groundbreaking approach to quality assurance:
*   **Dynamic Test Generation:** Gemini intelligently crafts diverse test prompts (Easy, Medium, Hard, Hallucination) based on the dataset schema.
*   **Detailed Failure Diagnostic:** The system runs these generated prompts through the core BI pipeline and automatically identifies exact reasons for failure—whether it's a SQL keyword gap, a chart mismatch, or a hallucinated response.
*   **Reliability Scoring:** Provides a real-time accuracy score, validating the robustness of our AI.

---

## 🛠️ 4. Getting Started (Local Setup)

Follow these steps to get Prompt BI running on your local machine.

### 4.1. Prerequisites
*   Python 3.9+
*   Google Gemini API Key (get yours from [Google AI Studio](https://aistudio.google.com/))

### 4.2. Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/CMKarth1kRaj/Prompt-BI.git
    cd Prompt-BI
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 4.3. Configuration
1.  Check for .env file or create one:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

### 4.4. Running the App
1.  **Main BI Dashboard:**
    ```bash
    streamlit run app.py
    ```
    Access the app at `http://localhost:8501`.

---

## 📈 5. Demo & Usage

1.  **Upload Your Data:** Start by uploading a `.csv` file via the sidebar. We recommend using the provided `nykaa_marketing_campaigns.csv` (or use your own data).
2.  **Chat Away:** Once the data is loaded, use the chat input at the bottom to ask questions in natural language.
    *   *Example:* "Show me the total revenue by campaign type."
    *   *Example:* "What is the average ROI for campaigns lasting more than 15 days?"
3.  **Admin Testing:** Navigate to the `🧪 Admin Test` tab in the sidebar to see our AI-powered QA in action. Generate tests by difficulty or add your own, and watch the system grade itself with real-time reports.

---

## 🎯 6. Evaluation Framework Alignment

*   **Accuracy (40 pts):** Proven via our **LLM-as-a-Judge Admin Test Suite** with automatic SQL validation.
*   **Aesthetics & UX (30 pts):** Clean, modern Dark Mode interface with interactive Plotly charts and custom design system.
*   **Approach & Innovation:** Text-to-SQL architecture with sophisticated hallucination handling and evaluation diagnostics.
*   **Bonus Points:** Supports conversational memory and is completely data-format agnostic.

---

## 🌟 8. Team & Acknowledgments

*   **CM Karthik Raj**
*   **Special Thanks:** To Google Gemini API for the LLM capabilities, Streamlit for the rapid prototyping, and the open-source data community.
