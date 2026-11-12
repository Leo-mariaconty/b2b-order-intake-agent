"""Point d'entrée : enchaîne les étapes du pipeline.

À lancer depuis la racine du dépôt :

    python -m src.main

Le script part des emails de data/inbox/ et des JSON de data/extractions/.
Chaque email doit finir quelque part : aucun n'est ignoré en silence.
"""

from pathlib import Path

from src.valider import valider_extraction

RACINE = Path(__file__).parent.parent
DOSSIER_INBOX = RACINE / "data" / "inbox"
DOSSIER_EXTRACTIONS = RACINE / "data" / "extractions"

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


def main():
    emails = lister_emails(DOSSIER_INBOX)
    print(f"{len(emails)} email(s) dans {DOSSIER_INBOX.relative_to(RACINE)}/")

    for nom_email in emails:
        extraction, raison = valider_extraction(nom_email, DOSSIER_EXTRACTIONS)
        if extraction is None:
            print(f"  [extraction illisible] {nom_email} : {raison}")
        else:
            print(f"  [extraction valide]    {nom_email} : {len(extraction.lignes)} ligne(s)")


if __name__ == "__main__":
    main()
