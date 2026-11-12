"""Étape 4 : le rapport de traitement, en Markdown.

Tous les chiffres sont comptés à partir des commandes traitées. Le rapport ne
contient pas l'heure du lancement : relancer le script sur les mêmes données
donne exactement le même fichier.
"""

from collections import Counter
from pathlib import Path

from src.resultats import CommandeControlee

NOMS_DES_CONTROLES = {
    "extraction": "Extraction illisible",
    "client": "Client non identifié",
    "date": "Date incomprise",
    "reference": "Produit non reconnu",
    "quantite": "Quantité refusée",
}


def pourcentage(part: int, total: int) -> str:
    return f"{100 * part / total:.0f} %" if total else "sans objet"


def ecrire_rapport(commandes: list[CommandeControlee], chemin: Path) -> None:
    valides = [c for c in commandes if c.est_valide()]
    lignes_total = sum(len(c.lignes) for c in commandes)
    lignes_valides = sum(len(c.lignes) for c in valides)

    motifs = Counter()
    for commande in commandes:
        for exception in commande.exceptions_commande:
            motifs[exception.controle] += 1
        for ligne in commande.lignes:
            for exception in ligne.exceptions:
                motifs[exception.controle] += 1

    texte = [
        "# Rapport de traitement",
        "",
        "## En bref",
        "",
        f"- Emails traités : {len(commandes)}",
        f"- Lignes de commande extraites : {lignes_total}",
        f"- Commandes passées sans intervention : {len(valides)} sur {len(commandes)} "
        f"({pourcentage(len(valides), len(commandes))})",
        f"- Lignes passées sans intervention : {lignes_valides} sur {lignes_total} "
        f"({pourcentage(lignes_valides, lignes_total)})",
        f"- Commandes envoyées à un humain : {len(commandes) - len(valides)}",
        "",
        "## Exceptions par motif",
        "",
    ]

    if motifs:
        texte += ["| Motif | Nombre |", "|---|---|"]
        for controle, nom in NOMS_DES_CONTROLES.items():
            if motifs[controle]:
                texte.append(f"| {nom} | {motifs[controle]} |")
    else:
        texte.append("Aucune exception.")

    texte += ["", "## Détail par email", "", "| Email | Lignes | Destination | Exceptions |", "|---|---|---|---|"]
    for commande in commandes:
        nombre = len(commande.exceptions_commande) + sum(len(l.exceptions) for l in commande.lignes)
        destination = "Import Odoo" if commande.est_valide() else "Exceptions"
        texte.append(f"| {commande.email_source} | {len(commande.lignes)} | {destination} | {nombre} |")

    chemin.write_text("\n".join(texte) + "\n", encoding="utf-8")
