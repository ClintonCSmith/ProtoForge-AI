"""FastAPI entrypoint — replace with the engagement's vertical slice.
Synthetic data only: this stub echoes requests without touching real data."""
from fastapi import FastAPI

app = FastAPI(title="{{CLIENT_SLUG}} prototype", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "vendor": "IIT Aethelgard", "synthetic_data_only": True}
