"""Mesures de performance des conversions binaires et de la triangulation."""

from collections.abc import Callable
from math import cos, pi, sin
from statistics import median
from time import perf_counter

import pytest


def _measure_seconds(operation: Callable[[], object]) -> float:
    """Mesure trois exécutions et retourne leur durée médiane en secondes."""
    durations = []

    for _ in range(3):
        start_time = perf_counter()
        operation()
        durations.append(perf_counter() - start_time)

    return median(durations)


@pytest.mark.performance
@pytest.mark.parametrize(
    ("size_name", "point_count"),
    [
        pytest.param("small", 10, id="small-10-points"),
        pytest.param("medium", 1_000, id="medium-1000-points"),
        pytest.param("large", 10_000, id="large-10000-points"),
    ],
)
def test_binary_conversion_performance(size_name, point_count):
    """Mesure les conversions PointSet ET Triangles pour plusieurs tailles."""
    from triangulator.binary import (
        decode_point_set,
        decode_triangles,
        encode_point_set,
        encode_triangles,
    )

    # Des coordonnées simples et distinctes rendent les données reproductibles grace au modulo 101.
    points = [(float(index), float(index % 101)) for index in range(point_count)]

    # Construire une suite de triangles valides pour mesurer aussi leur format.
    triangles = [
        (0, index, index + 1)
        for index in range(1, point_count - 1)
    ]

    point_set_data = encode_point_set(points)
    triangles_data = encode_triangles(points, triangles)

    # Vérifier une fois les résultats avant de chronométrer les opérations.
    assert decode_point_set(point_set_data) == points
    assert decode_triangles(triangles_data) == (points, triangles)

    # Mesurer séparément chaque conversion pour comparer leurs coûts.
    encode_point_set_seconds = _measure_seconds(lambda: encode_point_set(points))
    decode_point_set_seconds = _measure_seconds(
        lambda: decode_point_set(point_set_data)
    )
    encode_triangles_seconds = _measure_seconds(
        lambda: encode_triangles(points, triangles)
    )
    decode_triangles_seconds = _measure_seconds(
        lambda: decode_triangles(triangles_data)
    )

    print(
        f"{size_name} ({point_count} points): "
        f"encode PointSet={encode_point_set_seconds:.6f}s, "
        f"decode PointSet={decode_point_set_seconds:.6f}s, "
        f"encode Triangles={encode_triangles_seconds:.6f}s, "
        f"decode Triangles={decode_triangles_seconds:.6f}s"
    )


@pytest.mark.performance
@pytest.mark.parametrize(
    ("size_name", "point_count"),
    [
        pytest.param("small", 10, id="small-10-points"),
        pytest.param("medium", 50, id="medium-50-points"),
        pytest.param("large", 100, id="large-100-points"),
    ],
)
def test_triangulation_performance(size_name, point_count):
    """Mesure la durée de triangulation pour des ensembles de tailles variées."""
    from triangulator.triangulation import triangulate

    # Les points sont répartis sur un cercle avec un rayon variant légèrement pour éviter la colinéarité (que les points soient alignés).
    points = []
    for index in range(point_count):
        angle = 2 * pi * index / point_count
        radius = 1.0 + 0.1 * (index % 5)
        points.append((radius * cos(angle), radius * sin(angle)))

    # Vérifier que l'algorithme produit un résultat.
    triangles = triangulate(points)
    assert triangles

    # Renvoie la durée médiane de trois exécutions.
    duration = _measure_seconds(lambda: triangulate(points))

    print(
        f"{size_name} ({point_count} points): "
        f"triangulation={duration:.6f}s, triangles={len(triangles)}"
    )
