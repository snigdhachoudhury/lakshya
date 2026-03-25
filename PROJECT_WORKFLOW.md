# Lakshya AI - Project Workflow Documentation

## Overview
**Lakshya** is an AI-powered personal finance mentoring application for Indian investors. It helps users analyze their investment portfolios, assess financial health, and project retirement (FIRE - Financial Independence, Retire Early) goals.

**Tech Stack:**
- **Backend**: FastAPI (Python) with AI agents for financial analysis
- **Frontend**: React 18 with React Router and Tailwind CSS
- **Communication**: REST API via Axios
- **State**: localStorage for client-side persistence
- **Database**: In-memory during session (no persistent DB)

---

## 1. ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER (Port 3000)                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               REACT FRONTEND (SPA)                       │   │
│  │  ├─ LandingPage (Public signup)                          │   │
│  │  ├─ Dashboard (Main hub)                                 │   │
│  │  ├─ XRayPage (Portfolio upload & analysis)              │   │
│  │  ├─ HealthScorePage (Financial health assessment)       │   │
│  │  ├─ FIREPage (Retirement projection)                    │   │
│  │  ├─ ProfilePage (User settings)                         │   │
│  │  └─ BottomNav (Mobile navigation)                       │   │
│  │                                                          │   │
│  │  State: localStorage (userData persists across visits)   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         ↓ (Axios HTTP)                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND (Port 8000)                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              API ROUTES (/api/v1)                        │   │
│  │  ├─ POST /analyze-portfolio (Portfolio X-Ray)           │   │
│  │  ├─ POST /get-health-score (Money Health Score)         │   │
│  │  └─ POST /project-fire (FIRE Projection)                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         ↓                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           CORE PROCESSING LAYER                          │   │
│  │  ├─ StatementParser (Parse CAMS PDF)                    │   │
│  │  └─ FinancialEngine (Calculate XIRR, returns, etc.)     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         ↓                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │          AI AGENTS (Business Logic)                      │   │
│  │  ├─ PortfolioXRay (Fund overlap, savings leak)          │   │
│  │  ├─ MoneyHealthScore (0-100 financial health)           │   │
│  │  └─ FIREPlanner (Monte Carlo retirement simulation)     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. USER JOURNEY & AUTHENTICATION FLOW

### Step 1: Landing Page (Public)
```
User visits http://localhost:3000
  ↓
LandingPage.jsx displays:
  - Dark premium hero section
  - Email signup form
  - CTA buttons (Get Started, Features)
  
User enters email → handleSignup() → localStorage saved
  ↓
userData object created: { email, createdAt }
  ↓
Redirected to /dashboard
```

### Step 2: Dashboard (Protected)
```
User redirected to /dashboard
  ↓
Header shows:
  - User email in profile dropdown
  - Navigation to all features
  
Dashboard displays:
  - 4 Summary cards (empty initially)
    • Portfolio Value (from X-Ray)
    • Annual XIRR (from X-Ray)
    • Health Score (from Health assessment)
    • FIRE Probability (from Fire calculation)
  
  - 4 Action cards:
    • "Upload Portfolio" → links to /xray
    • "Check Health" → links to /health
    • "Plan FIRE" → links to /fire
    • "View Profile" → links to /profile
```

### Step 3: Protected Routes (Authenticated Users Only)
```
Available routes:
  /dashboard     - Main hub
  /xray          - Portfolio analysis
  /health        - Financial assessment
  /fire          - Retirement projection
  /profile       - User settings
  *              - Redirect to landing if not authenticated
```

---

## 3. FRONTEND STRUCTURE

### Components
```
src/
├── App.js (Router, Auth logic, localStorage)
├── components/
│   ├── LandingPage.jsx        (Signup, public page)
│   ├── Dashboard.jsx          (Main dashboard)
│   ├── XRayPage.jsx           (Portfolio file upload)
│   ├── HealthScorePage.jsx    (Health assessment form)
│   ├── FIREPage.jsx           (Retirement calculator)
│   ├── ProfilePage.jsx        (User profile/settings)
│   ├── Header.jsx             (Top navigation)
│   └── BottomNav.jsx          (Mobile bottom tabs)
└── styles/
    └── tailwind.css           (Custom color palette)
```

### State Management
**localStorage Key**: `lakshya_user_data`

```javascript
userData = {
  email: "user@example.com",
  createdAt: "2026-03-25T10:30:00Z",
  profileData: {
    age: 32,
    income: 75000,
    monthlyInvestment: 15000
  },
  portfolioData: {
    totalValue: 250000,
    xirr: 0.12,
    holdings: [...]
  },
  healthScore: 65,
  fireProjection: {...}
}
```

### Styling
- **Theme**: Dark mode with black backgrounds (`bg-black`)
- **Primary Accent**: Gold (`#d4af37` / `yellow-500`)
- **Cards**: Slate gray with transparency (`bg-slate-800/50`)
- **Text**: White (`text-white`)
- **CSS Framework**: Tailwind CSS

---

## 4. BACKEND STRUCTURE

### Entry Point: main.py
```python
from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI(title="Project Lakshya: AI Money Mentor")

# CORS middleware - allows frontend (port 3000) to call backend (port 8000)
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Include all API routes
app.include_router(api_router, prefix="/api/v1")

# Runs on: http://0.0.0.0:8000
```

### API Routes: api/routes.py
**Three main endpoints:**

#### Endpoint 1: `/api/v1/analyze-portfolio`
```
Method: POST
Request:
  - file: PDF (CAMS portfolio statement)

Process:
  1. Parse PDF using StatementParser
  2. Extract holdings and transactions
  3. Run PortfolioXRay agent for:
     - Fund overlap detection
     - Savings leak (Regular vs Direct fund comparison)
  4. Calculate XIRR using FinancialEngine
  
Response:
{
  "portfolio_value": 250000,
  "xirr": "12.50%",
  "overlap_report": {...},
  "annual_savings_potential": 45000,
  "holdings_count": 15
}
```

#### Endpoint 2: `/api/v1/get-health-score`
```
Method: POST
Request:
  {
    "metrics": {
      "portfolio_value": 250000,
      "xirr": 0.125,
      "emergency_fund": 50000
    },
    "profile": {
      "age": 32,
      "income": 75000,
      "dependents": 2
    }
  }

Process:
  1. MoneyHealthScore agent analyzes:
     - Asset allocation
     - Emergency fund adequacy
     - Income to portfolio ratio
     - Risk profile alignment
  
Response:
{
  "score": 65,
  "category": "Moderate",
  "breakdown": {
    "asset_allocation": 70,
    "liquidity": 60,
    "diversification": 65,
    "risk_management": 55
  },
  "recommendations": [...]
}
```

#### Endpoint 3: `/api/v1/project-fire`
```
Method: POST
Request:
  {
    "current_savings": 250000,
    "monthly_sip": 15000,
    "target": 5000000,
    "years_horizon": 20
  }

Process:
  1. FIREPlanner runs Monte Carlo simulation
  2. 10,000 iterations with:
     - Random market returns
     - Inflation adjustments
     - SIP continuity
  
Response:
{
  "success_probability": 0.78,
  "median_completion_age": 45,
  "percentile_10": 42,
  "percentile_90": 52,
  "simulation_results": [...]
}
```

### Core Processing: core/
```
core/
├── parser.py         → StatementParser (PDF parsing via LlamaCloud)
├── math_utils.py     → FinancialEngine (XIRR, returns, IRR)
└── config.py         → Configuration & constants
```

### AI Agents: agents/
```
agents/
├── portfolio_xray.py   → PortfolioXRay class
│   Methods:
│   - calculate_overlap_matrix()      (same funds across schemes)
│   - detect_regular_to_direct_savings() (fee comparison)
│
├── health_score.py     → MoneyHealthScore class
│   Methods:
│   - get_comprehensive_score()       (0-100 score)
│
└── fire_planner.py     → FIREPlanner class
    Methods:
    - run_monte_carlo()                (simulation)
```

---

## 5. DATA FLOW DIAGRAMS

### Flow 1: Portfolio Upload → Analysis
```
User uploads PDF
       ↓
Frontend/XRayPage sends file to /api/v1/analyze-portfolio
       ↓
Backend StatementParser reads PDF
       ↓
PortfolioXRay agent analyzes holdings
       ↓
FinancialEngine calculates XIRR
       ↓
Returns response with portfolio metrics
       ↓
Frontend receives & stores in userData.portfolioData
       ↓
XRayPage displays:
  - Overlap matrix
  - XIRR percentage
  - Annual savings potential
```

### Flow 2: Health Assessment
```
User fills form on HealthScorePage with:
  - Age, income, dependents
  - Current portfolio value
       ↓
Frontend sends POST to /api/v1/get-health-score
       ↓
MoneyHealthScore analyzes metrics
       ↓
Returns score (0-100) + breakdown
       ↓
Frontend displays:
  - Large health score circle
  - Category badge
  - Radar chart with breakdowns
  - Actionable recommendations
```

### Flow 3: FIRE Projection
```
User enters on FIREPage:
  - Current savings amount
  - Monthly SIP amount
  - Target corpus
  - Investment horizon (years)
       ↓
Frontend sends POST to /api/v1/project-fire
       ↓
FIREPlanner runs 10,000 Monte Carlo simulations
       ↓
Returns success probability + distribution
       ↓
Frontend displays:
  - Success probability percentage
  - Completion age range (10th, 50th, 90th percentile)
  - 3D visualization (optional)
```

---

## 6. KEY FEATURES EXPLAINED

### Portfolio X-Ray
**Purpose**: Identify inefficiencies in mutual fund portfolio
**Detects**:
- Overlapping funds (same company across regular & direct)
- Fee leakage (Regular plans charge more than Direct)
- Diversification gaps

**Example Output**:
```
Overlap Report:
  - HDFC Growth (Regular) + HDFC Growth (Direct) detected
  - Annual leak: ₹3,000 (fees difference)

Fund Overlap Matrix:
  15 holdings across SIP categories
  3 funds found in multiple schemes
```

### Money Health Score
**Purpose**: Holistic financial wellness assessment (0-100)
**Metrics**:
- Asset Allocation (diversification)
- Liquidity (emergency fund)
- Risk Alignment (age vs risk)
- Diversification (sector spread)

**Example Output**:
```
Score: 65/100 "Moderate"
  Asset Allocation: 70
  Liquidity: 60
  Diversification: 65
  Risk Management: 55

Recommendations:
  - Increase emergency fund by ₹50,000
  - Diversify into value stocks
  - Review insurance adequacy
```

### FIRE Projector
**Purpose**: Retirement timeline & probability calculator
**Simulation**: 10,000 Monte Carlo iterations
**Returns**:
- Success probability (reach ₹50L target)
- Timeline distribution (10th/50th/90th percentile ages)
- Range of outcomes

**Example Output**:
```
Target Corpus: ₹50,00,000
Success Probability: 78%
Median Completion Age: 45 years
Range: 42 to 52 years

With ₹15,000/month SIP from ₹2,50,000 base
Initial funds can compound to target in 15-20 years
```

---

## 7. SESSION WORKFLOW

### First Time User
```
1. Visit http://localhost:3000
2. See LandingPage with email signup
3. Enter email → Account created in localStorage
4. Redirected to /dashboard (empty state)
5. Can navigate to /xray to upload portfolio
```

### Returning User
```
1. Visit http://localhost:3000
2. App checks localStorage for lakshya_user_data
3. If found → Skip landing, go to /dashboard
4. All previous data loads from localStorage
5. Can continue analyzing or update profile
```

### Logout (Not Implemented)
- Clearing localStorage would reset session
- Can be added via Profile page

---

## 8. RUNNING THE PROJECT

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
# Server runs on http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm start
# React runs on http://localhost:3000
```

### Docker (Optional)
```bash
docker-compose up
# Starts both backend (8000) and frontend (3000)
```

---

## 9. API CONTRACT SUMMARY

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/` | GET | - | Status message |
| `/api/v1/analyze-portfolio` | POST | PDF file | Portfolio metrics, XIRR, overlap report |
| `/api/v1/get-health-score` | POST | Profile + portfolio data | Health score (0-100) + breakdown |
| `/api/v1/project-fire` | POST | Savings, SIP, target, horizon | Success probability + timeline |

---

## 10. ERROR HANDLING

**Frontend**:
- localStorage validation on app load
- Form validation (react-hook-form)
- API error messages displayed in UI

**Backend**:
- File upload validation (PDF format)
- HTTPException with 500 status on processing errors
- CORS errors logged

---

## Summary

**Lakshya** is a multi-feature personal finance AI assistant that:
1. **Analyzes** existing portfolios for inefficiencies
2. **Assesses** overall financial health with a 0-100 score
3. **Projects** retirement timelines using Monte Carlo simulation

The **React frontend** provides a dark-themed UX with form inputs, while the **FastAPI backend** performs heavy financial calculations using specialized AI agents. Data persists in **localStorage** for a seamless user experience across sessions.

