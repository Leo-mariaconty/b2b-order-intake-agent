"""Clé de contrôle des codes-barres EAN-13.

Un EAN-13 a 13 chiffres. Le 13e est une clé calculée à partir des 12 premiers.
Si quelqu'un se trompe d'un chiffre en recopiant le code, la clé ne tombe plus
juste : c'est ce qui nous permet de repérer une faute de frappe.
"""


def calculer_cle_ean13(douze_chiffres: str) -> int:
    """Calcule la clé de contrôle à partir des 12 premiers chiffres.

    Règle officielle : on additionne les chiffres en multipliant par 1 ceux en
    position impaire (1er, 3e, 5e...) et par 3 ceux en position paire. La clé
    est ce qu'il faut ajouter à cette somme pour atteindre la dizaine suivante.
    """
    if len(douze_chiffres) != 12 or not douze_chiffres.isdigit():
        raise ValueError("Il faut exactement 12 chiffres pour calculer la clé.")

    somme = 0
    for position, chiffre in enumerate(douze_chiffres):
        poids = 1 if position % 2 == 0 else 3
        somme += int(chiffre) * poids

    return (10 - somme % 10) % 10


def ean13_est_valide(ean: str) -> bool:
    """Vrai si le code a 13 chiffres et que le dernier est la bonne clé."""
    if len(ean) != 13 or not ean.isdigit():
        return False
    return calculer_cle_ean13(ean[:12]) == int(ean[12])
