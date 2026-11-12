# Guide pour l'équipe ADV

Cette page s'adresse à la personne qui traite les commandes. Aucune connaissance
technique n'est nécessaire.

## Ce que fait l'outil

Il lit les emails de commande et prépare deux fichiers dans le dossier `sorties/` :

| Fichier | Ce qu'il contient | Ce que vous en faites |
|---|---|---|
| `import_odoo.csv` | Les commandes où tout a été vérifié | Import dans Odoo, sans ressaisie |
| `exceptions.csv` | Les commandes où quelque chose cloche | Vous les traitez à la main |
| `rapport.md` | Le bilan du traitement | Lecture seule |

L'outil ne corrige jamais une commande à votre place. En cas de doute, il vous
la confie en entier, avec la raison.

## Lire le fichier des exceptions

Ouvrez `exceptions.csv` dans Excel : onglet Données, puis « À partir d'un fichier
texte/CSV », et choisissez la virgule comme séparateur.

Chaque rangée correspond à une ligne de commande. Les colonnes :

| Colonne | Ce qu'elle dit |
|---|---|
| `email_source` | L'email d'où vient la commande |
| `ligne` | Le numéro de la ligne dans l'email, ou « commande entière » |
| `texte_de_l_email` | Ce que la pharmacie a écrit, mot pour mot |
| `produit_reconnu` | La référence trouvée dans le catalogue, si elle l'a été |
| `quantite_lue` | La quantité lue dans l'email |
| `statut` | « à traiter » : il y a un problème. « en attente » : la ligne est correcte |
| `controle` | Le type de problème (voir le tableau ci-dessous) |
| `raison` | L'explication en clair |
| `suggestion` | Une piste, quand l'outil en a une. À vérifier, jamais appliquée seule |

Une commande retenue apparaît toujours en entier. Ses lignes correctes sont
marquées « en attente » : vous n'avez rien à corriger dessus, elles attendent
simplement que le reste de la commande soit réglé.

### Que faire selon le problème

| `controle` | Ce que ça veut dire | Ce que vous faites |
|---|---|---|
| `client` | La pharmacie n'est pas identifiée avec certitude (homonymes, code inconnu, nom sans code postal) | Choisir le bon client, parmi les suggestions s'il y en a, ou rappeler la pharmacie |
| `reference` | Le produit n'a pas de code, ou le code est faux ou inconnu | Vérifier la suggestion. Si deux produits sont proposés, demander à la pharmacie |
| `quantite` | La quantité est en cartons, hors colisage, au-dessus du maximum, ou n'est pas un nombre | Confirmer la quantité avec la pharmacie, ou l'ajuster selon vos usages |
| `date` | La date de l'email n'a pas été comprise | Saisir la date à la main |
| `extraction` | L'email ou sa pièce jointe n'a pas pu être lu (PDF vide, par exemple) | Ouvrir l'email d'origine et saisir la commande à la main |

## Modifier une règle

Les règles sont dans le fichier `regles.yaml`, à la racine du projet. Il s'ouvre
avec n'importe quel éditeur de texte (le Bloc-notes convient).

Chaque règle tient sur une ligne : son nom, deux-points, sa valeur. Les lignes
qui commencent par `#` sont des explications, l'outil ne les lit pas.

**Exemple 1 : accepter jusqu'à 150 unités par ligne.** Remplacez

```yaml
plafond_quantite_par_ligne: 100
```

par

```yaml
plafond_quantite_par_ligne: 150
```

**Exemple 2 : accepter les quantités hors colisage.** Remplacez `true` par `false` :

```yaml
colisage_obligatoire: false
```

**Exemple 3 : accepter le mot « flacons » comme unité.** Ajoutez une ligne à la
liste, en gardant le tiret et les deux espaces devant :

```yaml
unites_acceptees:
  - unité
  - unités
  - pièce
  - pièces
  - flacons
```

Trois précautions :

1. Ne changez que la valeur, à droite des deux-points. Le nom à gauche doit
   rester tel quel.
2. Enregistrez le fichier, puis demandez à relancer le traitement. La nouvelle
   règle s'applique à partir de ce moment.
3. Si une valeur est mal écrite (un mot à la place d'un nombre, par exemple),
   l'outil s'arrête sans rien écrire et nomme la règle en cause. Corrigez-la et
   relancez.

## Qui fait quoi

- **L'équipe ADV** décide des règles (`regles.yaml`) et traite les exceptions.
- **L'équipe technique** maintient le code et les colonnes du fichier Odoo
  (`odoo_colonnes.yaml`).

Si une exception vous paraît injustifiée, ou si une commande fausse est passée
dans l'import, signalez-le à l'équipe technique avec le nom de l'email : c'est
ce qui permet d'améliorer l'outil.
