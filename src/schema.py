"""Forme du JSON que le skill doit écrire pour chaque email.

C'est le contrat entre les deux moitiés du projet : le LLM remplit ce
formulaire, le code Python le relit. Tous les champs sont obligatoires : quand
une information n'est pas écrite dans l'email, le LLM doit mettre `null`
explicitement. Un champ oublié ou un champ en trop rend le JSON invalide.

Tout est du texte recopié, y compris la quantité : c'est le code, pas le LLM,
qui vérifie que « 12 » est bien un nombre entier acceptable.
"""

from pydantic import BaseModel, ConfigDict


class Modele(BaseModel):
    """Réglages communs aux trois formulaires ci-dessous."""

    model_config = ConfigDict(
        extra="forbid",  # un champ inconnu = JSON refusé
        coerce_numbers_to_str=True,  # si le LLM écrit 12 au lieu de "12", on accepte
    )


class ClientExtrait(Modele):
    code_client: str | None  # ex. "C1003", seulement s'il est écrit dans l'email
    nom: str | None  # ex. "Pharmacie des Tilleuls"
    code_postal: str | None
    ville: str | None


class LigneExtraite(Modele):
    texte_source: str  # le passage de l'email, recopié tel quel
    reference: str | None  # référence interne écrite dans l'email, ex. "VB-101"
    ean: str | None  # code-barres tel qu'écrit, même s'il semble faux
    libelle: str | None  # nom du produit tel qu'écrit
    quantite: str | None  # le nombre tel qu'écrit, ex. "12"
    unite: str | None  # ex. "cartons", ou null si aucune unité n'est écrite


class Extraction(Modele):
    email_source: str  # nom du fichier de data/inbox/
    lisible: bool  # false si l'email ou sa pièce jointe est vide ou illisible
    motif_illisible: str | None  # explication courte quand lisible vaut false
    client: ClientExtrait
    reference_commande: str | None  # numéro de commande donné par la pharmacie
    date_email: str | None  # la ligne "Date :" de l'email, telle qu'écrite
    lignes: list[LigneExtraite]
