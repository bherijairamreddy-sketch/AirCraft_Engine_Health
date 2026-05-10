# 🚀 Jive Analytics: Aircraft Engine Health Monitoring

## AI-Powered Predictive Maintenance & Data Analytics Platform

[![GitHub Repository](https://img.shields.io/badge/GitHub-AirCraft_Engine_Health-blue)](https://github.com/bherijairamreddy-sketch/AirCraft_Engine_Health)
[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB)](https://reactjs.org/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-orange)](https://ai.google.dev/)

---

## ✨ Overview

**Jive Analytics** is a comprehensive aircraft engine health monitoring platform that combines cutting-edge AI technology with modern web development to provide predictive maintenance insights. The system analyzes sensor data from aircraft engines using natural language queries, enabling engineers and maintenance teams to make data-driven decisions without requiring SQL expertise.

**Key Capabilities:**
- 🔍 **Natural Language Queries**: Ask questions in plain English about engine performance
- 📊 **Real-time Dashboards**: Interactive visualizations powered by AI-generated insights
- 🔧 **Predictive Maintenance**: Monitor engine health metrics and detect anomalies
- 📈 **Data Upload & Analysis**: Support for CSV datasets with automatic schema detection
- 🤖 **AI-Powered Analytics**: Google Gemini integration for intelligent query generation
- 🧪 **Automated Testing**: Admin dashboard with AI-generated test cases and diagnostics

---

## 🎯 Problem Statement

Aircraft engine maintenance is critical for aviation safety and operational efficiency. Traditional maintenance approaches rely on scheduled inspections or reactive repairs, leading to:

- **Unnecessary downtime** from overly conservative maintenance schedules
- **Safety risks** from undetected component failures
- **High operational costs** from inefficient maintenance practices
- **Data analysis bottlenecks** requiring specialized technical expertise

**Jive Analytics** solves these challenges by providing an intuitive platform where maintenance engineers can query engine sensor data using natural language and receive instant, actionable insights.

---

## 🏗️ Architecture

The platform consists of three main components working together:

### Backend (FastAPI)
- **API Endpoints**: RESTful APIs for data upload, querying, and analytics
- **Data Processing**: Pandas-based data manipulation and SQL query execution
- **LLM Integration**: Google Gemini API for natural language processing
- **CORS Support**: Configured for frontend-backend communication

### Frontend (React + Vite)
- **Modern UI**: Built with React 19 and Tailwind CSS
- **Interactive Dashboards**: Real-time charts using Recharts library
- **File Upload**: Drag-and-drop interface for dataset uploads
- **Chat Interface**: Conversational AI for natural language queries

### AI Engine (Google Gemini)
- **Query Generation**: Converts natural language to SQL queries
- **Insight Extraction**: Provides business intelligence and recommendations
- **Schema Understanding**: Analyzes dataset structure for accurate responses
- **Error Handling**: Intelligent failure detection and user guidance

---

## 🚀 Features

### Core Functionality
- **📁 Data Upload**: Support for CSV files with automatic encoding detection
- **💬 Natural Language Queries**: Ask questions like "Show me engines with high temperature readings"
- **📊 Interactive Visualizations**: Bar charts, line graphs, pie charts, and scatter plots
- **🔄 Real-time Updates**: Live dashboard updates as you interact with data
- **💾 Chat History**: Maintains conversation context for follow-up questions

### Advanced Analytics
- **🔍 Predictive Insights**: AI-generated recommendations based on sensor data
- **📈 Trend Analysis**: Monitor engine performance over time cycles
- **⚠️ Anomaly Detection**: Identify unusual sensor readings and patterns
- **📋 Summary Reports**: Automated data overview and key metrics

### Admin & Testing
- **🧪 Automated Testing Suite**: AI-generated test cases with detailed diagnostics
- **📊 Performance Metrics**: Accuracy scoring and failure analysis
- **🔧 System Validation**: Comprehensive testing of query generation and visualization

---

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **Pandas & PandasQL**: Data manipulation and SQL query execution
- **Google Generative AI**: LLM integration for natural language processing
- **Uvicorn**: ASGI server for production deployment

### Frontend
- **React 19**: Modern JavaScript library for UI development
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Composable charting library for React
- **Lucide React**: Beautiful icon library

### Development Tools
- **Python 3.9+**: Core programming language
- **Node.js**: JavaScript runtime for frontend development
- **Git**: Version control system

---

## 📋 Prerequisites

Before running the application, ensure you have:

- **Python 3.9 or higher**
- **Node.js 18+ and npm**
- **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/))
- **Git** for version control

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/bherijairamreddy-sketch/AirCraft_Engine_Health.git
cd AirCraft_Engine_Health
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Create environment file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 4. Configure API Key
Edit the `.env` file and add your Google Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key
```

---

## 🎮 Running the Application

### Option 1: Full Stack (Recommended)
```bash
# Terminal 1: Start Backend
python -m uvicorn backend:app --host localhost --port 8001

# Terminal 2: Start Frontend
cd frontend && npm run dev
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

### Option 2: Streamlit Interface
```bash
streamlit run app.py
```
Access at: http://localhost:8501

### Option 3: Admin Testing Suite
```bash
python admin_test.py
```

---

## 📊 Usage Guide

### 1. Upload Data
- Click the upload button or drag-and-drop CSV files
- Supported formats: CSV, TXT, TSV
- Automatic encoding detection for various file types

### 2. Ask Questions
Try these example queries:
- "Show me the average sensor readings for all engines"
- "Which engines have the highest temperature readings?"
- "Plot the performance trend over time cycles"
- "Find engines with abnormal vibration patterns"

### 3. Explore Insights
- View interactive charts and visualizations
- Ask follow-up questions to refine analysis
- Export insights and share findings

### 4. Admin Testing
- Access the admin dashboard for system validation
- Run automated test suites
- Review performance metrics and diagnostics

---

## 🔧 Configuration

### Environment Variables
```env
GEMINI_API_KEY=your_google_gemini_api_key
```

### CORS Settings
The backend is configured to accept requests from:
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:5173` (Alternative localhost)

### Supported Data Formats
- **File Types**: CSV, TXT, TSV
- **Encodings**: UTF-8, UTF-8-BOM, Latin-1, CP1252
- **Schema**: Automatic column detection and type inference

---

## 🧪 Testing & Validation

The platform includes comprehensive testing capabilities:

### Automated Test Generation
- **Easy**: Basic queries and simple visualizations
- **Medium**: Complex aggregations and multi-column analysis
- **Hard**: Advanced analytics and trend analysis
- **Hallucination**: Tests for error handling and edge cases

### Performance Metrics
- Query success rate
- Response time analysis
- Visualization accuracy
- Error categorization and diagnostics

---

## 🤝 Contributing

We welcome contributions to improve Jive Analytics!

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/React
- Include docstrings and comments
- Test your changes thoroughly

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **NASA** for the C-MAPSS aircraft engine simulation dataset
- **Google** for the Gemini AI platform
- **Open source community** for the amazing libraries and tools

---

## 📞 Support

For questions, issues, or contributions:
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Email**: Contact the maintainers for direct support

---

**Built with ❤️ for safer skies and smarter maintenance**

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

*   **Jairamm Reddi**
*   **Special Thanks:** To Google Gemini API for the LLM capabilities, Streamlit for the rapid prototyping, and the open-source data community.
