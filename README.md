# ⚡ NXTWATT — AI-Powered EV Charging Network

**Making EV charging smarter, more accessible, and community-powered.**

NXTWATT is a web-based EV charging platform concept designed to help electric vehicle users find charging options, discover suitable chargers, and connect with a community-powered charging network. It combines a web dashboard, a booking system, charger recommendations, and a locally running AI chatbot.

## 🚨 Problem Statement

Electric vehicle users may struggle to find convenient charging options, plan charging stops, and access charging facilities when they need them. At the same time, people with charging facilities or available charging capacity could potentially help nearby EV users.

NXTWATT explores how AI and a community-driven network can make the EV charging experience more convenient and accessible.

## 💡 Our Solution

NXTWATT provides a single interface for exploring charging options and interacting with an AI assistant.

### Key Features

- **🔌 Charger Discovery:** Browse and search available charger listings.
- **📍 Charger Filtering:** Narrow down options using the available search and filter features.
- **🤖 AI Chatbot:** Ask questions through a chatbot powered by the locally running Gemma model.
- **⚡ Charger Recommendations:** Get charger suggestions through the recommendation endpoint.
- **📅 Booking System:** Use the backend booking functionality to check available slots and submit bookings.
- **🏠 Community Charging Concept:** Explore the idea of connecting EV users with nearby hosts who may be able to offer charging.
- **🌱 Sustainability Focus:** Promote convenient EV charging and the potential for better use of charging resources.
- **🧠 Multi-Agent Workflow Concept:** Demonstrate a proposed workflow involving six agents. In the current prototype, this workflow is simulated and is not yet a fully autonomous multi-agent system.

## 🧠 AI and Agentic AI Approach

NXTWATT explores how AI agents could collaborate to support EV charging decisions.

The proposed workflow can be divided into six roles:

1. **User Intent Agent:** Understands the user's charging requirements.
2. **Charger Discovery Agent:** Identifies relevant charging options.
3. **Recommendation Agent:** Helps select suitable options.
4. **Availability Agent:** Supports checking charging-slot availability.
5. **Booking Agent:** Supports the booking process.
6. **Response Agent:** Presents useful information to the user.

These are the intended responsibilities of the proposed agent workflow. The current website includes a simulated six-agent demonstration; the local Gemma chatbot is implemented separately.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI |
| AI chatbot | Gemma 3 1B |
| Local model runtime | Ollama |
| HTTP communication | HTTPX |
| Database | SQLite |
| API testing | FastAPI Swagger UI |

## 🏗️ Project Structure

```text
Nxtwatt/
├── frontend/
│   ├── index.html
│   └── indexcopy.html
├── backend/
│   ├── main.py
│   ├── agents.py
│   ├── data.py
│   └── nxtwatt.db
└── README.md
```

The SQLite database is used by the project for local data storage. The exact database contents and schema depend on the current implementation.

## ⚙️ Installation and Setup

### Prerequisites

Install the following:

- Python
- Git
- Ollama
- A web browser

### Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Nxtwatt
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual GitHub repository URL.

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### Step 3: Install Python dependencies

```bash
python -m pip install fastapi uvicorn httpx
```

If the project has additional Python dependencies, install those as well.

### Step 4: Set up the AI model

Install Ollama, then download the model:

```bash
ollama pull gemma3:1b
```

Make sure Ollama is running locally and the model is available before testing the chatbot.

### Step 5: Start the backend

From the project root directory, run:

```bash
python -m uvicorn backend.main:app --reload
```

The application will normally be available at:

- **Website:** http://localhost:8000/
- **API documentation:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

Keep the backend terminal running while using the website.

## 🔗 API Endpoints

The prototype includes the following backend endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Check backend health |
| `POST /api/gemma` | Send a message to the local Gemma chatbot |
| `POST /api/recommend` | Request charger recommendations |
| `GET /api/bookings/slots/{charger_id}` | Check booking slots for a charger |
| `POST /api/bookings` | Submit a charger booking |

Refer to the interactive API documentation at `/docs` for the request formats and available responses.

## 🔐 Privacy and Security

The chatbot uses a local Gemma model through Ollama rather than requiring a paid cloud AI API for its current local setup.

The application is a prototype. Before public deployment, additional work may be required for authentication, input validation, database security, rate limiting, and protection of user information.

## 🚧 Current Limitations and Future Scope

Planned improvements include:

- Implementing genuinely collaborating AI agents.
- Integrating verified real-world charger locations and live availability.
- Developing location-aware matching between EV users and charging hosts.
- Adding secure user accounts and booking management.
- Exploring payments and incentives for community charging hosts.
- Improving recommendations using charging requirements and availability data.
- Deploying the application for public access.

Community charging and payments are proposed future capabilities and should not be considered live services in the current prototype.

## 🎯 Hackathon Objective

Our goal is to explore how AI-assisted recommendations, local language-model inference, booking functionality, and a community-powered charging concept can contribute to a more accessible EV charging experience.

NXTWATT is an early-stage prototype built to demonstrate the concept and provide a foundation for future development.

## 👥 Team

**Team Name:** NXTWATT  
**Event:** HackOctober 2026  
**Team Members:** Add the names of all four team members here.

---

*Built with ⚡ and a vision for smarter, more accessible EV charging.*