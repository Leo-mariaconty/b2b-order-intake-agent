"""Point d'entrée : enchaîne les quatre étapes du pipeline.

À lancer depuis la racine du dépôt :

    python -m src.main

Le script part des emails de data/inbox/ et des JSON de data/extractions/.
Chaque email finit soit dans l'import Odoo, soit dans les exceptions : aucun
n'est ignoré en silence.
"""

import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from src.controler import controler_commande
from src.rapport import ecrire_rapport
from src.referentiel import charger_catalogue, charger_clients
from src.regles import Regles, charger_regles
from src.resultats import CommandeControlee, ExceptionControle
from src.router import ColonnesOdoo, charger_colonnes_odoo, ecrire_exceptions, ecrire_import_odoo, router
from src.valider import valider_extraction

RACINE = Path(__file__).parent.parent

EXTENSIONS_EMAIL = {".txt", ".html"}


def lister_emails(dossier_inbox: Path) -> list[str]:
    """Un email = un fichier .txt ou .html posé directement dans inbox/.

    Les pièces jointes sont dans le sous-dossier pieces_jointes/ et ne comptent
    pas comme des emails.
    """
    return sorted(
        fichier.name
        for fichier in dossier_inbox.iterdir()
        if fichier.is_file() and fichier.suffix in EXTENSIONS_EMAIL
    )


def traiter(
    dossier_inbox: Path,
    dossier_extractions: Path,
    dossier_sorties: Path,
    catalogue: list[dict],
    clients: list[dict],
    regles: Regles,
    colonnes_odoo: ColonnesOdoo,
) -> list[CommandeControlee]:
    """Fait tout le travail pour un dossier d'emails et renvoie les commandes contrôlées."""
    emails = lister_emails(dossier_inbox)
    commandes = []

    for nom_email in emails:
        # Étape 1 : valider le JSON d'extraction
        extraction, raison = valider_extraction(nom_email, dossier_extractions)
        if extraction is None:
            exception = ExceptionControle("extraction", f"Extraction illisible. {raison}")
            commandes.append(CommandeControlee(nom_email, exceptions_commande=[exception]))
            continue
        # Étape 2 : contrôler
        commandes.append(controler_commande(extraction, catalogue, clients, regles))

    # Étape 3 : router et écrire les deux fichiers
    valides, en_exception = router(commandes)
    if len(valides) + len(en_exception) != len(emails):
        raise RuntimeError("Un email n'a été rangé nulle part : le script s'arrête.")

    dossier_sorties.mkdir(exist_ok=True)
    ecrire_import_odoo(valides, dossier_sorties / "import_odoo.csv", colonnes_odoo)
    ecrire_exceptions(en_exception, dossier_sorties / "exceptions.csv", catalogue, clients)

    # Étape 4 : rapport
    ecrire_rapport(commandes, dossier_sorties / "rapport.md")
    return commandes


def charger_ou_arreter(fonction_de_chargement, chemin: Path):
    """Lit un fichier de réglage. S'il contient une erreur, arrête le script
    avec un message clair, avant d'avoir écrit quoi que ce soit."""
    try:
        return fonction_de_chargement(chemin)
    except (ValidationError, yaml.YAMLError) as erreur:
        sys.exit(f"Erreur dans {chemin.name} : le script s'arrête sans rien écrire.\n{erreur}")


def main():
    commandes = traiter(
        dossier_inbox=RACINE / "data" / "inbox",
        dossier_extractions=RACINE / "data" / "extractions",
        dossier_sorties=RACINE / "sorties",
        catalogue=charger_catalogue(RACINE / "data" / "catalogue.csv"),
        clients=charger_clients(RACINE / "data" / "clients.csv"),
        regles=charger_ou_arreter(charger_regles, RACINE / "regles.yaml"),
        colonnes_odoo=charger_ou_arreter(charger_colonnes_odoo, RACINE / "odoo_colonnes.yaml"),
    )

    print(f"{len(commandes)} email(s) traité(s)")
    for commande in commandes:
        nombre = len(commande.exceptions_commande) + sum(len(l.exceptions) for l in commande.lignes)
        if commande.est_valide():
            print(f"  [import Odoo] {commande.email_source} : {len(commande.lignes)} ligne(s)")
        else:
            print(f"  [exceptions]  {commande.email_source} : {nombre} exception(s)")
    print("Fichiers écrits dans sorties/ : import_odoo.csv, exceptions.csv, rapport.md")


if __name__ == "__main__":
    main()
