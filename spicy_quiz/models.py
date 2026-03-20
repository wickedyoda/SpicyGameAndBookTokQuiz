from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScrapedQuestion:
    prompt: str
    category: str
    source_name: str
    source_url: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "category": self.category,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "metadata": self.metadata,
        }
