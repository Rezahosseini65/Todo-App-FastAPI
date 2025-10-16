from fastapi.testclient import TestClient
from sqlalchemy import StaticPool

from app.main import app
from app.core.database import (
    Base, 
    sessionmaker,
    create_engine,
    get_db
)

SQLALCHEMY_DATABASE_URL = "sqlite:///memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def overrides_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = overrides_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)