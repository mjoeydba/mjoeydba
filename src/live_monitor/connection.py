"""SQL Server connection helpers."""
from __future__ import annotations

import contextlib
import logging
from dataclasses import dataclass
from typing import Iterator

from src.common.config import SQLServerSettings

LOGGER = logging.getLogger(__name__)


@dataclass
class ConnectionResult:
    connection: any
    cursor: any


def _import_pyodbc():  # pragma: no cover - trivial wrapper
    try:
        import pyodbc  # type: ignore

        return pyodbc
    except ImportError as exc:  # pragma: no cover - platform dependent
        raise RuntimeError(
            "pyodbc is required for live SQL Server monitoring. Install it and ensure ODBC drivers are present."
        ) from exc


class SQLServerConnectionManager:
    def __init__(self, settings: SQLServerSettings):
        self._settings = settings

    def _build_connection_string(self) -> str:
        if self._settings.dsn:
            return f"DSN={self._settings.dsn};"
        if not self._settings.server:
            raise RuntimeError("SQL Server host must be configured when DSN is not used")
        parts = [
            "DRIVER={ODBC Driver 18 for SQL Server}",
            f"SERVER={self._settings.server}",
            f"DATABASE={self._settings.database}",
        ]
        if self._settings.username and self._settings.password:
            parts.append(f"UID={self._settings.username}")
            parts.append(f"PWD={self._settings.password}")
        if self._settings.encrypt:
            parts.append("Encrypt=yes")
            if self._settings.trust_server_certificate:
                parts.append("TrustServerCertificate=yes")
        return ";".join(parts)

    @contextlib.contextmanager
    def connect(self) -> Iterator[ConnectionResult]:
        pyodbc = _import_pyodbc()
        conn_str = self._build_connection_string()
        LOGGER.debug("Connecting to SQL Server", extra={"conn_str": conn_str})
        connection = pyodbc.connect(conn_str, timeout=5)
        cursor = connection.cursor()
        try:
            yield ConnectionResult(connection=connection, cursor=cursor)
        finally:
            with contextlib.suppress(Exception):
                cursor.close()
            with contextlib.suppress(Exception):
                connection.close()


__all__ = ["SQLServerConnectionManager", "ConnectionResult"]
