"""Tests unitaires du client du PointSetManager."""

from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest


def test_fetch_point_set_requests_binary_representation():
    """Récupère et décode le PointSet binaire associé à son identifiant."""
    from triangulator.point_set_client import fetch_point_set

    # Identifiant utilisé pour construire l'URL de récupération.
    point_set_id = "123e4567-e89b-12d3-a456-426614174000"
    # Contenu binaire simulé ; le décodeur est remplacé plus bas dans ce test.
    payload = b"encoded-point-set"
    # Valeur que le décodeur simulé doit renvoyer au client.
    points = [(1.25, -2.5)]

    # Simule la réponse HTTP et son gestionnaire de contexte (with urlopen(...)).
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = payload

    # Remplace le réseau et le décodeur pour vérifier le comportement du client seul.
    with (
        patch("urllib.request.urlopen", return_value=response) as urlopen,
        patch(
            "triangulator.point_set_client.decode_point_set",
            return_value=points,
        ) as decode_point_set,
    ):
        result = fetch_point_set(point_set_id, "http://point-set-manager")

    # Vérifie que le résultat est exactement la liste de points décodée.
    assert result == points
    decode_point_set.assert_called_once_with(payload)
    request = urlopen.call_args.args[0]
    # Vérifie que l'URL construite correspond à l'identifiant fourni.
    assert request.full_url == f"http://point-set-manager/pointset/{point_set_id}"


def test_fetch_point_set_maps_not_found_response():
    """Traduit la réponse HTTP 404 en erreur métier dédiée."""
    from triangulator.point_set_client import PointSetNotFound, fetch_point_set

    error = HTTPError(
        "http://point-set-manager/pointset/missing", 404, "Not found", {}, None
    )
    # Simule une réponse HTTP 404 du serveur distant
    with patch("urllib.request.urlopen", side_effect=error), pytest.raises(
        PointSetNotFound
    ):
        fetch_point_set(
            "123e4567-e89b-12d3-a456-426614174000",
            "http://point-set-manager",
        )


def test_fetch_point_set_maps_network_failure():
    """Traduit une erreur réseau en indisponibilité du service distant."""
    from triangulator.point_set_client import (
        PointSetManagerUnavailable,
        fetch_point_set,
    )
    # Simule une erreur réseau
    with patch(
        "urllib.request.urlopen", side_effect=URLError("connection refused")
    ), pytest.raises(PointSetManagerUnavailable):
        # Vérifie que le client transforme erreur réseau en erreur métier.
        fetch_point_set(
            "123e4567-e89b-12d3-a456-426614174000",
            "http://point-set-manager",
        )


def test_fetch_point_set_maps_timeout():
    """Traduit un délai dépassé en indisponibilité du service distant."""
    from triangulator.point_set_client import (
        PointSetManagerUnavailable,
        fetch_point_set,
    )

    # Simule un délai dépassé sans attendre une vraie requête réseau.
    with patch(
        "urllib.request.urlopen",
        side_effect=TimeoutError("request timed out"),
    ), pytest.raises(PointSetManagerUnavailable):
        # Vérifie que le délai dépassé devient une erreur d'indisponibilité.
        fetch_point_set(
            "123e4567-e89b-12d3-a456-426614174000",
            "http://point-set-manager",
        )