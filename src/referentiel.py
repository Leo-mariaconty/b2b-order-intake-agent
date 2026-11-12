"""Chargement des deux fichiers de référence : le catalogue et les clients.

Chaque fichier CSV devient une liste de dictionnaires, un par ligne.
Exemple pour un produit :
    {"reference": "VB-101", "ean": "2055501001016",
     "libelle": "Crème hydratante visage 50 ml", "colisage": 6,
     "prix_tarif_ht": "9.80"}
"""

import csv
from pathlib import Path


def charger_catalogue(chemin: Path) -> list[dict]:
    with open(chemin, newline="", encoding="utf-8") as fichier:
        produits = list(csv.DictReader(fichier))
    for produit in produits:
        produit["colisage"] = int(produit["colisage"])
    return produits


def charger_clients(chemin: Path) -> list[dict]:
    with open(chemin, newline="", encoding="utf-8") as fichier:
        return list(csv.DictReader(fichier))
