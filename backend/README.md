# FinRelief AI Backend Service

Welcome to the backend service of **FinRelief AI**, the AI-Powered Debt Relief & Financial Recovery Platform.
This service is built using **FastAPI**, **SQLAlchemy 2.0 ORM**, **Pydantic v2**, and **MySQL**.

---

## Folder Structure

```text
backend/
├── app/
│   ├── ai/            # Google Gemini AI strategy prompts and generation engines
│   ├── api/           # Router groups and API endpoints
│   ├── auth/          # JWT Verification & password security handlers
│   ├── config/        # Environment config loaders & base settings using Pydantic Settings
│   ├── core/          # Log formats and core application errors/exceptions
│   ├── database/      # MySQL Async DB Session managers and engine wrappers
│   ├── models/        # SQLAlchemy 2.0 database tables ORM definitions
│   ├── repositories/  # Database access layer using Repository pattern
│   ├── routers/       # APIRouter registration hubs
│   ├── schemas/       # Request and response models (Pydantic v2 validation)
│   ├── services/      # Business logic calculation routines
│   ├── utils/         # Base string helper scripts
│   ├── __init__.py    
│   └── main.py        # Application runner and initialization hub
├── tests/             # Pytest configuration and unit-test scripts
├── requirements.txt   # Base package requirements
├── .env.example       # Template env file for development
├── alembic.ini        # Alembic configuration for migrations
└── README.md          # Technical documentation (this file)
```

---

## Getting Started

### 1. Requirements
Ensure you have **Python 3.10+** installed on your system.

### 2. Environment Configuration
Copy the `.env.example` file and create a `.env` file in the `backend/` directory:
```bash
cp .env.example .env
```
Fill out the variables inside `.env` including your MySQL database configuration and Google Gemini API token.

### 3. Installation
Create a Python virtual environment and install the required dependencies:
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Running the Development Server
Run the FastAPI application with Uvicorn:
```bash
uvicorn app.main:app --reload
```
The server will start at [http://127.0.0.1:8000](http://127.0.0.1:8000).
Interactive Swagger docs will be available at [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs).
