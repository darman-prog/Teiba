"""Reloj del sistema en UTC; los tests pueden inyectar uno fijo."""
from datetime import UTC, datetime


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)
