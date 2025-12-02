from __future__ import annotations
from typing import Optional, Dict
import pandas as pd


class FlashCard:
    def __init__(self, concept, question, answer):
        self.concept = concept
        self.question = question
        self.answer = answer


def retrieve_flashcard(concept: str, flashcards_csv_path="../../data/flashcards.csv",):
    flashcards_df = pd.read_csv(flashcards_csv_path)
    card_row = flashcards_df[flashcards_df["concept"] == concept]
    if not card_row.empty:
        row = card_row.iloc[0]
        return {
            "concept": row["concept"],
            "question": row["question"],
            "answer": row["answer"],
        }
    return None
