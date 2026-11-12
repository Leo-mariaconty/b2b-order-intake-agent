# Résultats attendus (vérité terrain)

Un fichier par email de `data/inbox/`. Ces fichiers sont écrits à la main, avant
le code : ils décrivent ce que le pipeline doit produire. Le test de bout en bout
(`tests/test_bout_en_bout.py`) compare le résultat réel à ces fichiers.

- `destination` : `import_odoo` (tout est valide) ou `exceptions` (au moins un
  contrôle en échec, la commande entière part chez un humain).
- `client` : le code client identifié, ou `null` s'il ne l'est pas.
- `exceptions_commande` : contrôles en échec sur la commande entière.
- `lignes` : pour chaque ligne, le produit reconnu (ou `null`), la quantité lue
  et les contrôles en échec. Une liste `exceptions` vide veut dire « ligne valide ».
- `pourquoi` est une explication pour le lecteur. Le test compare `controle` et
  `suggestion`, pas le texte de `pourquoi`.
