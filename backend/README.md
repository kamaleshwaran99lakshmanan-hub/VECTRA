# VECTRA Demo Backend

FastAPI backend adapted from the provided NER-LOGIX backend.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Frontend-facing additions

- `GET /api/roads/` exposes road display coordinates for Leaflet.
- `GET /api/routes/` exposes all saved demo routes.
- Existing vehicle, incident, route, simulation and WebSocket APIs are preserved.

Do not commit a virtual environment or `.env` secrets.
