"""Tests HTTP du service Triangulator."""

from unittest.mock import patch


def test_invalid_point_set_id_returns_bad_request(client):
    """Retourne 400 lorsque l'identifiant n'est pas un UUID."""
    response = client.get("/triangulation/not-a-uuid")

    assert response.status_code == 400
    assert {"code", "message"} <= response.json.keys()


def test_missing_point_set_returns_not_found(client):
    """Retourne 404 lorsque le PointSetManager ne trouve pas l'ensemble."""
    from triangulator.point_set_client import PointSetNotFound

    with patch("triangulator.api.fetch_point_set", side_effect=PointSetNotFound):
        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")

    assert response.status_code == 404
    assert {"code", "message"} <= response.json.keys()


def test_unavailable_point_set_manager_returns_service_unavailable(client):
    """Retourne 503 lorsque le PointSetManager est inaccessible."""
    from triangulator.point_set_client import PointSetManagerUnavailable

    with patch(
        "triangulator.api.fetch_point_set",
        side_effect=PointSetManagerUnavailable,
    ):
        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")

    assert response.status_code == 503
    assert {"code", "message"} <= response.json.keys()


def test_triangulation_failure_returns_internal_server_error(client):
    """Retourne 500 si l'algorithme échoue après récupération des points."""
    with (
        patch(
            "triangulator.api.fetch_point_set",
            return_value=[(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)],
        ),
        patch(
            "triangulator.api.triangulate",
            side_effect=RuntimeError("triangulation failed"),
        ),
    ):
        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")

    assert response.status_code == 500
    assert {"code", "message"} <= response.json.keys()


def test_successful_triangulation_returns_binary_triangles(client):
    """Retourne les triangles au format octet-stream pour un UUID valide."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    with patch("triangulator.api.fetch_point_set", return_value=points):
        response = client.get("/triangulation/123e4567-e89b-12d3-a456-426614174000")

    from triangulator.binary import decode_triangles

    assert response.status_code == 200
    assert response.mimetype == "application/octet-stream"
    vertices, triangles = decode_triangles(response.data)
    assert vertices == points
    assert len(triangles) == 1
    assert set(triangles[0]) == {0, 1, 2}

