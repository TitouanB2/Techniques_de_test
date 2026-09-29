# Plan de tests du `Triangulator`

## 1. Démarche test-first

Les tests sont organisé en 3 niveaux :

- **tests d'API** vérifie le comportement des api en fonction des données en entrée  ;
- **tests unitaires** regroupant les conversions binaires et l'algorithme de triangulation ;
- **tests d'intégration** vérifiant la communication avec le `PointSetManager` et le `Client`.

## 2. Architecture de test prévue :

- `tests/unit/test_binary.py` : conversions `PointSet` et `Triangles` ;
- `tests/unit/test_triangulation.py` : calcul géométrique ;
- `tests/unit/test_point_set_client.py` : communication avec le
	`PointSetManager` ;
- `tests/api/test_triangulator_api.py` : endpoint HTTP ;
- `tests/perf/` : mesures de performance, exclues des tests unitaires.

## 3. Tests d'API du `Triangulator`

### API-01 - Renvoyer `400` la donnée en entre est utilise un format incorect

- **Objectif du test :** vérifier qu'un `pointSetId` qui n'est pas un UUID
	valide produit une réponse `400` au format d'erreur prévu.
- **Composant mis en œuvre :** les endpoints nécessitant `pointSetId` en données d'entrée tel que `get/pointset/{pointSetId}` .
- **Type de test :** test d'API sans mock.
- **Nb test :** 1 pour chaque endpoints

### API-02 - Renvoyer `404` si le `PointSet` ou `pointSetId` n'existe pas

- **Objectif du test :** vérifier que l'API transmet une réponse `404` et un
	objet d'erreur contenant un code et un message.
- **Composant mis en œuvre :** les endpoints nécessitant `pointSetId` ou `pointSetId` en données d'entrée
- **Type de test :** test d'API avec mock.
- **Pourquoi :** le service distant doit être simulé pour être sûre que la donnée d'entrée n'existe pas déjà.
- **Nb test :** 1 pour chaque endpoints sauf `POST /pointset`

### API-03 - Renvoyer `503` si le service distant est indisponible

- **Objectif du test :** vérifier que l'API renvoie `503` lorsque le
	`PointSetManager` ne peut pas être contacté.
- **Composant mis en œuvre :** endpoint Flask et gestion des erreurs réseau 
- **Type de test :** test d'API avec mock .
- **Pourquoi :** le mock permet de reproduire une indisponibilité sans dépendre
	de l'état réel.
- **Nb test :** 1 pour chaque endpoints

### API-04 - Demander une triangulation avec un identifiant valide

- **Objectif du test :** vérifier que `GET /triangulation/{pointSetId}` récupère
	le `PointSet`, lance la triangulation et renvoie une réponse `200` avec le
	type `application/octet-stream`.
- **Composant mis en œuvre :** endpoint Flask du `Triangulator` . 
- **Type de test :** test d'API du `Triangulator`.
- **Nb test :** 1 pour l'endpoint `GET /triangulation/{pointSetId}`

### API-05 - Renvoyer `500` en cas d'échec de triangulation

- **Objectif du test :** le test vérifie à partir d'un cas provoquant l'erreur de l'algorithme que l'algorithme envoie bien une erreur `500` à l'API 
- **Composant mis en œuvre :** endpoint Flask du `Triangulator`
- **Type de test :** test d'API de l'algorithme de triangulation.
- **Nb test :** 1 pour l'endpoint `GET /triangulation/{pointSetId}`
 
### API-06 - Vérifier le format binaire de la réponse de la triangulation 

- **Objectif du test :** vérifier que le corps de la réponse `200` peut être
	décodé comme une structure `Triangles` valide.
- **Composant mis en œuvre :** endpoint `GET /triangulation/{pointSetId}`
- **Type de test :** test d'API du `Triangulator`
- **Nb test :** 1 pour l'endpoint `GET /triangulation/{pointSetId}`

### API-07 - Vérifier la création d'un PointSetID

- **Objectif du test :** vérifier que le corps de la réponse est `201` et qu'il renvoie bien un PointSetID au format UUID  .
- **Composant mis en œuvre :** endpoint `POST /pointset`
- **Type de test :** test d'API `PointSetManager`
- **Nb test :** 1 pour l'endpoint `POST /pointset`

## 4. Tests unitaires du format binaire

### TU-BIN-01 - Encoder un ensemble de points valide

- **Objectif du test :** vérifier qu'un ensemble de points est correctement
	transformé en représentation binaire : nombre de points, puis coordonnées
	`X` et `Y` sous forme de `float`.
- **Composant mis en œuvre :** encodeur de `PointSet` - méthode `encode_point_set()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** l'encodeur ne dépend d'aucun composant externe 

### TU-BIN-02 - Décoder un ensemble de points valide

- **Objectif du test :** vérifier qu'une représentation binaire valide est
	reconvertie en une liste de points identique aux valeurs d'origine.
- **Composant mis en œuvre :** décodeur de `PointSet` - méthode `decode_point_set()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** le décodage est une fonction déterministe qui doit être
	vérifiée indépendamment du réseau et de l'API.

### TU-BIN-03 - Gérer un ensemble de points vide

- **Objectif du test :** vérifier le comportement pour un `PointSet` contenant
	zéro point, si ce cas est accepté par le contrat de l'application.
- **Composant mis en œuvre :** validation et décodage de `PointSet` - méthodes `validate_point_set()` et `decode_point_set()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** ce cas limite permet de préciser le contrat et d'éviter un
	traitement implicite ou une erreur d'indexation.

### TU-BIN-04 - Rejeter un `PointSet` tronqué

- **Objectif du test :** vérifier qu'une donnée dont la taille ne correspond pas
	au nombre de points déclaré est rejetée proprement.
- **Composant mis en œuvre :** validateur/décodeur de `PointSet` - méthodes `validate_point_set()` et `decode_point_set()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** la donnée est locale et le défaTU doit être détecté avant tout
	appel au `PointSetManager` ou à l'algorithme.


### TU-BIN-05 - Encoder des triangles et leurs sommets

- **Objectif du test :** vérifier que la représentation `Triangles` contient
	d'abord les sommets au format `PointSet`, puis le nombre de triangles et les
	trois indices de chaque triangle.
- **Composant mis en œuvre :** encodeur de `Triangles` - méthode `encode_triangles()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** la strucutre binaire doit respecter exactement les contraintes qui lui sont associé .

### TU-BIN-06 - Décoder une triangulation valide

- **Objectif du test :** vérifier que les sommets et les indices des triangles
	sont correctement récupérés à partir d'une donnée binaire valide.
- **Composant mis en œuvre :** décodeur de `Triangles` - méthode `decode_triangles()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** le décodeur détermine si la triangulation à bien été réalisé.

### TU-BIN-07 - Rejeter un indice de sommet invalide

- **Objectif du test :** vérifier qu'un triangle faisant référence à un indice
	qui n'existe pas dans la liste des sommets est refusé.
- **Composant mis en œuvre :** validation de `Triangles` - méthode `validate_triangles()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** cette incohérence doit être détectée localement avant le
	renvoi d'une réponse incorrecte au client.

## 5. Tests unitaires de la triangulation

### TU-TRI-01 - Trianguler trois points non alignés

- **Objectif du test :** vérifier que trois points non alignés produisent un
	triangle dont les indices référencent bien les trois sommets.
- **Composant mis en œuvre :** algorithme de triangulation - méthode `triangulate()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** il s'agit du cas géométrique minimal et son résultat attendu
	est entièrement déterministe.

### TU-TRI-02 - Trianguler un ensemble de points connu

- **Objectif du test :** vérifier les triangles produits pour un ensemble de
	points dont la triangulation attendue est définie à l'avance.
- **Composant mis en œuvre :** algorithme de triangulation - méthode `triangulate()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** ce test valide la justesse du résultat sur un exemple
	représentatif, et pas seulement l'exécution de l'algorithme.

### TU-TRI-03 - Vérifier la cohérence des indices produits

- **Objectif du test :** vérifier que chaque triangle contient trois indices
	distincts et que chaque indice appartient à l'ensemble des sommetscomposant le triangle .
- **Composant mis en œuvre :** résultat de l'algorithme de triangulation - méthode `validate_triangulation_result()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** cette propriété est vérifiable quelle que soit la triangulation
	choisie lorsque plusieurs résultats géométriquement valides sont possibles.

### TU-TRI-04 - Gérer un ensemble insuffisant pour trianguler

- **Objectif du test :** vérifier le comportement avec zéro, un ou deux points.
- **Composant mis en œuvre :** algorithme de triangulation et validation de
	ses entrées - méthodes `validate_points()` et `triangulate()`.
- **Type de test :** test unitaire sans mock.
- **Pourquoi :** l'algorithme doit retourner un résultat vide ou une erreur
	métier documentée, sans produire de triangle invalide.


## 6. Tests de performance

Les tests de performance seront marqués avec `@pytest.mark.performance` afin
de pouvoir les exclure des tests habituels.

### PERF-01 - Mesurer l'encodage et le décodage

- **Objectif du test :** mesurer le temps de conversion binaire pour de petits,
	moyens et grands ensembles de points.
- **Composant mis en œuvre :** encodeurs et décodeurs `PointSet` et `Triangles` - méthodes `encode_point_set()`, `decode_point_set()`, `encode_triangles()` et `decode_triangles()`.
- **Type de test :** test de performance 

### PERF-02 - Mesurer la triangulation selon le nombre de points

- **Objectif du test :** comparer le temps de calcul pour plusieurs tailles
	d'ensembles de points.
- **Composant mis en œuvre :** algorithme de triangulation - méthode `triangulate()`.
- **Type de test :** test de performance 

## 7. Tests d'intégration avec le `PointSetManager`

### INT-CLIENT-01 - Récupérer un `PointSet` avec un identifiant valide

- **Objectif du test :** vérifier que le client du `Triangulator` effecute une
	requête `GET` vers `/pointset/{pointSetId}` et décode correctement la réponse.
- **Composant mis en œuvre :** client HTTP du `Triangulator` - méthode `fetch_point_set()`.
- **Type de test :** test d'intégration avec mock du service HTTP.
- **Pourquoi :** le `PointSetManager` est un service externe ; le mock permet de
	vérifier la requête et le traitement de sa réponse sans lancer de serveur.

### INT-CLIENT-02 - Propager une réponse `404` du `PointSetManager`

- **Objectif du test :** vérifier qu'un ensemble inexistant envoie une `404` pour l'API du `Triangulator`.
- **Composant mis en œuvre :** client HTTP et gestion des erreurs - méthodes `fetch_point_set()` et `map_http_error()`.
- **Type de test :** test d'intégration avec mock HTTP.

### INT-CLIENT-03 - Gérer l'indisponibilité du `PointSetManager`

- **Objectif du test :** vérifier qu'une erreur réseau, un délai dépassé ou une
	réponse indisponible est convertie en erreur de service `503`.
- **Composant mis en œuvre :** client HTTP du `Triangulator` - méthode `fetch_point_set()`.
- **Type de test :** test d'intégration avec mock du service HTTP.
- **Pourquoi :** ces conditions sont difficiles à provoquer de façon fiable avec
	un véritable service ; le mock permet de les simuler de manière déterministe.

