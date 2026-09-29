"""Tests du format binaire des PointSet et Triangles."""

import pytest


def test_point_set_round_trip():
    """Encode puis décode un ensemble de points."""
    from triangulator.binary import decode_point_set, encode_point_set

    points = [(1.25, -2.5), (0.0, 3.75)]
    encoded = encode_point_set(points)
    #Vérifie que la taille de l'encodage correspond à la structure attendue : 4 octets pour le nombre de points, puis 8 octets par point.
    assert len(encoded) == 4 + 8 * len(points)
    # Vérifie que le décodage restitue exactement les points d'origine.
    assert decode_point_set(encoded) == points


def test_empty_point_set_round_trip():
    """Accepte la représentation d'un ensemble vide."""
    from triangulator.binary import decode_point_set, encode_point_set

    assert decode_point_set(encode_point_set([])) == []


def test_point_set_rejects_truncated_payload():
    """Rejette les données dont la taille contredit le nombre de points."""
    from triangulator.binary import decode_point_set

    # Vérifie que le décodage échoue si le nombre de points indiqué ne correspond pas à la taille réelle des données.
    with pytest.raises(ValueError):
        decode_point_set(b"\x01\x00\x00\x00" + b"\x00" * 7)


def test_triangles_round_trip():
    """Encode puis décode les sommets et les indices des triangles."""
    from triangulator.binary import decode_triangles, encode_triangles

    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangles = [(0, 1, 2)]

    encoded = encode_triangles(points, triangles)

    # Vérifie que la taille de l'encodage correspond à la structure attendue : 
    #   4 octets pour le nombre de points
    #   8 octets par point
    #   4 octets pour le nombre de triangles
    #   12 octets par triangle
    assert len(encoded) == 4 + 8 * len(points) + 4 + 12 * len(triangles)
    # Vérifie que le décodage restitue exactement les points et triangles d'origine.
    assert decode_triangles(encoded) == (points, triangles)


def test_triangles_reject_invalid_vertex_index():
    """Refuse un triangle qui référence un sommet inexistant."""
    from triangulator.binary import validate_triangles

    with pytest.raises(ValueError):
        validate_triangles([(0.0, 0.0), (1.0, 0.0)], [(0, 1, 2)])