"""
NLU pipeline: classifier + rule overrides + entity extraction.

Rule overrides: if the statistical model is weak, keyword rules can still
classify obvious phrases (improves robustness for interviews and demos).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.config import settings
from app.nlu.classifier import IntentPrediction, get_classifier
from app.nlu.entity_extractor import ExtractedEntities, entities_to_dict, extract_entities
from app.nlu import intents as L


@dataclass
class NLUResult:
    """Complete NLU output."""

    intent: str
    confidence: float
    entities: ExtractedEntities
    probabilities: Dict[str, float]
    fallback_reason: Optional[str] = None


def _rule_based_intent(text: str) -> Optional[str]:
    """High-precision keyword routing before trusting the model."""
    t = text.lower().strip()
    # Specific tools first (avoid swallowing generic verbs).
    # Bare shell habits (power users)
    if re.match(r"^ls(\s+[-a-z0-9./~]+)?\s*$", t) or t in ("dir", "dir ."):
        return L.INTENT_FILE_LIST
    if t in ("pwd", "cwd"):
        return L.INTENT_NAV_PWD
    if re.match(r"^ps(\s+[-a-z]+)?\s*$", t) or t == "tasklist":
        return L.INTENT_PROC_LIST
    if re.search(r"\bping\s+\S+", t):
        return L.INTENT_NET_PING
    if re.search(
        r"\b(printenv|environment variables?|show\s+env|list\s+env)\b", t
    ) or (re.search(r"\b(path|home)\b", t) and re.search(r"\b(show|print|echo|what)\b", t)):
        return L.INTENT_ENV_SHOW
    if re.search(
        r"\b(mkdir|md\b|make\s+directory|create\s+(?:a\s+)?folder)\b", t
    ):
        return L.INTENT_FILE_MKDIR
    if re.search(r"\b(grep|ripgrep|\brg\b)\b", t):
        return L.INTENT_SEARCH_GREP
    if re.search(r"\b(find|locate)\b", t) and (
        re.search(r"\b(files?|named?|pattern|all\s+\w+\s+files)\b", t)
        or "*" in t
        or re.search(r"find\s+\.", t)
        or re.search(r"\blocate\s+\S+", t)
    ):
        return L.INTENT_FIND_FILES
    # Use files? / folders? so phrases like "list all files" match (not only "file").
    if re.search(r"\b(rm|delete|remove|erase|unlink)\b", t) and re.search(
        r"(\bfiles?\b|\.|\/|\\)"
    ):
        return L.INTENT_FILE_DELETE
    if re.search(r"\b(copy|cp|duplicate)\b", t):
        return L.INTENT_FILE_COPY
    if re.search(r"\b(move|mv|rename|relocate)\b", t):
        return L.INTENT_FILE_MOVE
    if re.search(r"\b(list|ls|dir|show)\b", t) and re.search(
        r"\b(files?|folders?|directories?|contents?|folder|directory|here)\b", t
    ):
        return L.INTENT_FILE_LIST
    if re.search(r"\b(list|show)\s+all\s+files\b", t) or re.search(
        r"\blist\s+(everything|every file)\b", t
    ):
        return L.INTENT_FILE_LIST
    if re.search(r"\b(cat|read|display|show)\s+.*\b(files?|\.)\b", t) or re.search(
        r"\bread\s+files?\b", t
    ):
        return L.INTENT_FILE_READ
    if re.search(r"\b(cd|chdir|go to folder|navigate to)\b", t):
        return L.INTENT_NAV_CD
    if re.search(r"\b(pwd|working directory|current path|where am i)\b", t):
        return L.INTENT_NAV_PWD
    if re.search(r"\b(ps|processes|running programs|tasklist|running tasks)\b", t):
        return L.INTENT_PROC_LIST
    if re.search(r"\b(kill|terminate)\b.*\b(process|pid)\b", t) or re.search(
        r"\bkill\s+\d+", t
    ):
        return L.INTENT_PROC_KILL
    if re.search(r"\b(disk|memory|uname|uptime|system info|df|free)\b", t):
        return L.INTENT_SYSTEM_INFO
    if re.search(r"\b(help|what can you)\b", t):
        return L.INTENT_HELP
    return None


def interpret(text: str) -> NLUResult:
    """
    Run intent classification and entity extraction.

    If confidence is below threshold or intent is *unknown*, set fallback_reason.
    """
    text = (text or "").strip()
    if not text:
        return NLUResult(
            intent=L.INTENT_UNKNOWN,
            confidence=0.0,
            entities=ExtractedEntities(),
            probabilities={},
            fallback_reason="empty_input",
        )

    clf = get_classifier()
    pred: IntentPrediction = clf.predict(text)

    rule = _rule_based_intent(text)
    intent = pred.intent
    confidence = pred.confidence

    # Prefer rule when model is uncertain or unknown; align intent with rule when it fires.
    if rule is not None:
        if confidence < settings.intent_confidence_threshold + 0.15 or intent == L.INTENT_UNKNOWN:
            intent = rule
        # When rules and model agree, still lift score so short commands (e.g. "ls") look confident.
        if intent == rule:
            confidence = max(confidence, 0.92)

    entities = extract_entities(text)

    fallback_reason: Optional[str] = None
    if confidence < settings.intent_confidence_threshold:
        fallback_reason = "low_confidence"
        intent = L.INTENT_UNKNOWN
    elif intent == L.INTENT_UNKNOWN:
        fallback_reason = "unknown_intent"

    return NLUResult(
        intent=intent,
        confidence=confidence,
        entities=entities,
        probabilities=pred.probabilities,
        fallback_reason=fallback_reason,
    )


def nlu_result_to_dict(r: NLUResult) -> Dict[str, Any]:
    return {
        "intent": r.intent,
        "confidence": r.confidence,
        "entities": entities_to_dict(r.entities),
        "probabilities": r.probabilities,
        "fallback_reason": r.fallback_reason,
    }
