from uuid import uuid4
from flask import Blueprint, request, jsonify, current_app
from ..domain.summarization.cli import summarize_dialogue
from ..domain.flashcard.cli import retrieve_flashcard
from ..domain.summarization.task_manager import task_manager
import time
bp = Blueprint("v1", __name__, url_prefix="/api/v1")


def _require_auth() -> bool:
    token = current_app.config.get("APP_TOKEN")
    if not token:
        return True
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {token}"


@bp.before_app_request
def _inject_request_id() -> None:
    if not hasattr(request, "id"):
        request.id = request.headers.get("X-Request-Id") or str(uuid4())


@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True}), 200

# @bp.route("/summarize-dialogue", methods=["POST"])
# def summarize_dialogue_route():
#     print(f'Summary Pass at Time {time.time()}')
#     if not _require_auth():
#         return jsonify({"error": "Unauthorized", "requestId": request.id}), 401

#     data = request.get_json(force=True) or {}
#     dialogue = data.get("dialogue") or []
#     csv_path = current_app.config["FLASHCARDS_CSV"]

#     summary = summarize_dialogue(dialogue)

#     return jsonify({"summary": summary}), 200


@bp.route("/start-dialogue-summary", methods=["POST"])
def start_dialogue_summary():
    """Start asynchronous dialogue summarization and return task_id immediately."""
    print(f'Start Summary Task at Time {time.time()}')

    if not _require_auth():
        return jsonify({"error": "Unauthorized", "requestId": request.id}), 401

    data = request.get_json(force=True) or {}
    dialogue = data.get("dialogue") or []
    user_id = data.get("user_id", 0)

    if not dialogue:
        return (
            jsonify(
                {
                    "error": "BadRequest",
                    "message": "dialogue is required",
                    "requestId": request.id,
                }
            ),
            400,
        )

    # Get CSV paths from config
    dialogue_csv = current_app.config.get(
        "DIALOGUES_CSV", "../../data/dialogues.csv")
    flashcards_csv = current_app.config.get(
        "FLASHCARDS_CSV", "../../data/flashcards.csv")

    # Create and start the async task
    task_id = task_manager.create_task(
        dialogue=dialogue,
        user_id=user_id,
        dialogue_csv_path=dialogue_csv,
        flashcards_csv_path=flashcards_csv
    )

    return jsonify({"task_id": task_id, "requestId": request.id}), 202


@bp.route("/query-summary/<task_id>", methods=["GET"])
def query_summary(task_id: str):
    """Query the current status and progress of a summarization task."""
    print(f'Query Summary Task {task_id} at Time {time.time()}')

    if not _require_auth():
        return jsonify({"error": "Unauthorized", "requestId": request.id}), 401

    task_status = task_manager.get_task_status(task_id)

    if task_status is None:
        return (
            jsonify(
                {
                    "error": "NotFound",
                    "message": f"Task {task_id} not found",
                    "requestId": request.id,
                }
            ),
            404,
        )

    return jsonify(task_status), 200


@bp.route("/wait-summary/<task_id>", methods=["GET"])
def wait_summary(task_id: str):
    """Long-polling endpoint that waits for task completion or timeout."""
    print(f'Wait Summary Task {task_id} at Time {time.time()}')

    if not _require_auth():
        return jsonify({"error": "Unauthorized", "requestId": request.id}), 401

    # Get timeout from query parameter, default to 300 seconds (5 minutes)
    timeout = min(int(request.args.get("timeout", 300)), 600)  # Max 10 minutes

    task_status = task_manager.wait_for_completion(task_id, timeout)

    if task_status is None:
        return (
            jsonify(
                {
                    "error": "NotFound",
                    "message": f"Task {task_id} not found",
                    "requestId": request.id,
                }
            ),
            404,
        )

    return jsonify(task_status), 200


@bp.route("/flashcards", methods=["GET"])
def retrieve_flashcard_route():
    print(f'Flashcard Pass at Time {time.time()}')
    if not _require_auth():
        return jsonify({"error": "Unauthorized", "requestId": request.id}), 401

    concept = (request.args.get("concept") or "").strip()
    if not concept:
        return (
            jsonify(
                {
                    "error": "BadRequest",
                    "message": "concept query parameter is required",
                    "requestId": request.id,
                }
            ),
            400,
        )
    card = retrieve_flashcard(concept)
    if not card:
        return jsonify({
            "found": False,
            "card": None,
        }), 200

    return jsonify({
        "found": True,
        "card": card,
    }), 200
