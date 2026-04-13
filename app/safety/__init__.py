"""Safety: risk scoring and confirmation for dangerous commands."""

from app.safety.layer import SafetyResult, evaluate_safety

__all__ = ["evaluate_safety", "SafetyResult"]
