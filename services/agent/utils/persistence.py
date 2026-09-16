from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class CheckpointStore(Protocol):
    async def get(self, thread_id: str) -> dict[str, Any] | None: ...
    async def put(self, thread_id: str, state: Mapping[str, Any]) -> None: ...
    async def claim_event(self, event_id: str) -> bool: ...


class InMemoryCheckpointStore:
    def __init__(self) -> None:
        self._states: dict[str, dict[str, Any]] = {}
        self._events: set[str] = set()

    async def get(self, thread_id: str) -> dict[str, Any] | None:
        state = self._states.get(thread_id)
        return dict(state) if state is not None else None

    async def put(self, thread_id: str, state: Mapping[str, Any]) -> None:
        self._states[thread_id] = dict(state)

    async def claim_event(self, event_id: str) -> bool:
        if event_id in self._events:
            return False
        self._events.add(event_id)
        return True


async def create_postgres_checkpointer(database_url: str) -> Any:
    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        from psycopg_pool import AsyncConnectionPool
    except ImportError as error:
        raise RuntimeError("Install langgraph-checkpoint-postgres and psycopg-pool for Postgres checkpoints") from error
    pool = AsyncConnectionPool(database_url, open=False)
    await pool.open()
    saver = AsyncPostgresSaver(pool)
    await saver.setup()
    return saver