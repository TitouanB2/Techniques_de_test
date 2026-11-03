"""Tests du format binaire des PointSet et Triangles."""

import pytest


def test_point_set_round_trip():
    """Encode puis décode un ensemble de points."""
    from triangulator.binary import decode_point_set, encode_point_set

    points = [(1.25, -2.5), (0.0, 3.75)]
    encoded = encode_point_set(points)
    # Vérifie la taille : 4 octets pour le nombre de points, puis 8 par point.
    assert len(encoded) == 4 + 8 * len(points)
    # Vérifie que le décodage restitue exactement les points d'origine.
    assert decode_point_set(encoded) == points


def test_encode_point_set_matches_reference_bytes():
    """Compare l'encodage d'un PointSet à des octets de référence."""
    from triangulator.binary import encode_point_set

    points = [(1.0, -2.5)]
    # Structure attendue :
    # - 1 triangle (unsigned long, 4 octets) : \x01\x00\x00\x00 -> 01000000
    # - X = 1.0 (float, 4 octets)            : \x00\x00\x80\x3f -> 0000803f
    # - Y = -2.5 (float, 4 octets)           : \x00\x00\x20\xc0 -> 000020c0
    expected_bytes = bytes.fromhex("010000000000803f000020c0")

    # Étape Séance 4 : On s'attend à ce que la fonction lève NotImplementedError
    with pytest.raises(NotImplementedError):
        assert encode_point_set(points) == expected_bytes


def test_decode_point_set_matches_reference_bytes():
    """Vérifie le décodage d'un PointSet à partir d'octets de référence."""
    from triangulator.binary import decode_point_set

    reference_bytes = bytes.fromhex("010000000000803f000020c0")
    expected_points = [(1.0, -2.5)]

    # Étape Séance 4 : On s'attend à ce que la fonction lève NotImplementedError
    with pytest.raises(NotImplementedError):
        assert decode_point_set(reference_bytes) == expected_points


def test_empty_point_set_round_trip():
    """Accepte la représentation d'un ensemble vide."""
    from triangulator.binary import decode_point_set, encode_point_set

    assert decode_point_set(encode_point_set([])) == []


def test_point_set_rejects_truncated_payload():
    """Rejette les données dont la taille contredit le nombre de points."""
    from triangulator.binary import decode_point_set

    # Le nombre de points annoncé ne correspond pas à la taille du contenu.
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


def test_encode_triangles_matches_reference_bytes():
    """Compare l'encodage des triangles à des octets de référence."""
    from triangulator.binary import encode_triangles

    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangles = [(0, 1, 2)]

    # Construction méthodique de la référence (Little-Endian) :
    expected_bytes = bytes.fromhex(
        "03000000"  # Part 1: nombre de points
        "0000000000000000"  # Point 0 : X=0.0 (00000000), Y=0.0 (00000000)
        "0000803f00000000"  # Point 1 : X=1.0 (0000803f), Y=0.0 (00000000)
        "000000000000803f"  # Point 2 : X=0.0 (00000000), Y=1.0 (0000803f)
        "01000000"  # Part 2: nombre de triangles
        "000000000100000002000000"  # Triangle 0 : indices (0, 1, 2)
    )

    assert encode_triangles(points, triangles) == expected_bytes


def test_decode_triangles_matches_reference_bytes():
    """Vérifie le décodage d'octets sans utiliser l'encodeur testé."""
    from triangulator.binary import decode_triangles

    reference_bytes = bytes.fromhex(
        "03000000"
        "0000000000000000"
        "0000803f00000000"
        "000000000000803f"
        "01000000"
        "000000000100000002000000"
    )

    assert decode_triangles(reference_bytes) == (
        [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)],
        [(0, 1, 2)],
    )


def test_triangles_reject_invalid_vertex_index():
    """Refuse un triangle qui référence un sommet inexistant."""
    from triangulator.binary import validate_triangles

    with pytest.raises(ValueError):
        validate_triangles([(0.0, 0.0), (1.0, 0.0)], [(0, 1, 2)])
