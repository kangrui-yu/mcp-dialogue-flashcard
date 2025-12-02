import atexit
from flask import Flask
from .api.v1 import bp as v1_bp
from .config import load_config
from .logging import configure_logging
from .domain.summarization.task_manager import task_manager


def create_app() -> Flask:
    app = Flask(__name__)
    load_config(app)
    configure_logging(app)
    app.register_blueprint(v1_bp)

    @atexit.register
    def cleanup_task_manager():
        try:
            task_manager.shutdown()
        except Exception:
            pass

    return app
