# FinRelief AI 💰

> **The AI-Powered Debt Relief & Financial Recovery Platform**

An intelligent web application built to simplify and automate debt management and financial recovery for borrowers. FinRelief AI uses **Google Gemini** to generate personalized negotiation letters, settlement recommendations, and actionable financial insights.

---

## 📋 Tech Stack

| Layer       | Technology                          |
|------------|-------------------------------------|
| Frontend   | React.js, Recharts, Axios           |
| Backend    | FastAPI (Python), SQLAlchemy ORM    |
| Database   | SQLite                              |
| AI         | Google Gemini API                   |
| Auth       | JWT (python-jose + bcrypt)          |
| Charts     | Recharts                            |

---

## ️ Project Structure

```
FinRelief_AI/
├── .env                    # Sensitive config (NEVER commit)
├── .env.example            # Template for new developers
├── .gitignore              # Keeps secrets out of git
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── config.py       # Loads .env via pydantic-settings
│   │   ├── database.py     # SQLAlchemy engine & session
│   │   ├── models/         # User, Loan, FinancialProfile, etc.
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # AI service + financial calculations
│   │   └── utils/          # Auth helpers (JWT, hashing)
│   ├── requirements.txt
│   └── tests/
└── frontend/
    ├── package.json
    ├── public/
    ── src/
        ├── App.js          # Router
        ├── context/        # AuthContext (JWT state)
        ├── services/       # Axios API client
        ├── styles/         # Global CSS
        └── pages/          # Dashboard, Loans, Negotiation, etc.
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **Google Gemini API Key** (get one at [aistudio.google.com](https://aistudio.google.com))

### 1. Clone & Configure

```bash
git clone <your-repo-url>
cd FinRelief_AI

# Copy the example env and fill in your API key
cp .env.example .env
```

Open `.env` and update:
```
GEMINI_API_KEY=your_actual_gemini_key_here
SECRET_KEY=generate_a_long_random_string
DATABASE_URL=sqlite:///./finrelief.db
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**  
API Docs (Swagger): **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at: **http://localhost:3000**

---

##  Security Features

- **`.env` never committed** — listed in `.gitignore`
- **Passwords hashed** with bcrypt (passlib)
- **JWT tokens** for stateless authentication
- **CORS configured** for frontend-backend communication
- **Input validation** via Pydantic schemas
- **Ownership enforcement** — users can only access their own data

---

## 🤖 AI Features

### 1. Settlement Recommendations
Analyze any loan and get an AI-generated settlement strategy with:
- Recommended settlement amount (40–70% of outstanding)
- Expected savings
- Risk factors and confidence level
- Suggested repayment timeline

### 2. Negotiation Letter Generation
Select a loan and negotiation type (settlement / restructuring / waiver), and Gemini produces:
- A professional formal letter
- RBI guideline references (India)
- Clear financial hardship explanation
- Specific settlement proposal

### 3. AI Financial Insights
The dashboard's AI section provides:
- Debt stress assessment
- Personalized risk factors
- Actionable debt management tips
- Settlement readiness evaluation

---

## 📊 Database Models

| Model                  | Purpose                                      |
|-----------------------|----------------------------------------------|
| `User`                | Authentication, profile, monthly income      |
| `Loan`                | Individual loan records with full details    |
| `FinancialProfile`    | Aggregated health metrics per user           |
| `NegotiationHistory`  | AI-generated letters and their status        |
| `SettlementRecommendation` | AI settlement suggestions per loan     |

---

## 📡 API Endpoints

### Auth
| Method | Endpoint              | Description              |
|--------|----------------------|--------------------------|
| POST   | `/api/auth/register` | Create new account       |
| POST   | `/api/auth/login`    | Get JWT token            |
| GET    | `/api/auth/me`       | Current user profile     |
| PUT    | `/api/auth/me`       | Update profile           |

### Loans
| Method | Endpoint            | Description             |
|--------|-------------------|--------------------------|
| POST   | `/api/loans/`      | Add a loan              |
| GET    | `/api/loans/`      | List user's loans       |
| GET    | `/api/loans/{id}`  | Get loan details        |
| PUT    | `/api/loans/{id}`  | Update loan             |
| DELETE | `/api/loans/{id}`  | Delete loan             |

### Dashboard
| Method | Endpoint                       | Description              |
|--------|-------------------------------|--------------------------|
| GET    | `/api/dashboard/overview`     | Full dashboard data      |
| GET    | `/api/dashboard/ai-insights`  | AI-generated insights    |

### Negotiations
| Method | Endpoint                                    | Description              |
|--------|-------------------------------------------|--------------------------|
| POST   | `/api/negotiations/`                       | Generate AI letter       |
| GET    | `/api/negotiations/`                       | List negotiations        |
| PUT    | `/api/negotiations/{id}/status`            | Update status            |

### Settlements
| Method | Endpoint                                  | Description               |
|--------|-------------------------------------------|---------------------------|
| POST   | `/api/settlements/`                       | Generate settlement       |
| GET    | `/api/settlements/`                       | List recommendations      |
| POST   | `/api/settlements/{id}/accept`            | Accept recommendation     |

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

---

##  Deployment Notes

1. Set `DEBUG=False` and `CORS_ORIGINS` to your production domain in `.env`
2. Use a production WSGI server (e.g., `gunicorn` or `uvicorn --workers 4`)
3. For SQLite in production, consider migrating to PostgreSQL
4. Store `.env` securely (e.g., AWS Secrets Manager, Vercel env vars)

---

## 📜 License

MIT

---

Built with ❤️ for borrowers seeking financial freedom.
