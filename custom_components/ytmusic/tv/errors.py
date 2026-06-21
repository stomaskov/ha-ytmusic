"""Typed errors for the TV backend."""

from __future__ import annotations


class TvAuthError(Exception):
    """Auth rejected (401/403, or token refresh failed) — triggers reauth."""


class TvTransientError(Exception):
    """Transient server/network error — HA should retry."""


class TvFormatError(Exception):
    """Response was structurally unexpected — YouTube likely changed the TV format."""
