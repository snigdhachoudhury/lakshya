# 💰 Lakshya AI - AI-Powered Financial Strategy Engine

An intelligent personal finance mentor built for Indian investors. Upload your CAMS statement, get a portfolio X-Ray, assess your financial health, and plan your path to FIRE — all in one place.

![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=flat-square)
![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square)

---

## Features

- **Portfolio X-Ray** — Upload CAMS PDF statements to detect fund overlap, identify savings leaks, and get rebalancing suggestions
- **Financial Health Score** — 0-100 score across income, emergency fund, debt, and investment rate
- **FIRE Projection** — Monte Carlo simulation projecting retirement timeline and probability
- **Real-time AI Insights** — Powered by Google Gemini 1.5 Flash

---

## Architecture
```
React Frontend (Port 3000)
        │ Axios REST
        ↓
FastAPI Backend (Port 8000)
        │
        ├── Portfolio X-Ray Agent
        ├── Health Score Agent
        └── FIRE Planner Agent
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.9+ |
| AI Engine | Google Gemini 1.5 Flash |
| PDF Processing | LlamaCloud |
| Financial Math | NumPy, SciPy, Pandas |
| Frontend | React 18, Tailwind CSS, Recharts |
| Infra | Docker, Docker Compose |

---

## Setup

### Prerequisites
- Python 3.9+, Node.js 18+, Docker (optional)
- API keys: `GOOGLE_API_KEY`, `LLAMA_CLOUD_API_KEY`

### Environment Variables
Create a `.env` file in the root:
```bash
GOOGLE_API_KEY=your_google_api_key
LLAMA_CLOUD_API_KEY=your_llama_api_key
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Run with Docker (Recommended)
```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Run Locally
```bash
# Backend
cd backend && pip install -r requirements.txt && python main.py

# Frontend
cd frontend && npm install && npm start
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze-portfolio` | Upload CAMS PDF, get fund analysis |
| POST | `/get-health-score` | Submit financials, get health score |
| POST | `/project-fire` | Run Monte Carlo FIRE simulation |

---

## AI Agents

**PortfolioXRay** — Parses CAMS statements, calculates XIRR, detects overlap, flags underperforming funds

**HealthScore** — Scores financial health across 6 dimensions: income ratio, emergency fund, debt, tax, insurance, retirement readiness

**FIREPlanner** — Runs 10,000 Monte Carlo scenarios, outputs probability of FIRE by target date with required SIP amounts

---

## Roadmap

- [ ] PostgreSQL integration for persistent storage
- [ ] JWT-based multi-user authentication
- [ ] Direct broker API integration
- [ ] Tax optimization recommendations
- [ ] Mobile app (React Native)

---

**Built for Indian investors. Powered by AI. Made for financial independence.**
