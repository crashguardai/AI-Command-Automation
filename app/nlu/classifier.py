"""
Intent classification using scikit-learn (TF-IDF + linear model).

Why this stack (interview-friendly):
- **TF-IDF** turns text into sparse vectors highlighting discriminative words
  ("delete", "copy", "kill") vs generic words ("the", "file").
- **LogisticRegression** (multinomial) gives calibrated probabilities per intent,
  which we use for confidence and fallback when uncertain.

Alternatives: Rasa DIET, fine-tuned transformers (heavier), or pure rules (fast
but brittle). This hybrid is lightweight and easy to extend with more examples.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.nlu.intents import training_pairs


@dataclass
class IntentPrediction:
    """Single intent classification result."""

    intent: str
    confidence: float
    probabilities: Dict[str, float]


class IntentClassifier:
    """Train-on-init classifier wrapping a sklearn Pipeline."""

    def __init__(self) -> None:
        pairs = training_pairs()
        texts = [p[0] for p in pairs]
        labels = [p[1] for p in pairs]

        self._pipeline: Pipeline = Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        min_df=1,
                        lowercase=True,
                    ),
                ),
                (
                    "clf",
                    # sklearn>=1.5: multiclass handling is automatic; lbfgs supports multinomial loss.
                    LogisticRegression(max_iter=2000, solver="lbfgs"),
                ),
            ]
        )
        self._pipeline.fit(texts, labels)
        self._classes: List[str] = list(self._pipeline.named_steps["clf"].classes_)

    def predict_proba(self, text: str) -> Dict[str, float]:
        """Return intent -> probability for all known classes."""
        proba = self._pipeline.predict_proba([text])[0]
        return {self._classes[i]: float(proba[i]) for i in range(len(self._classes))}

    def predict(self, text: str) -> IntentPrediction:
        """Best intent and full probability distribution."""
        probs = self.predict_proba(text)
        best = max(probs.items(), key=lambda kv: kv[1])
        return IntentPrediction(intent=best[0], confidence=best[1], probabilities=probs)


# Lazy singleton so import time stays fast in tests.
_classifier: Optional[IntentClassifier] = None


def get_classifier() -> IntentClassifier:
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier
