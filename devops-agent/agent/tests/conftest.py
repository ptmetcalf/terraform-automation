import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.append(str(SRC))


@pytest.fixture(scope="session", autouse=True)
def _initialize_database():
    """Ensure the SQLite schema exists for tests."""
    from app.services.database import init_database, shutdown_database

    asyncio.run(init_database())
    yield
    asyncio.run(shutdown_database())
