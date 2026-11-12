"""Prépare les fichiers à importer dans une base Odoo de test, avant les commandes.

Ce script ne fait pas partie du pipeline. Il transforme les deux fichiers de
référence (data/clients.csv et data/catalogue.csv) en fichiers d'import Odoo,
rangés dans odoo/. À lancer depuis la racine du dépôt :

    python scripts/generer_fichiers_odoo.py

Les titres de colonnes sont les noms techniques des champs Odoo, reconnus
quelle que soit la langue de l'interface. Marche à suivre : docs/test_odoo.md
"""

import csv
from pathlib import Path

RACINE = Path(__file__).parent.parent
DATA = RACINE / "data"
DOSSIER_ODOO = RACINE / "odoo"


def lire(chemin: Path) -> list[dict]:
    with open(chemin, newline="", encoding="utf-8") as fichier:
        return list(csv.DictReader(fichier))


def ecrire(chemin: Path, titres: list[str], lignes: list[list]) -> None:
    with open(chemin, "w", newline="", encoding="utf-8") as fichier:
        tableau = csv.writer(fichier)
        tableau.writerow(titres)
        tableau.writerows(lignes)
    print(f"{len(lignes)} lignes écrites dans {chemin.relative_to(RACINE)}")


def main():
    DOSSIER_ODOO.mkdir(exist_ok=True)

    # Clients (modèle Odoo : res.partner)
    # id = identifiant externe. C'est lui que sorties/import_odoo.csv utilise
    # dans sa colonne partner_id/id pour désigner le client sans ambiguïté.
    ecrire(
        DOSSIER_ODOO / "clients.csv",
        ["id", "name", "is_company", "ref", "zip", "city", "country_id/id"],
        [
            [f"client_{c['code_client']}", c["nom"], "True", c["code_client"],
             c["code_postal"], c["ville"], "base.fr"]
            for c in lire(DATA / "clients.csv")
        ],
    )

    # Produits (modèle Odoo : product.template)
    # default_code = référence interne. C'est elle que sorties/import_odoo.csv
    # utilise dans sa colonne order_line/product_id pour désigner le produit.
    ecrire(
        DOSSIER_ODOO / "produits.csv",
        ["id", "name", "default_code", "barcode", "list_price"],
        [
            [f"produit_{p['reference'].replace('-', '_')}", p["libelle"], p["reference"],
             p["ean"], p["prix_tarif_ht"]]
            for p in lire(DATA / "catalogue.csv")
        ],
    )


if __name__ == "__main__":
    main()
