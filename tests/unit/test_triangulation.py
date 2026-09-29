"""Tests unitaires de l'algorithme de triangulation."""

import pytest


def test_triangulates_three_non_collinear_points():
    """Le cas minimal non dégénéré doit produire un triangle."""
    from triangulator.triangulation import triangulate

    result = triangulate([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
    
    # Vérifie que le résultat contient exactement un triangle.
    assert len(result) == 1

    # Les trois sommets du triangle doivent référencer les trois points fournis.
    assert set(result[0]) == {0, 1, 2}


def test_triangulates_square_without_gaps_or_overlaps():
    """Découpe le carré en deux triangles partageant une diagonale."""
    from triangulator.triangulation import triangulate

    points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    triangles = triangulate(points)
    normalized_triangles = tuple(
        sorted(tuple(sorted(triangle)) for triangle in triangles)
    )

    # Les deux diagonales sont valides ; l'ordre des triangles et de leurs
    # sommets ne doit donc pas influencer la comparaison.
    assert normalized_triangles in {
        ((0, 1, 2), (0, 2, 3)),
        ((0, 1, 3), (1, 2, 3)),
    }


def test_triangulation_indices_are_valid_and_distinct():
    """Chaque triangle référence trois sommets distincts de l'entrée."""
    from triangulator.triangulation import triangulate

    points = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0), (1.0, 1.0)]
    triangles = triangulate(points)

    #la liste des triangles triangulés n'est pas vide 
    assert triangles

    for triangle in triangles:
        # Chaque triangle a trois indices (sommets)
        assert len(triangle) == 3
        #chaques indices sont distincts
        assert len(set(triangle)) == 3
        # Les indices existent dans la liste des points fournis
        assert all(0 <= index < len(points) for index in triangle)


#change la valeur de points et relance le test pour chaque cas (0, 1 ou 2 points) : aucun triangle ne peut être formé.
@pytest.mark.parametrize("points", [[], [(0.0, 0.0)], [(0.0, 0.0), (1.0, 1.0)]])
def test_insufficient_points_produce_no_triangles(points):
    """Zéro, un ou deux points ne suffisent pas à former un triangle."""
    from triangulator.triangulation import triangulate

    assert triangulate(points) == []

