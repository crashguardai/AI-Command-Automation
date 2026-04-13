"""
Safety confirmation layer.

Assigns **risk levels** from intent + command text. High-risk operations require
explicit user confirmation before any execution (the API returns
`requires_confirmation` and does not run the shell by default).

Patterns like `rm -rf`, `sudo`, `format`, `shutdown` are always treated as
critical even if the intent classifier misfires.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.command_mapping.mapper import CommandMappingResult
from app.nlu import intents as L


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyResult:
    risk_level: RiskLevel
    requires_confirmation: bool
    reason: str


_CRITICAL_PATTERNS = [
    (re.compile(r"\brm\s+-\w*f", re.I), "recursive/force delete"),
    (re.compile(r"\bsudo\b", re.I), "elevated privileges"),
    (re.compile(r"\bformat\b", re.I), "disk format"),
    (re.compile(r"\bshutdown\b|\breboot\b|\bhalt\b", re.I), "power / shutdown"),
    (re.compile(r">\s*/dev/", re.I), "redirect to device"),
    (re.compile(r"\bdd\b", re.I), "dd disk operation"),
]

_HIGH_INTENTS = {
    L.INTENT_FILE_DELETE,
    L.INTENT_PROC_KILL,
}

_MEDIUM_INTENTS = {
    L.INTENT_FILE_MOVE,
    L.INTENT_SYSTEM_INFO,
}


def evaluate_safety(
    intent: str,
    mapping: CommandMappingResult,
    raw_command: Optional[str] = None,
) -> SafetyResult:
    """
    Decide if the user must confirm before execution.

    Command-line scanning catches risky flags even when intent is benign.
    """
    cmd = (mapping.command or "") + " " + (raw_command or "")
    cmd_lower = cmd.lower()

    for rx, label in _CRITICAL_PATTERNS:
        if rx.search(cmd_lower):
            return SafetyResult(
                risk_level=RiskLevel.CRITICAL,
                requires_confirmation=True,
                reason=f"Matched risky pattern: {label}",
            )

    if intent in _HIGH_INTENTS:
        return SafetyResult(
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True,
            reason="Destructive or process-termination action",
        )

    if intent in _MEDIUM_INTENTS:
        return SafetyResult(
            risk_level=RiskLevel.MEDIUM,
            requires_confirmation=False,
            reason="Potentially impactful; review command before running",
        )

    if mapping.ambiguous:
        return SafetyResult(
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            reason="No executable command mapped",
        )

    return SafetyResult(
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        reason="Routine read-only or navigation command",
    )
