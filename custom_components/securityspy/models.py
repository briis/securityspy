"""The SecuritySpy integration models."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class SecSpyRequiredKeysMixin:
    """Mixin for required keys."""

    trigger_field: str | None = None
    device_type: str | None = None
