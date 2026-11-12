# Tester l'import dans une base Odoo

Objectif : vérifier que `sorties/import_odoo.csv` crée bien deux devis dans une
vraie base Odoo, sans ressaisie.

**État de cette procédure.** Elle a été préparée à partir de la documentation
Odoo et du code source d'Odoo 19 (module d'import), pas encore déroulée dans
une base. Les intitulés français viennent des fichiers de traduction d'Odoo 19 :
ils peuvent varier légèrement selon la version. Le résultat du test est noté
dans le README.

## Avant de commencer

- Une base Odoo Online avec l'application **Ventes**. Aucune autre application
  à installer.
- Trois fichiers du dépôt, à télécharger sur votre ordinateur (sur GitHub :
  ouvrir le fichier, puis le bouton « Download raw file ») :

| Ordre | Fichier | Contenu |
|---|---|---|
| 1 | `odoo/clients.csv` | Les 8 pharmacies |
| 2 | `odoo/produits.csv` | Les 12 produits |
| 3 | `sorties/import_odoo.csv` | Les 2 commandes validées par le pipeline |

L'ordre compte : les commandes désignent les clients et les produits, qui
doivent donc exister avant.

Les titres de colonnes des trois fichiers sont les noms techniques des champs
Odoo (`partner_id`, `default_code`...). C'est voulu : ils sont reconnus quelle
que soit la langue de l'interface.

## Les gestes communs aux trois imports

1. Ouvrir la liste concernée (menu indiqué à chaque étape).
2. Passer en vue liste : icône à lignes horizontales, en haut à droite.
3. Cliquer sur la roue crantée ⚙ à côté du titre de la page, puis sur
   **Importer des enregistrements**.
4. Cliquer sur **Télécharger un fichier de données** et choisir le fichier.
5. Odoo affiche un tableau : à gauche **Colonne de fichier**, à droite
   **Champ Odoo**. Vérifier que chaque ligne correspond au tableau donné à
   l'étape.
6. Cliquer sur **Tester**. Message attendu sur fond vert : « Tout semble correct. »
7. Cliquer sur **Importer**. Message attendu : « N enregistrements importés avec
   succès », puis retour à la liste.

Ne cliquez sur **Importer** que si **Tester** a réussi.

## Étape 1 : les clients

Menu : **Ventes > Commandes > Clients**. Fichier : `odoo/clients.csv`.

| Colonne de fichier | Champ Odoo attendu |
|---|---|
| `id` | ID externe |
| `name` | Nom |
| `is_company` | Est une société |
| `ref` | Référence |
| `zip` | Code postal |
| `city` | Ville |
| `country_id/id` | Pays / ID externe |

Ce que vous devez voir après l'import :
- le message « 8 enregistrements importés avec succès » ;
- 8 pharmacies dans la liste, dont deux « Pharmacie du Centre » (une à
  Valbrune-sur-Orve, une à Montclar-le-Lac) ;
- en ouvrant « Pharmacie des Tilleuls » : pays France, et la référence `C1003`
  dans l'onglet « Ventes et achats ».

Si la liste paraît vide après l'import, retirez le filtre présent dans la barre
de recherche (la petite croix à côté de « Clients »).

## Étape 2 : les produits

Menu : **Ventes > Produits > Produits**. Fichier : `odoo/produits.csv`.

| Colonne de fichier | Champ Odoo attendu |
|---|---|
| `id` | ID externe |
| `name` | Nom |
| `default_code` | Référence interne |
| `barcode` | Code-barres |
| `list_price` | Prix de vente |

Ce que vous devez voir après l'import :
- le message « 12 enregistrements importés avec succès » ;
- 12 produits dans la liste ;
- en ouvrant « Crème mains réparatrice 75 ml » : référence interne `VB-102`,
  prix de vente 4,20.

La référence interne est le point important : c'est par elle que les commandes
retrouveront les produits.

## Étape 3 : les commandes

Menu : **Ventes > Commandes > Devis**. Fichier : `sorties/import_odoo.csv`.

| Colonne de fichier | Champ Odoo attendu |
|---|---|
| `partner_id/id` | Client / ID externe |
| `client_order_ref` | Référence client |
| `date_order` | Date de la commande |
| `order_line/product_id` | Lignes de commande / Produit |
| `order_line/product_uom_qty` | Lignes de commande / Quantité |
| `order_line/price_unit` | Lignes de commande / Prix unitaire |

Le fichier compte 7 lignes mais seulement 2 commandes : les champs de commande
ne sont remplis que sur la première ligne de chacune. C'est le format prévu par
Odoo pour les commandes à plusieurs lignes.

Ce que vous devez voir après l'import :
- le message « 2 enregistrements importés avec succès » ;
- deux devis, à l'état « Devis » (rien n'est confirmé ni envoyé) :

| Client | Référence client | Date | Lignes | Montant hors taxes |
|---|---|---|---|---|
| Pharmacie des Tilleuls | CDE-TIL-2311 | 03/11/2026 09:12 | 3 | 136,20 |
| Pharmacie des Remparts | BC-2026-0457 | 09/11/2026 08:40 | 4 | 279,00 |

- en ouvrant le devis de la Pharmacie des Tilleuls, ces trois lignes :

| Produit | Quantité | Prix unitaire |
|---|---|---|
| [VB-102] Crème mains réparatrice 75 ml | 12 | 4,20 |
| [VB-104] Gel douche surgras 400 ml | 6 | 5,90 |
| [VB-108] Stick lèvres nourrissant 4 g | 24 | 2,10 |

Le montant hors taxes est le chiffre à comparer. Le montant toutes taxes dépend
des taxes réglées dans votre base. Si l'heure affichée est décalée d'une heure
ou deux, c'est le fuseau horaire de votre compte Odoo, pas une erreur du fichier.

Pour le README : faites une capture d'écran du devis de la Pharmacie des
Tilleuls ouvert, et enregistrez-la sous `docs/images/test_odoo.png`.

## Si quelque chose ne se passe pas comme prévu

**Une colonne affiche « Pour importer, sélectionnez un champ... »**
Odoo n'a pas relié la colonne tout seul. Cliquez sur cette zone et choisissez le
champ indiqué dans le tableau de l'étape. Pour un champ en deux parties
(« Client / ID externe », « Lignes de commande / Produit »), cherchez d'abord la
première partie, dépliez-la avec la flèche à sa droite, puis choisissez la
seconde. Notez la colonne concernée : c'est une information utile pour ajuster
`odoo_colonnes.yaml`.

**« Une seule colonne a été trouvée dans le fichier »**
Dans le panneau **Formatage**, à gauche, réglez **Séparateur** sur « Virgule ».

**Les accents sont abîmés dans l'aperçu**
Dans **Formatage**, réglez **Encodage** sur « utf-8 ».

**« Aucun enregistrement correspondant trouvé pour l'id externe 'client_C1003' dans le champ 'Client' »**
Les clients n'ont pas été importés, ou l'ont été sans la colonne `id`. Refaites
l'étape 1 en vérifiant que `id` est bien relié à « ID externe ».

**« Aucun enregistrement correspondant trouvé pour le nom 'VB-102' dans le champ 'Produit' »**
Les produits n'ont pas été importés, ou `default_code` n'était pas relié à
« Référence interne ». Refaites l'étape 2.

**Un avertissement « plusieurs correspondances » sur un produit**
Deux produits portent la même référence interne, souvent après un import fait
deux fois sans la colonne `id`. Archivez le doublon dans la liste des produits.

**Une erreur sur le code-barres à l'étape 2**
Le code-barres ne sert pas à retrouver les produits. Dans le tableau, videz le
champ Odoo en face de `barcode` (la croix), puis relancez **Tester**.

**Une erreur sur la date à l'étape 3**
Dans **Formatage**, vérifiez **Format de date**. Les dates du fichier sont
écrites année-mois-jour heure:minute:seconde, par exemple `2026-11-03 09:12:00`.

**Vous voulez recommencer**
- Clients et produits : vous pouvez réimporter les mêmes fichiers. Grâce à la
  colonne `id`, Odoo met à jour les fiches au lieu de les créer en double.
- Commandes : le fichier n'a volontairement pas de colonne `id`. Chaque import
  crée de nouveaux devis. Supprimez les devis de test avant de réimporter.

**Autre message d'erreur**
N'importez pas. Notez le message exact, la ligne concernée et faites une
capture : le réglage se fait ensuite dans `odoo_colonnes.yaml`, sans toucher au
code Python.

## Ce que ce test ne vérifie pas

- Le colisage n'existe pas dans les fiches produits importées : il est contrôlé
  avant, par le pipeline, à partir de `data/catalogue.csv`.
- Les prix sont ceux du catalogue de démonstration, sans remise ni liste de prix.
- Les commandes en exception ne sont pas importées : elles restent dans
  `sorties/exceptions.csv`.
