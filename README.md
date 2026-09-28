# FitBuddy – AI Fitness Plan Generator

FitBuddy is an AI-powered fitness planning application built with:

- FastAPI
- Jinja2
- SQLite
- SQLAlchemy
- Pydantic
- Google Gemini
- HTML
- CSS
- JavaScript

The application generates a personalized 7-day workout plan, provides nutrition/recovery guidance, and allows users to submit feedback to update their plan.

---

# Setup and Run

From PowerShell in the project root, create the virtual environment and install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the app with mock AI enabled for local testing:

```powershell
$env:MOCK_AI = "true"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --reload-dir app --reload-dir templates --reload-dir static --port 8001
```

Open http://127.0.0.1:8001. The explicit reload directories keep Uvicorn from watching the virtual environment. If port `8001` is already in use, choose another port with `--port`.

---

# Project Structure

```text
fitbuddy/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── database_service.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   └── main.py
│
├── templates/
│   ├── index.html
│   ├── result.html
│   ├── all_users.html
│   └── error.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── data/
│
├── tests/
│   └── test_app.py
│
├── .vscode/
│   ├── settings.json
│   └── extensions.json
│
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md