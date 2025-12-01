from uuid import uuid4
from flask import Blueprint, request, jsonify, current_app
from ..domain.summarization import summarize_dialogue
from ..domain.flashcards import retrieve_flashcard

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


@bp.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"ok": True}), 200


@bp.route("/readyz", methods=["GET"])
def readyz():
    return jsonify({"ready": True}), 200


@bp.route("/summarize-dialogue", methods=["POST"])
def summarize_dialogue_route():
    if not _require_auth():
        return jsonify({"error": "Unauthorized", "requestId": request.id}), 401

    data = request.get_json(force=True) or {}
    dialogue = data.get("dialogue") or []
    csv_path = current_app.config["FLASHCARDS_CSV"]

    summary = summarize_dialogue(dialogue, csv_path)

    return jsonify({"summary": summary}), 200


@bp.route("/flashcards", methods=["GET"])
def retrieve_flashcard_route():
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

    csv_path = current_app.config["FLASHCARDS_CSV"]
    card = retrieve_flashcard(concept, csv_path)

    if not card:
        return (
            jsonify(
                {
                    "error": "NotFound",
                    "message": f"No flashcard available in CSV at {csv_path}",
                    "requestId": request.id,
                }
            ),
            404,
        )

    return jsonify({"found": True, "card": card}), 200
