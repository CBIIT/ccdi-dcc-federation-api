
# CCDI Federation API — FastAPI Server Prototype
## Childhood Cancer Data Initiative Data Coordinating Center (CCDI-DCC) Federation API 
Data Coordinating Center Childhood Cancer Data Initiative Federation API development.

- **Docs**: `/openapi.json` and Swagger UI are **served directly from `app/openapi/swagger.yaml`**, so all search URL query parameters and enum values appear as in the spec.
- **Routers**: live in `app/routers/` and accept **all query params optionally** via `request.query_params`; strict filtering logic is implemented server-side.
- Includes experimental endpoints: `/subject-diagnosis`, `/sample-diagnosis`.
- REsponses Data in JSON is taken from `app/data/`.

## Run
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs
Open http://localhost:8000/redoc