from __future__ import annotations


class EvaligatorError(Exception):
    """Base class for every error raised by evaligator."""


class DatasetError(EvaligatorError):
    """Raised when a dataset cannot be loaded, parsed, or written."""


class ScorerError(EvaligatorError):
    """Raised when a scorer is misconfigured or fails unexpectedly."""


class UnknownScorerError(ScorerError):
    """Raised when a scorer name is not present in a registry."""


class DuplicateRegistrationError(EvaligatorError):
    """Raised when a name is registered twice in a registry."""
