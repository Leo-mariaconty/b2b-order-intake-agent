"""Étape 2 : les trois contrôles métier.

Chaque contrôle est une fonction pure : elle reçoit des données, renvoie un
résultat, et ne touche à rien d'autre (pas de fichier, pas d'affichage). On peut
donc la tester seule, avec un cas qui passe et un cas qui échoue.

Chaque contrôle renvoie deux valeurs : ce qu'il a trouvé, et une exception.
Quand tout va bien l'exception vaut None.

Un quatrième contrôle, plus technique, vérifie que la date de l'email est
lisible : Odoo refuse une commande sans date.
"""

from datetime import datetime

from src.ean import ean13_est_valide
from src.regles import Regles
from src.ressemblance import mots_utiles, suggerer_produits
from src.resultats import CommandeControlee, ExceptionControle, LigneControlee
from src.schema import ClientExtrait, Extraction, LigneExtraite


# --- Contrôle a : la référence produit -------------------------------------


def controler_reference(
    ligne: LigneExtraite, catalogue: list[dict], regles: Regles
) -> tuple[dict | None, ExceptionControle | None]:
    """Le produit doit être désigné par un EAN ou une référence interne exacte.

    Un libellé seul ne suffit jamais : il sert seulement à proposer des
    candidats dans l'exception.
    """
    produit_par_ean = chercher(catalogue, "ean", ligne.ean)
    produit_par_reference = chercher(catalogue, "reference", ligne.reference)

    if not ligne.ean and not ligne.reference:
        raison = "L'email ne donne aucun code produit (ni code-barres, ni référence)."
    elif ligne.ean and produit_par_ean is None:
        if ean13_est_valide(ligne.ean.strip()):
            raison = f"Le code-barres {ligne.ean} n'existe pas dans notre catalogue."
        else:
            raison = (
                f"Le code-barres {ligne.ean} n'est pas un code valide : "
                "il contient probablement une faute de frappe."
            )
    elif ligne.reference and produit_par_reference is None:
        raison = f"La référence {ligne.reference} n'existe pas dans notre catalogue."
    elif produit_par_ean and produit_par_reference and produit_par_ean != produit_par_reference:
        raison = (
            f"Le code-barres {ligne.ean} et la référence {ligne.reference} "
            "désignent deux produits différents."
        )
    else:
        return produit_par_ean or produit_par_reference, None

    suggestion = suggerer_produits(ligne.libelle, catalogue, regles.seuil_ressemblance)
    return None, ExceptionControle("reference", raison, suggestion)


def chercher(liste: list[dict], colonne: str, valeur: str | None) -> dict | None:
    """Renvoie la fiche dont la colonne vaut exactement la valeur, sinon None."""
    if not valeur:
        return None
    for fiche in liste:
        if fiche[colonne] == valeur.strip():
            return fiche
    return None


# --- Contrôle b : le client ------------------------------------------------


def controler_client(
    client: ClientExtrait, clients: list[dict]
) -> tuple[dict | None, ExceptionControle | None]:
    """La pharmacie doit être identifiée sans doute possible.

    Deux façons acceptées : le code client, ou le nom accompagné du code postal.
    """
    if client.code_client:
        trouve = chercher(clients, "code_client", client.code_client)
        if trouve:
            return trouve, None
        raison = f"Le code client {client.code_client} n'existe pas dans notre fichier clients."
        return None, ExceptionControle("client", raison, codes_des_homonymes(client.nom, clients))

    if not client.nom:
        raison = "L'email ne donne ni code client ni nom de pharmacie."
        return None, ExceptionControle("client", raison)

    homonymes = [c for c in clients if meme_nom(c["nom"], client.nom)]
    codes = [c["code_client"] for c in homonymes]

    if client.code_postal:
        au_bon_code_postal = [c for c in homonymes if c["code_postal"] == client.code_postal.strip()]
        if len(au_bon_code_postal) == 1:
            return au_bon_code_postal[0], None
        raison = f"Aucune pharmacie « {client.nom} » au code postal {client.code_postal} dans notre fichier clients."
    elif len(homonymes) >= 2:
        villes = ", ".join(c["ville"] for c in homonymes)
        raison = (
            f"{len(homonymes)} pharmacies s'appellent « {client.nom} » ({villes}) "
            "et l'email ne donne ni code client ni code postal."
        )
    elif len(homonymes) == 1:
        raison = (
            f"L'email donne seulement le nom « {client.nom} », sans code client "
            "ni code postal : identité à confirmer."
        )
    else:
        raison = f"Aucune pharmacie « {client.nom} » dans notre fichier clients."

    return None, ExceptionControle("client", raison, codes)


def meme_nom(nom_a: str, nom_b: str) -> bool:
    """Compare deux noms sans tenir compte des majuscules, accents et petits mots."""
    return mots_utiles(nom_a) == mots_utiles(nom_b)


def codes_des_homonymes(nom: str | None, clients: list[dict]) -> list[str]:
    if not nom:
        return []
    return [c["code_client"] for c in clients if meme_nom(c["nom"], nom)]


# --- Contrôle c : la quantité ----------------------------------------------


def controler_quantite(
    ligne: LigneExtraite, produit: dict | None, regles: Regles
) -> tuple[int | None, ExceptionControle | None]:
    """La quantité doit être un entier positif, en unités, sous le plafond, et
    multiple du colisage. Renvoie la quantité lue même quand elle est refusée,
    pour que l'humain la voie dans l'exception."""
    texte = (ligne.quantite or "").strip()

    if not texte.isdecimal() or int(texte) == 0:
        ecrit = f"« {texte} »" if texte else "absente"
        raison = f"La quantité ({ecrit}) n'est pas un nombre entier positif."
        return None, ExceptionControle("quantite", raison)

    quantite = int(texte)

    if ligne.unite and ligne.unite.strip().lower() not in regles.unites_acceptees:
        raison = (
            f"La quantité est donnée en « {ligne.unite} » : "
            "le nombre d'unités n'est pas écrit dans l'email."
        )
        return quantite, ExceptionControle("quantite", raison)

    if quantite > regles.plafond_quantite_par_ligne:
        raison = (
            f"La quantité {quantite} dépasse le maximum accepté par ligne "
            f"({regles.plafond_quantite_par_ligne}) : erreur de saisie possible."
        )
        return quantite, ExceptionControle("quantite", raison)

    # Sans produit reconnu, on ne connaît pas le colisage : rien à vérifier ici,
    # la ligne est déjà en exception sur la référence.
    if regles.colisage_obligatoire and produit is not None:
        colisage = produit["colisage"]
        if quantite % colisage != 0:
            en_dessous = quantite - quantite % colisage
            au_dessus = en_dessous + colisage
            proches = [str(q) for q in (en_dessous, au_dessus) if q > 0]
            raison = f"La quantité {quantite} n'est pas un multiple du colisage ({colisage})."
            return quantite, ExceptionControle("quantite", raison, proches)

    return quantite, None


# --- Contrôle technique : la date de l'email --------------------------------

FORMATS_DE_DATE = ["%d/%m/%Y %H:%M", "%d/%m/%Y"]


def controler_date(date_email: str | None) -> tuple[datetime | None, ExceptionControle | None]:
    """La date doit être écrite comme 03/11/2026 09:12 ou 03/11/2026."""
    for format_date in FORMATS_DE_DATE:
        try:
            return datetime.strptime((date_email or "").strip(), format_date), None
        except ValueError:
            continue
    ecrit = f"« {date_email} »" if date_email else "absente"
    raison = f"La date de l'email ({ecrit}) n'a pas pu être comprise."
    return None, ExceptionControle("date", raison)


# --- Assemblage : une commande entière -------------------------------------


def controler_commande(
    extraction: Extraction, catalogue: list[dict], clients: list[dict], regles: Regles
) -> CommandeControlee:
    """Applique les contrôles à une extraction et range les résultats."""
    commande = CommandeControlee(
        email_source=extraction.email_source,
        reference_commande=extraction.reference_commande,
    )

    commande.client, exception_client = controler_client(extraction.client, clients)
    commande.date_commande, exception_date = controler_date(extraction.date_email)
    for exception in (exception_client, exception_date):
        if exception:
            commande.exceptions_commande.append(exception)

    for numero, ligne in enumerate(extraction.lignes, start=1):
        produit, exception_reference = controler_reference(ligne, catalogue, regles)
        quantite, exception_quantite = controler_quantite(ligne, produit, regles)
        exceptions = [e for e in (exception_reference, exception_quantite) if e]
        commande.lignes.append(
            LigneControlee(numero, ligne.texte_source, produit, quantite, exceptions)
        )

    return commande
