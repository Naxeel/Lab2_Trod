import os

import pytest

# CI (GitHub Actions) sets POSTGRES_HOST=postgres via workflow env.
# For local runs: start PostgreSQL on localhost:5432 with matching credentials.
os.environ.setdefault("POSTGRES_USER", "ci")
os.environ.setdefault("POSTGRES_PASSWORD", "ci")
os.environ.setdefault("POSTGRES_DB", "ci")
os.environ.setdefault("POSTGRES_HOST", "127.0.0.1")
os.environ.setdefault("POSTGRES_PORT", "5432")


def _clear_todos() -> None:
    from src import models
    from src.database import SessionLocal

    db = SessionLocal()
    try:
        db.query(models.Todo).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient

    from src.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _clean_todos_table():
    _clear_todos()
    yield
    _clear_todos()
