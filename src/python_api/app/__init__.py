from flask import Flask
from .api.v1 import bp as v1_bp
from .config import load_config
from .logging import configure_logging


def create_app() -> Flask:
    app = Flask(__name__)
    load_config(app)
    configure_logging(app)
    app.register_blueprint(v1_bp)
    return app
