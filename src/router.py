"""Étape 3 : envoyer chaque commande au bon endroit et écrire les deux fichiers.

Règle unique : une commande entièrement valide va dans l'import Odoo. Une
commande qui a au moins une exception part en entier chez un humain. Une
commande n'est jamais coupée en deux.
"""

import csv
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from src.resultats import CommandeControlee, ExceptionControle


def router(commandes: list[CommandeControlee]) -> tuple[list[CommandeControlee], list[CommandeControlee]]:
    """Sépare les commandes en deux listes : (valides, en exception)."""
    valides = [commande for commande in commandes if commande.est_valide()]
    en_exception = [commande for commande in commandes if not commande.est_valide()]
    return valides, en_exception


# --- Fichier d'import Odoo ---------------------------------------------------


class ColonnesOdoo(BaseModel):
    """Contenu attendu de odoo_colonnes.yaml."""

    model_config = ConfigDict(extra="forbid")

    separateur: str
    format_date: str
    colonnes_commande: dict[str, str]  # titre de colonne -> modèle de valeur
    colonnes_ligne: dict[str, str]


def charger_colonnes_odoo(chemin: Path) -> ColonnesOdoo:
    contenu = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    return ColonnesOdoo.model_validate(contenu)


def ecrire_import_odoo(commandes_valides: list[CommandeControlee], chemin: Path, colonnes: ColonnesOdoo) -> None:
    """Écrit le CSV d'import : une ligne par article, les champs de commande
    seulement sur la première ligne de chaque commande."""
    titres = list(colonnes.colonnes_commande) + list(colonnes.colonnes_ligne)

    with open(chemin, "w", newline="", encoding="utf-8") as fichier:
        tableau = csv.writer(fichier, delimiter=colonnes.separateur)
        tableau.writerow(titres)

        for commande in commandes_valides:
            valeurs_commande = {
                "code_client": commande.client["code_client"],
                "nom_client": commande.client["nom"],
                "reference_commande": commande.reference_commande or "",
                "date_commande": commande.date_commande.strftime(colonnes.format_date),
                "email_source": commande.email_source,
            }
            for ligne in commande.lignes:
                valeurs_ligne = {
                    "reference": ligne.produit["reference"],
                    "ean": ligne.produit["ean"],
                    "libelle": ligne.produit["libelle"],
                    "quantite": ligne.quantite,
                    "prix_unitaire": ligne.produit["prix_tarif_ht"],
                }
                if ligne.numero == 1:
                    cellules_commande = remplir(colonnes.colonnes_commande, valeurs_commande)
                else:
                    cellules_commande = [""] * len(colonnes.colonnes_commande)
                tableau.writerow(cellules_commande + remplir(colonnes.colonnes_ligne, valeurs_ligne))


def remplir(modeles: dict[str, str], valeurs: dict) -> list[str]:
    """Remplace les mots entre accolades : "[{reference}] {libelle}" devient
    "[VB-102] Crème mains réparatrice 75 ml"."""
    try:
        return [modele.format(**valeurs) for modele in modeles.values()]
    except KeyError as erreur:
        raise ValueError(
            f"odoo_colonnes.yaml utilise le mot {{{erreur.args[0]}}}, qui n'existe pas ici. "
            f"Mots disponibles : {', '.join(valeurs)}."
        ) from None


# --- Fichier des exceptions --------------------------------------------------

TITRES_EXCEPTIONS = [
    "email_source",
    "ligne",
    "texte_de_l_email",
    "produit_reconnu",
    "quantite_lue",
    "statut",
    "controle",
    "raison",
    "suggestion",
]

LIGNE_EN_ATTENTE = "Ligne correcte. Elle attend que le reste de la commande soit traité."


def ecrire_exceptions(
    commandes_en_exception: list[CommandeControlee],
    chemin: Path,
    catalogue: list[dict],
    clients: list[dict],
) -> None:
    """Écrit le fichier destiné à l'ADV : toutes les lignes des commandes en
    exception, y compris les lignes correctes, pour traiter la commande d'un bloc."""
    # utf-8-sig : pour que les accents s'affichent bien à l'ouverture dans Excel
    with open(chemin, "w", newline="", encoding="utf-8-sig") as fichier:
        tableau = csv.writer(fichier)
        tableau.writerow(TITRES_EXCEPTIONS)

        for commande in commandes_en_exception:
            for exception in commande.exceptions_commande:
                tableau.writerow(
                    [commande.email_source, "commande entière", "", "", "", "à traiter",
                     exception.controle, exception.raison,
                     texte_suggestion(exception, catalogue, clients)]
                )
            for ligne in commande.lignes:
                debut = [
                    commande.email_source,
                    ligne.numero,
                    ligne.texte_source,
                    ligne.produit["reference"] if ligne.produit else "",
                    ligne.quantite if ligne.quantite is not None else "",
                ]
                if not ligne.exceptions:
                    tableau.writerow(debut + ["en attente", "", LIGNE_EN_ATTENTE, ""])
                for exception in ligne.exceptions:
                    tableau.writerow(
                        debut + ["à traiter", exception.controle, exception.raison,
                                 texte_suggestion(exception, catalogue, clients)]
                    )


def texte_suggestion(exception: ExceptionControle, catalogue: list[dict], clients: list[dict]) -> str:
    """Transforme les codes suggérés en texte lisible, avec le nom à côté du code."""
    if exception.controle == "reference":
        noms = {p["reference"]: p["libelle"] for p in catalogue}
        return " ; ".join(f"{code} {noms[code]}" for code in exception.suggestion)
    if exception.controle == "client":
        fiches = {c["code_client"]: c for c in clients}
        return " ; ".join(
            f"{code} {fiches[code]['nom']} ({fiches[code]['code_postal']} {fiches[code]['ville']})"
            for code in exception.suggestion
        )
    return " ou ".join(exception.suggestion)
