# 🥗 NutriCare AI — Personalised Nutrition Agentic Application

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![IBM Granite](https://img.shields.io/badge/IBM%20Granite-3.3--8B-054ADA?logo=ibm&logoColor=white)
![watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-BE95FF?logo=ibm&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**An AI-powered, web-based Nutrition Planning application built with IBM Granite 3.3 on IBM watsonx.ai**

[Features](#-features) · [Demo](#-screenshots) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Ethics](#-ai-ethics--guardrails) · [Disclaimer](#-medical-disclaimer)

</div>

---

## 📌 Overview

**NutriCare AI** is an Agentic AI application that uses IBM Granite LLM (`ibm/granite-3-3-8b-instruct`) hosted on IBM watsonx.ai to generate fully personalised, medically aware nutrition plans and answer free-form nutrition queries in real time.

The application collects user details — name, age, gender, location, dietary preferences, medical history, and health goals — and uses IBM Granite to generate a comprehensive 7-day meal plan tailored to the individual. A conversational Q&A assistant allows users to ask any follow-up nutrition question with context-aware responses.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **IBM Granite LLM** | `ibm/granite-3-3-8b-instruct` via watsonx.ai REST API |
| 📋 **Personalised Plans** | 7-day meal plan with calories, macros, micronutrients |
| 👤 **Full User Profiling** | Name, age, gender, city/country, diet, activity, goals, allergies |
| 🏥 **Medical Awareness** | Handles diabetes, hypertension, PCOS, thyroid, kidney disease & more |
| 💬 **Agentic Q&A Chat** | Context-aware nutrition assistant with suggested questions |
| 🛡️ **AI Ethics Guardrails** | 3-layer input/output safety filtering — blocks harmful advice |
| 💚 **HAM Principles** | Helpful, Accountable, Mindful communication framework |
| 🌍 **Cultural Sensitivity** | Location-aware, culturally appropriate food recommendations |
| ⚕️ **Medical Disclaimer** | Attached to every plan and response |
| 🖨️ **Print / PDF Export** | Browser print-to-PDF for saving your plan |

---

## 🗂️ Project Structure

```
Nutrition-Agent/
├── app.py                    # Flask web server — entry point
├── requirements.txt          # Python dependencies
├── env.example               # Environment variable template
├── README.md                 # This file
├── .gitignore                # Git ignore rules
│
├── agents/
│   ├── __init__.py
│   ├── granite_client.py     # IBM Granite LLM REST API client (IAM auth + inference)
│   ├── nutrition_agent.py    # Agentic logic — plan generation & Q&A prompts
│   └── guardrails.py         # AI ethics & safety content filters
│
├── templates/
│   └── index.html            # Main 3-tab web UI (Jinja2 template)
│
└── static/
    ├── css/
    │   ├── style.css          # Main stylesheet
    │   └── plan.css           # Nutrition plan output formatting
    └── js/
        └── app.js             # Frontend JavaScript (tabs, forms, chat)
```

---

## 🚀 Quick Start

### Prerequisites

- Python **3.9** or higher
- `pip` package manager
- Internet access (IBM watsonx.ai API calls)
- A valid IBM Cloud API key with watsonx.ai access

### 1. Clone the repository

```bash
git clone https://github.com/yashodhanmane/Nutrition-Agent.git
cd Nutrition-Agent
```

### 2. Create a virtual environment (recommended)

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and edit it with your credentials:

```bash
cp env.example .env
```

Edit `.env`:

```env
IBM_API_KEY=your_ibm_cloud_api_key
IBM_PROJECT_ID=your_watsonx_project_id
IBM_ENDPOINT=https://au-syd.ml.cloud.ibm.com
PORT=5000
FLASK_DEBUG=false
```

> ⚠️ **Never commit your `.env` file** — it is listed in `.gitignore` by default.

### 5. Run the application

```bash
python app.py
```

Open your browser: **http://localhost:5000**

---

## 🔌 API Reference

### `GET /api/health`
Returns service health status.

**Response:**
```json
{
  "status": "ok",
  "service": "Nutrition Agentic AI",
  "model": "IBM Granite"
}
```

---

### `POST /api/generate-plan`
Generates a personalised 7-day nutrition plan.

**Request body:**
```json
{
  "name": "Priya Sharma",
  "age": "35",
  "gender": "Female",
  "city": "Mumbai",
  "country": "India",
  "diet_preference": "Vegetarian",
  "activity_level": "Moderately Active",
  "goals": ["Weight Loss", "Manage Blood Sugar"],
  "medical_history": ["Type 2 Diabetes", "High Blood Pressure"],
  "allergies": ["Dairy"]
}
```

**Response:**
```json
{
  "success": true,
  "plan": "## Your Personalised Nutrition Plan\n...",
  "warning": "",
  "disclaimer": "IMPORTANT MEDICAL DISCLAIMER..."
}
```

---

### `POST /api/query`
Answers a free-form nutrition question with user context.

**Request body:**
```json
{
  "query": "What foods help manage blood sugar levels?",
  "user_context": {
    "name": "Priya",
    "diet_preference": "Vegetarian",
    "medical_history": ["Type 2 Diabetes"],
    "city": "Mumbai",
    "country": "India"
  }
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Great question, Priya! For managing blood sugar...",
  "warning": "",
  "disclaimer": "IMPORTANT MEDICAL DISCLAIMER..."
}
```

---

### `GET /api/disclaimer`
Returns the full medical disclaimer text.

---

## 🧠 Agentic AI Architecture

```
User Browser
     │
     ├─ POST /api/generate-plan ──┐
     └─ POST /api/query ──────────┤
                                  ▼
                          ┌──────────────┐
                          │  Guardrails  │  ← Input safety check
                          │  (Layer 1)   │
                          └──────┬───────┘
                                 │ Safe ✓
                                 ▼
                          ┌──────────────┐
                          │  Nutrition   │  ← Prompt builder
                          │   Agent      │    (HAM persona + user context)
                          └──────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  IBM Granite 3.3-8B    │  ← watsonx.ai au-syd
                    │  ibm/granite-3-3-8b-   │
                    │  instruct              │
                    └────────────┬───────────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │  Guardrails  │  ← Output safety filter
                          │  (Layer 2)   │
                          └──────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  + Medical Disclaimer  │  ← Always appended
                    └────────────────────────┘
                                 │
                                 ▼
                          User Browser
```

---

## 🛡️ AI Ethics & Guardrails

NutriCare AI follows a **3-layer safety architecture**:

### Layer 1 — Input Filtering
Regex-based blocking of dangerous content patterns:
- Self-harm, extreme fasting, crash diets
- Laxative/diuretic abuse, purging
- Illegal supplements, steroids
- Overdose-related queries

### Layer 2 — Sensitive Topic Detection
Automatically flags topics requiring extra medical caution:
- Chemotherapy, cancer treatment, dialysis
- Organ transplant, eating disorders (anorexia, bulimia)
Adds a prominent caution banner to the response.

### Layer 3 — Output Post-Processing
- Scans and removes any inadvertent harmful instructions from model output
- Always appends the full medical disclaimer
- Prevents leakage of blocked content patterns

### HAM Framework
The IBM Granite model is instructed to follow **H**elpful, **A**ccountable, **M**indful principles:
- **Helpful** — practical, evidence-based, actionable advice
- **Accountable** — always recommends professional consultation
- **Mindful** — culturally sensitive, inclusive, respectful of all body types and backgrounds

---

## 🔧 Technology Stack

| Component | Technology |
|---|---|
| **LLM** | IBM Granite 3.3 8B Instruct (`ibm/granite-3-3-8b-instruct`) |
| **AI Platform** | IBM watsonx.ai (Sydney region — `au-syd`) |
| **Authentication** | IBM Cloud IAM (API Key → Bearer Token) |
| **Backend** | Python 3.9+ · Flask 3.x · Flask-CORS |
| **Frontend** | HTML5 · CSS3 · Vanilla JavaScript (ES6) |
| **HTTP Client** | `requests` library |

---

## 🌐 Regional Availability

This application is configured for the **Sydney (`au-syd`)** IBM watsonx.ai endpoint.  
The `ibm/granite-3-3-8b-instruct` model is also available in:

| Region | Endpoint |
|---|---|
| Sydney (default) | `https://au-syd.ml.cloud.ibm.com` |
| Dallas | `https://us-south.ml.cloud.ibm.com` |
| Toronto | `https://ca-tor.ml.cloud.ibm.com` |

To switch region, update `IBM_ENDPOINT` in your `.env` file.

---

## ⚕️ Medical Disclaimer

> **IMPORTANT:** The nutrition information and plans provided by this application are generated by an AI model for **general educational purposes only**. They do **NOT** constitute medical advice, diagnosis, or treatment.
>
> - Always consult a qualified healthcare professional or registered dietitian before making significant changes to your diet.
> - People with diabetes, hypertension, kidney disease, cardiovascular conditions, or any chronic illness should seek personalised medical guidance from a licensed physician.
> - This tool is **not** a substitute for professional medical advice.
> - In case of a medical emergency, contact emergency services immediately.
>
> IBM and the developers of this application are not liable for any health outcomes resulting from the use of this information.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👤 Author

**Yashodhan Mane**  
GitHub: [@yashodhanmane](https://github.com/yashodhanmane)

---

*Built for IBM Faculty Development Programme (FDP) — Agentic AI with IBM Granite on watsonx.ai*
