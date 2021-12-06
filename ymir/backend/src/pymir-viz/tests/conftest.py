# -*- coding: utf-8 -*-
import pytest

from src.app import create_connexion_app

connexion_app_cache = None


def get_app():
    global connexion_app_cache
    if not connexion_app_cache:
        config = dict()
        connexion_app_cache = create_connexion_app(config)
    return connexion_app_cache


@pytest.fixture(autouse=True)
def core_app():
    connexion_app = get_app()
    app = connexion_app.app

    context = app.app_context()
    context.push()

    try:
        yield app
    finally:
        context.pop()
