import os
from flask import Flask


def load_config(app: Flask) -> None:
    base_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", ".."))
    default_flashcards_csv = os.path.join(base_dir, "data", "flashcards.csv")
    default_dialogues_csv = os.path.join(base_dir, "data", "dialogues.csv")

    app.config["APP_HOST"] = os.getenv("APP_HOST", "127.0.0.1")
    app.config["APP_PORT"] = int(os.getenv("APP_PORT", "8081"))
    app.config["APP_TOKEN"] = os.getenv("APP_TOKEN")  # optional
    app.config["FLASHCARDS_CSV"] = os.getenv(
        "FLASHCARDS_CSV", default_flashcards_csv)
    app.config["DIALOGUES_CSV"] = os.getenv(
        "DIALOGUES_CSV", default_dialogues_csv)
