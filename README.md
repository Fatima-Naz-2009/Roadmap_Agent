# 🗺️ Roadmap Agent

An AI-powered learning roadmap generator built with **Python, Streamlit, Google Gemini, and the OpenAI Agents SDK**.

Roadmap Agent helps learners turn a learning goal into a structured, day-by-day study roadmap based on the amount of time they have available.

## 🚀 Live Demo

Try the working application here:

👉 [Roadmap Agent](https://roadmap-agent.streamlit.app/)

## ✨ Features

- 🤖 AI-generated personalized learning roadmaps
- 🎯 Takes the learner's specific learning goal
- 📅 Creates a roadmap based on the number of available days
- ⏱️ Considers the learner's available study time
- 🧠 Uses an AI Agent to structure and organize the learning plan
- 📄 Generates a PDF version of the roadmap
- 🌐 Simple and interactive Streamlit interface
- 🔐 Keeps API credentials in environment variables

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python** | Core application logic |
| **Streamlit** | Frontend and user interface |
| **Google Gemini API** | AI model used for roadmap generation |
| **OpenAI Agents SDK** | Building and running the AI agent |
| **FPDF** | Generating roadmap PDFs |
| **python-dotenv** | Loading environment variables |
| **re** | Text processing and formatting |
| **os** | Environment and system operations |

## 🧠 How It Works

The application follows a simple process:

text
User enters learning goal
        ↓
User enters available days
        ↓
User enters study time
        ↓
Roadmap Agent processes the request
        ↓
Gemini generates the learning roadmap
        ↓
Roadmap is displayed in Streamlit
        ↓
User can generate a PDF version


Roadmap_Agent/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
└── ...

CLone from here
git clone https://github.com/Fatima-Naz-2009/Roadmap_Agent.git
