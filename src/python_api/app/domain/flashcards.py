from __future__ import annotations

from typing import Optional, Dict
from ..infrastructure.csv_repository import load_flashcards_from_csv


def retrieve_flashcard(concept: str, csv_path: str) -> Optional[Dict[str, str]]:
    """
    Retrieve a flashcard.

    Current behavior (for now):
    - Load flashcards from the given CSV path.
    - Ignore the `concept` argument.
    - Always return the first entry in the CSV, if any.

    If there are no rows in the CSV, returns None.
    """
    flashcards = load_flashcards_from_csv(csv_path)
    if not flashcards:
        return None

    first = flashcards[0]

    # Ensure the expected keys exist
    return {
        "concept": first.get("concept", ""),
        "question": first.get("question", ""),
        "answer": first.get("answer", ""),
    }
