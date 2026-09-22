# Résumé des rôles et des composants

## `PointSetManager`

Le `PointSetManager` enregistre et récupère les ensembles de points via l'API
décrite dans [`api/point_set_manager.yml`](api/point_set_manager.yml).

## `Triangulator`

Le `Triangulator` calcule la triangulation d'un ensemble de points récupéré
auprès du `PointSetManager`, via l'API décrite dans
[`api/triangulator.yml`](api/triangulator.yml).

## `PointSet`

Un `PointSet` est un ensemble de points fourni par le client et utilisé pour
réaliser la triangulation.

### Format binaire de `PointSet`

- Les 4 premiers octets définissent le nombre de points de l'ensemble.
- Les octets suivants représentent les points.
- Chaque point occupe 8 octets :
    - les 4 premiers octets représentent la coordonnée `X` sous forme de `float` ;
    - les 4 octets suivants représentent la coordonnée `Y` sous forme de `float`.

## `Triangles`

`Triangles` représente un ensemble de triangles dérivé de la structure
`PointSet`.

### Format binaire de `Triangles`

La représentation se compose de deux parties :

1. **Les sommets** : ils suivent le même format binaire qu'un `PointSet`.
2. **Les triangles** :
     - 4 octets définissent le nombre de triangles ;
     - chaque triangle occupe 12 octets ;
     - ces 12 octets contiennent trois `unsigned long` de 4 octets ;
     - chaque valeur référence l'indice d'un sommet dans le `PointSet`.

## Workflow général

Le workflow typique est le suivant:
- Le `Client` envoie un `PointSet` au `PointSetManager` pour enregistrement
- Le `PointSetManager` enregistre le `PointSet` et renvoie un `PointSetID` au `Client`
- Le `Client` demande une triangulation au `Triangulator` en lui passant un `PointSetID`
- Le `Triangulator` récupère le `PointSet` auprès du `PointSetManager` en lui passant le `PointSetID`
- Le `Triangulator` réalise la triangulation
- Le `Triangulator` répond au `Client` avec les `Triangles` issus de la triangulation