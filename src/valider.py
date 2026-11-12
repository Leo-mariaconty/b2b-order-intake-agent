"""Étape 1 : vérifier que le JSON écrit par le skill est exploitable.

On ne juge pas encore le contenu de la commande (ce sera l'étape 2). On vérifie
seulement que le fichier existe, qu'il a la bonne forme, et que le LLM n'a pas
signalé un email illisible. Dans tous les cas d'échec, la fonction renvoie une
raison en français : la commande partira en exception « extraction illisible ».
"""

import json
from pathlib import Path

from pydantic import ValidationError

from src.schema import Extraction


def valider_extraction(nom_email: str, dossier_extractions: Path) -> tuple[Extraction | None, str | None]:
    """Renvoie (extraction, None) si tout va bien, sinon (None, raison)."""
    chemin = dossier_extractions / (Path(nom_email).stem + ".json")

    if not chemin.exists():
        return None, f"Aucun fichier d'extraction trouvé pour cet email ({chemin.name} attendu)."

    try:
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, f"Le fichier {chemin.name} n'est pas un JSON lisible."

    try:
        extraction = Extraction.model_validate(contenu)
    except ValidationError as erreur:
        premier_probleme = erreur.errors()[0]
        champ = ".".join(str(element) for element in premier_probleme["loc"]) or "racine"
        return None, (
            f"Le fichier {chemin.name} ne respecte pas le format attendu "
            f"({len(erreur.errors())} problème(s), le premier sur le champ « {champ} »)."
        )

    if extraction.email_source != nom_email:
        return None, (
            f"Le fichier {chemin.name} dit venir de « {extraction.email_source} » "
            f"au lieu de « {nom_email} »."
        )

    if not extraction.lisible:
        motif = extraction.motif_illisible or "motif non précisé"
        return None, f"L'email ou sa pièce jointe n'a pas pu être lu : {motif}."

    if not extraction.lignes:
        return None, "Aucune ligne de commande n'a été trouvée dans cet email."

    return extraction, None
