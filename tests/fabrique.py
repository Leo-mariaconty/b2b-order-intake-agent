"""Petites commandes toutes prêtes, réutilisées par plusieurs fichiers de tests."""

from datetime import datetime

from src.resultats import CommandeControlee, ExceptionControle, LigneControlee

CREME = {"reference": "VB-102", "ean": "2055501001023", "libelle": "Crème mains réparatrice 75 ml",
         "colisage": 12, "prix_tarif_ht": "4.20"}
GEL = {"reference": "VB-104", "ean": "2055501001047", "libelle": "Gel douche surgras 400 ml",
       "colisage": 6, "prix_tarif_ht": "5.90"}
TILLEULS = {"code_client": "C1003", "nom": "Pharmacie des Tilleuls", "code_postal": "44990",
            "ville": "Saint-Avel-des-Marais"}


def commande_valide(email="a.txt") -> CommandeControlee:
    return CommandeControlee(
        email_source=email,
        client=TILLEULS,
        reference_commande="CDE-1",
        date_commande=datetime(2026, 11, 3, 9, 12),
        lignes=[
            LigneControlee(1, "12 x crème", CREME, 12),
            LigneControlee(2, "6 x gel", GEL, 6),
        ],
    )


def commande_avec_une_ligne_en_exception(email="b.txt") -> CommandeControlee:
    commande = commande_valide(email)
    commande.lignes[1].quantite = 10
    commande.lignes[1].exceptions.append(
        ExceptionControle("quantite", "La quantité 10 n'est pas un multiple du colisage (6).", ["6", "12"])
    )
    return commande
