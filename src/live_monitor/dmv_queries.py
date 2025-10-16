"""DMV query helpers for live monitoring."""
from __future__ import annotations

from typing import Iterable, List, Mapping

from src.live_monitor.connection import SQLServerConnectionManager

WAIT_STATS_SQL = """
SELECT TOP (@limit)
    GETDATE() AS collection_time,
    wait_type,
    waiting_tasks_count,
    wait_time_ms,
    max_wait_time_ms,
    signal_wait_time_ms
FROM sys.dm_os_wait_stats
ORDER BY wait_time_ms DESC;
"""

BLOCKING_SQL = """
SELECT TOP (@limit)
    GETDATE() AS collection_time,
    session_id,
    blocking_session_id,
    wait_type,
    wait_duration_ms,
    resource_description
FROM sys.dm_exec_requests
WHERE blocking_session_id <> 0
ORDER BY wait_duration_ms DESC;
"""

SESSIONS_SQL = """
SELECT TOP (@limit)
    GETDATE() AS collection_time,
    s.session_id,
    s.login_name,
    r.status,
    r.cpu_time,
    r.logical_reads,
    r.wait_type,
    r.blocking_session_id
FROM sys.dm_exec_sessions AS s
LEFT JOIN sys.dm_exec_requests AS r ON s.session_id = r.session_id
WHERE s.is_user_process = 1
ORDER BY r.cpu_time DESC;
"""


class DMVCollector:
    def __init__(self, manager: SQLServerConnectionManager):
        self._manager = manager

    def _execute(self, sql: str, limit: int) -> List[Mapping[str, object]]:
        with self._manager.connect() as ctx:
            ctx.cursor.execute(sql, limit)
            columns = [col[0] for col in ctx.cursor.description]
            rows = ctx.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def wait_stats(self, limit: int = 25) -> List[Mapping[str, object]]:
        return self._execute(WAIT_STATS_SQL, limit)

    def blocking(self, limit: int = 25) -> List[Mapping[str, object]]:
        return self._execute(BLOCKING_SQL, limit)

    def active_sessions(self, limit: int = 50) -> List[Mapping[str, object]]:
        return self._execute(SESSIONS_SQL, limit)


__all__ = ["DMVCollector", "WAIT_STATS_SQL", "BLOCKING_SQL", "SESSIONS_SQL"]
