from __future__ import annotations

import os
from typing import Any

import asyncpg


async def get_connection() -> asyncpg.Connection:
    dsn = os.getenv("DATABASE_URL", "postgresql://agency:agency@localhost:5432/agency")
    return await asyncpg.connect(dsn)
