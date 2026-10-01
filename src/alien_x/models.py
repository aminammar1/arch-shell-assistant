"""Domain models: suggestion + risk. Single place for validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Risk = Literal["low", "medium", "high"]

RISK_COLORS: dict[str, str] = {"low": "green", "medium": "yellow", "high": "red"}
VALID_RISKS = frozenset(RISK_COLORS)


@dataclass(frozen=True)
class Suggestion:
    command: str = ""
    explanation: str = "No explanation given."
    risk: Risk = "medium"  # type: ignore[assignment]
    needs_root: bool = False
    question: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Suggestion:
        risk = str(data.get("risk", "medium")).strip().lower()
        if risk not in VALID_RISKS:
            risk = "medium"
        return cls(
            command=str(data.get("command", "") or "").strip(),
            explanation=str(data.get("explanation", "") or "").strip()
            or "No explanation given.",
            risk=risk,  # type: ignore[arg-type]
            needs_root=bool(data.get("needs_root", False)),
            question=str(data.get("question", "") or "").strip(),
        )

    @property
    def is_clarification(self) -> bool:
        return bool(self.question) and not self.command

    @property
    def is_refusal(self) -> bool:
        return not self.command and not self.question
