import uuid
from typing import Dict

import connexion
import sentry_sdk
from flask import request
from sentry_sdk.integrations.flask import FlaskIntegration

from src.config import VIZ_SENTRY_DSN
from src.encoder import JSONEncoder


def config_app(app: connexion, config: Dict = None) -> None:
    # load default configuration
    app.config.from_object("src.config")

    # load app specified configuration if need
    if config is not None and isinstance(config, dict):
        app.config.update(config)


def create_connexion_app(config: Dict = None) -> connexion.App:
    connexion_app = connexion.App(__name__, specification_dir="./swagger/")
    app = connexion_app.app
    app.json_encoder = JSONEncoder
    config_app(app, config)

    sentry_sdk.init(dsn=VIZ_SENTRY_DSN, integrations=[FlaskIntegration()])

    connexion_app.add_api("swagger.yaml", arguments={"title": "Ymir-viz API"})

    @app.before_request
    def init_request() -> None:
        request_id = request.headers.get("request_id", str(uuid.uuid1()))
        setattr(request.headers, "request_id", request_id)

    # to do, add uniform error handler for all API

    # For test server
    @app.route("/ping")
    def ping() -> str:
        return "pong"

    return connexion_app
