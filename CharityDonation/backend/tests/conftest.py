import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.deps import get_db
from app.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/charity_donation_test",
)

# Guard: the engine fixture calls Base.metadata.drop_all() at teardown, so it
# MUST only ever point at a disposable test database. Refuse to run against a
# URL that doesn't clearly name one — this prevents pointing the suite at a real
# database and wiping it. Override intentionally by including "test" in the name.
if "test" not in TEST_DATABASE_URL.rsplit("/", 1)[-1].lower():
    raise RuntimeError(
        "TEST_DATABASE_URL must point at a database whose name contains 'test' "
        "(tests DROP ALL TABLES on teardown). Refusing to run against "
        f"{TEST_DATABASE_URL.rsplit('/', 1)[-1]!r} to avoid data loss."
    )


@pytest.fixture(scope="session")
def engine():
    test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    with test_engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")

    yield test_engine

    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def db(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
