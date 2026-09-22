"""Shared error type for the pipeline. Layer 2/3 raise this; Layer 0 renders it."""
from __future__ import annotations


class JobFailed(Exception):
    """A deterministic, user-explicable pipeline failure."""

    def __init__(self, stage: str, kind: str, message: str):
        super().__init__(message)
        self.stage = stage
        self.kind = kind
        self.message = message

    def to_dict(self) -> dict:
        return {"stage": self.stage, "type": self.kind, "message": self.message}
