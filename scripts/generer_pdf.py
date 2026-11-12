"""Fabrique le bon de commande PDF joint à l'email n°5.

Ce script ne fait pas partie du pipeline : il sert une seule fois, à créer une
pièce jointe de démonstration. À lancer depuis la racine du dépôt :

    python scripts/generer_pdf.py
"""

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

RACINE = Path(__file__).parent.parent
CATALOGUE = RACINE / "data" / "catalogue.csv"
SORTIE = RACINE / "data" / "inbox" / "pieces_jointes" / "05_bon_de_commande.pdf"

# Ce que la pharmacie commande : (référence, quantité).
# Le libellé et l'EAN sont relus dans le catalogue pour rester cohérents.
LIGNES_COMMANDEES = [("VB-105", 12), ("VB-107", 6), ("VB-111", 12), ("VB-112", 36)]


def main():
    with open(CATALOGUE, newline="", encoding="utf-8") as fichier:
        catalogue = {produit["reference"]: produit for produit in csv.DictReader(fichier)}

    tableau = [["Référence", "EAN", "Désignation", "Quantité"]]
    for reference, quantite in LIGNES_COMMANDEES:
        produit = catalogue[reference]
        tableau.append([reference, produit["ean"], produit["libelle"], str(quantite)])

    styles = getSampleStyleSheet()
    contenu = [
        Paragraph("BON DE COMMANDE n° BC-2026-0457", styles["Title"]),
        Paragraph("Date : 09/11/2026", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("<b>Pharmacie des Remparts</b>", styles["Normal"]),
        Paragraph("Code client : C1007", styles["Normal"]),
        Paragraph("8 rue des Remparts, 67990 Hautefeuille", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Fournisseur : Laboratoires Velbrume", styles["Normal"]),
        Spacer(1, 18),
        Table(
            tableau,
            style=TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                ]
            ),
        ),
    ]

    # invariant=1 : le PDF produit est identique à chaque lancement
    SimpleDocTemplate(str(SORTIE), pagesize=A4, invariant=1).build(contenu)
    print(f"PDF écrit : {SORTIE.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
