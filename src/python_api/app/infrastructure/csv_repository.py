from __future__ import annotations

import csv
from typing import List, Dict, Optional

_flashcards_cache: Optional[List[Dict[str, str]]] = None
_flashcards_cache_path: Optional[str] = None


def load_flashcards_from_csv(path: str) -> List[Dict[str, str]]:
    """
    Load flashcards from a CSV file.

    Expected headers: concept, question, answer

    This function caches the result in memory per-path for the lifetime of
    the process. If needed later, you can add TTL or invalidation.
    """
    global _flashcards_cache, _flashcards_cache_path

    if _flashcards_cache is not None and _flashcards_cache_path == path:
        return _flashcards_cache

    rows: List[Dict[str, str]] = []

    try:
        with open(path, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip completely empty rows
                if not any(row.values()):
                    continue

                # Normalize keys we care about; keep extras if present
                normalized: Dict[str, str] = {
                    "concept": row.get("concept", "") or "",
                    "question": row.get("question", "") or "",
                    "answer": row.get("answer", "") or "",
                }
                rows.append(normalized)
    except FileNotFoundError:
        # If the file doesn't exist, behave as "no flashcards"
        rows = []

    _flashcards_cache = rows
    _flashcards_cache_path = path
    return rows
