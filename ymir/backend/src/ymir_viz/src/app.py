import logging
import sys
import uuid
from typing import Dict, Tuple

import connexion
import sentry_sdk
from flask import request, jsonify
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.wrappers import Response

from id_definition.error_codes import VizErrorCode
from src.config import viz_settings
from src.encoder import JSONEncoder
from src.libs.exceptions import VizException


def config_app(app: connexion, config: Dict = None) -> None:
    # load default configuration
    app.config.from_object("src.config.viz_settings")

    # load app specified configuration if need
    if config is not None and isinstance(config, dict):
        app.config.update(config)


def init_logging() -> None:
    logging_level = logging.DEBUG if viz_settings.VIZ_DEBUG_MODE else logging.INFO
    logging.basicConfig(stream=sys.stdout,
                        format='%(levelname)-8s: [%(asctime)s] %(filename)s:%(lineno)s:%(funcName)s(): %(message)s',
                        datefmt='%Y%m%d-%H:%M:%S',
                        level=logging_level)


def create_connexion_app(config: Dict = None) -> connexion.App:
    init_logging()
    connexion_app = connexion.App(__name__, specification_dir="./swagger/")
    app = connexion_app.app
    app.json_encoder = JSONEncoder
    config_app(app, config)

    sentry_sdk.init(dsn=viz_settings.VIZ_SENTRY_DSN, integrations=[FlaskIntegration()])

    connexion_app.add_api("swagger.yaml", arguments={"title": "Ymir-viz API"})

    @app.before_request
    def init_request() -> None:
        request_id = request.headers.get("request_id", str(uuid.uuid1()))
        setattr(request.headers, "request_id", request_id)

    @app.errorhandler(VizException)
    def handle_viz_exception(e: VizException) -> Tuple[Response, int]:
        resp = dict(code=e.code, message=e.message)

        return jsonify(resp), e.status_code

    @app.errorhandler(Exception)
    def handle_exception(e: Exception) -> Tuple[Response, int]:
        logging.exception(e)
        resp = dict(code=VizErrorCode.INTERNAL_ERROR, message=str(e))

        return jsonify(resp), 500

    # For test server
    @app.route("/ping")
    def ping() -> str:
        return "pong"

    return connexion_app
