"""Fixtures communes aux tests du Triangulator."""

import pytest


@pytest.fixture
def client():
    """Construit un client Flask configuré pour les tests."""
    from triangulator.api import create_app

    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()
