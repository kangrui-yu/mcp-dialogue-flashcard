import os
import json
import time
import pandas as pd
from pandas.errors import EmptyDataError
from typing import Callable, Optional

from .extraction import MultiAgentLatentExtractor
from .generation import FlashCardGenerator
from .task_manager import TaskStage


def _load_or_empty(path: str, columns: list[str]) -> pd.DataFrame:
    """
    Load a CSV if it has content, otherwise return an empty DataFrame
    with the given columns.
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        # File doesn't exist or is completely empty -> start fresh
        return pd.DataFrame(columns=columns)

    try:
        return pd.read_csv(path)
    except EmptyDataError:
        # File exists but has no columns/rows
        return pd.DataFrame(columns=columns)


def summarize_dialogue(
    dialogue,
    user_id=0,
    dialogue_csv_path="../../data/dialogues.csv",
    flashcards_csv_path="../../data/flashcards.csv",
):
    """
    Synchronous dialogue summarization (legacy function).

    This function is kept for backward compatibility.
    For new async implementations, use summarize_dialogue_async.
    """
    return summarize_dialogue_async(
        dialogue, user_id, dialogue_csv_path, flashcards_csv_path
    )


def summarize_dialogue_async(
    dialogue,
    user_id=0,
    dialogue_csv_path="../../data/dialogues.csv",
    flashcards_csv_path="../../data/flashcards.csv",
    progress_callback: Optional[Callable[[TaskStage, str], None]] = None,
):
    """
    Asynchronous dialogue summarization with progress tracking.

    Args:
        dialogue: List of dialogue turns with role and message
        user_id: User identifier
        dialogue_csv_path: Path to dialogue CSV file
        flashcards_csv_path: Path to flashcards CSV file
        progress_callback: Optional callback to report progress updates

    Returns:
        Extracted latent concept as string
    """
    def report_progress(stage: TaskStage, message: str = ""):
        if progress_callback:
            progress_callback(stage, message)

    report_progress(TaskStage.GENERATION, "Starting latent concept extraction")

    extractor = MultiAgentLatentExtractor()
    generator = FlashCardGenerator()

    # Modify extractor to support progress reporting
    latent = extractor.predict_with_progress(dialogue, report_progress)

    report_progress(TaskStage.FLASHCARD_GENERATION,
                    "Generating flashcard content")
    flashcard = generator.generate(latent)

    report_progress(TaskStage.SAVING_RESULTS, "Saving results to CSV files")

    # Define expected columns for new/empty files
    dialogue_columns = ["user_id", "timestamp", "dialogue", "latent"]
    flashcards_columns = ["user_id", "concept", "question", "answer"]

    # Safely load or create empty DataFrames
    dialogue_df = _load_or_empty(dialogue_csv_path, dialogue_columns)
    flashcards_df = _load_or_empty(flashcards_csv_path, flashcards_columns)

    # New dialogue entry
    new_dialogue_entry = {
        "user_id": user_id,
        "timestamp": int(time.time()),
        "dialogue": json.dumps(dialogue),
        "latent": latent,
    }
    dialogue_df = pd.concat(
        [dialogue_df, pd.DataFrame([new_dialogue_entry])],
        ignore_index=True,
    )
    dialogue_df.to_csv(dialogue_csv_path, index=False)

    # New flashcard entry
    new_flashcard_entry = {
        "user_id": user_id,
        "concept": latent,
        "question": flashcard.question,
        "answer": flashcard.answer,
    }
    flashcards_df = pd.concat(
        [flashcards_df, pd.DataFrame([new_flashcard_entry])],
        ignore_index=True,
    )
    flashcards_df.to_csv(flashcards_csv_path, index=False)

    return latent


if __name__ == "__main__":
    # Example usage
    generator = FlashCardGenerator()
    flashcards_csv_path = "flashcards.csv"
    flashcards_df = _load_or_empty(
        flashcards_csv_path, ["concept", "question", "answer"])
    concepts = [
        'maximum_likelihood',
    ]
    for concept in concepts:
        print(concept)
        flashcard = generator.generate(concept)
        new_flashcard_entry = {
            "concept": concept,
            "question": flashcard.question,
            "answer": flashcard.answer,
        }
        flashcards_df = pd.concat(
            [flashcards_df, pd.DataFrame([new_flashcard_entry])],
            ignore_index=True,
        )
    flashcards_df.to_csv(flashcards_csv_path, index=False)
    print(f"Generated flashcards for {len(concepts)} concepts.")
