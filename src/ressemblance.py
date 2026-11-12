"""Ressemblance entre un nom de produit écrit dans un email et le catalogue.

Sert uniquement à proposer des candidats à l'humain qui traite une exception.
Ce module ne valide jamais une ligne.

La méthode est volontairement simple : on regarde quelle part des mots de
l'email se retrouve dans le libellé du catalogue.
"""

import unicodedata
from difflib import SequenceMatcher


def mots_utiles(texte: str) -> list[str]:
    """Met en minuscules, retire les accents, garde les mots de 3 lettres et plus.

    « 2 cartons du Déo » -> ["cartons", "deo"]
    """
    sans_accents = unicodedata.normalize("NFD", texte.lower())
    sans_accents = "".join(c for c in sans_accents if unicodedata.category(c) != "Mn")
    propre = "".join(c if c.isalnum() else " " for c in sans_accents)
    return [mot for mot in propre.split() if len(mot) >= 3]


def ressemblance_de_deux_mots(mot_a: str, mot_b: str) -> float:
    """1.0 si l'un est le début de l'autre (« deo » / « deodorant », « gels » /
    « gel »), sinon une note de 0 à 1 selon les lettres en commun."""
    if mot_a.startswith(mot_b) or mot_b.startswith(mot_a):
        return 1.0
    return SequenceMatcher(None, mot_a, mot_b).ratio()


def score_ressemblance(libelle_email: str, libelle_catalogue: str) -> float:
    """Note de 0 à 1 : part des mots de l'email retrouvés dans le libellé catalogue."""
    mots_email = mots_utiles(libelle_email)
    mots_catalogue = mots_utiles(libelle_catalogue)
    if not mots_email or not mots_catalogue:
        return 0.0

    total = 0.0
    for mot in mots_email:
        total += max(ressemblance_de_deux_mots(mot, autre) for autre in mots_catalogue)
    return total / len(mots_email)


def suggerer_produits(libelle_email: str | None, catalogue: list[dict], seuil: float) -> list[str]:
    """Références des produits dont le libellé ressemble assez, dans l'ordre du catalogue."""
    if not libelle_email:
        return []
    return [
        produit["reference"]
        for produit in catalogue
        if score_ressemblance(libelle_email, produit["libelle"]) >= seuil
    ]
