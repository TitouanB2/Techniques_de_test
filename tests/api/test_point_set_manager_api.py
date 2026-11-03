"""Tests API du PointSetManager prévus par le plan de tests."""

from uuid import UUID


def test_create_point_set_returns_valid_point_set_id():
    """Vérifie qu'un PointSet valide reçoit un identifiant UUID."""
    from point_set_manager.api import create_app

    response = (
        create_app()
        .test_client()
        .post(
            "/pointset",
            data=bytes.fromhex(
                "0300000000000000000000000000803f00000000000000000000803f"
            ),
            content_type="application/octet-stream",
        )
    )

    assert response.status_code == 201
    UUID(response.json["pointSetId"])
