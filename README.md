# Windsurf Performance Parameter Visualizer

Hybrid web + desktop application for windsurf analytics.

## Monorepo Structure

- `backend/` Django + DRF API for CSV upload, analytics, auth, PDF reporting, and upload history.
- `web/` React + Chart.js client consuming backend APIs.
- `desktop/` PyQt5 + Matplotlib desktop client consuming the same backend APIs.
- `sample_windsurf_data.csv` Sample dataset for demo and testing.

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API root: `http://127.0.0.1:8000/api/`

### Web Frontend

```bash
cd web
npm install
npm start
```

Web app: `http://127.0.0.1:3000`

### Desktop Frontend

```bash
cd desktop
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Authentication

- Backend provides token login endpoint: `POST /api/auth/token/`
- Both web and desktop clients store the token in-memory/session and attach `Authorization: Token <token>` header.

## Required Feature Coverage

- CSV upload from web and desktop apps.
- Analytics summary endpoint.
- Line/bar/pie visualizations in both frontends.
- Last 5 uploads persisted in SQLite.
- PDF report endpoint with summary + generated chart images.
- Basic authentication for protected endpoints.

