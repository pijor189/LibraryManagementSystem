import pytest

from data.database_manager import DatabaseManager
from data.init_db import initialize_database


@pytest.fixture(scope="function")
def test_db():
    db = DatabaseManager(":memory:")

    initialize_database(db)

    yield db

    db.close()
