"""Les fichiers du dossier odoo/ doivent rester cohérents avec le reste du dépôt.

Si le catalogue, les clients ou les colonnes de l'import changent sans que
odoo/ soit régénéré, l'import des commandes échouerait dans Odoo : ces tests
le signalent avant.
"""

import csv
from pathlib import Path

from src.main import traiter

RACINE = Path(__file__).parent.parent


def lire(chemin: Path) -> list[dict]:
    with open(chemin, newline="", encoding="utf-8-sig") as fichier:
        return list(csv.DictReader(fichier))


def test_les_fichiers_odoo_contiennent_tous_les_clients_et_tous_les_produits(catalogue, clients):
    clients_odoo = lire(RACINE / "odoo" / "clients.csv")
    produits_odoo = lire(RACINE / "odoo" / "produits.csv")

    assert [(c["ref"], c["name"], c["zip"]) for c in clients_odoo] == [
        (c["code_client"], c["nom"], c["code_postal"]) for c in clients]
    assert [(p["default_code"], p["barcode"], p["list_price"]) for p in produits_odoo] == [
        (p["reference"], p["ean"], p["prix_tarif_ht"]) for p in catalogue]


def test_les_identifiants_externes_sont_uniques_et_sans_caractere_risque():
    for fichier in ["clients.csv", "produits.csv"]:
        identifiants = [ligne["id"] for ligne in lire(RACINE / "odoo" / fichier)]
        assert len(identifiants) == len(set(identifiants))
        for identifiant in identifiants:
            assert identifiant.replace("_", "").isalnum(), identifiant


def test_l_import_des_commandes_ne_cite_que_des_clients_et_produits_presents_dans_odoo(
    tmp_path, catalogue, clients, regles, colonnes_odoo
):
    traiter(RACINE / "data" / "inbox", RACINE / "data" / "extractions", tmp_path,
            catalogue, clients, regles, colonnes_odoo)
    commandes = lire(tmp_path / "import_odoo.csv")

    identifiants_clients = {c["id"] for c in lire(RACINE / "odoo" / "clients.csv")}
    references_produits = {p["default_code"] for p in lire(RACINE / "odoo" / "produits.csv")}

    for ligne in commandes:
        if ligne["partner_id/id"]:
            assert ligne["partner_id/id"] in identifiants_clients
        assert ligne["order_line/product_id"] in references_produits


# --- Deux défauts trouvés pendant le test dans une vraie base Odoo ----------

BOM = b"\xef\xbb\xbf"  # la marque UTF-8 en tête de fichier


def test_les_fichiers_importes_dans_odoo_commencent_par_la_marque_bom():
    # Sans elle, Odoo a affiché « MarchÃ© » au lieu de « Marché ».
    for chemin in [
        RACINE / "odoo" / "clients.csv",
        RACINE / "odoo" / "produits.csv",
        RACINE / "sorties" / "import_odoo.csv",
    ]:
        assert chemin.read_bytes().startswith(BOM), chemin.name


def test_le_fichier_clients_n_a_pas_de_colonne_is_company():
    # Cette colonne n'est pas importable dans la version d'Odoo testée :
    # Odoo la reliait au champ « Société » et l'import échouait.
    titres = list(lire(RACINE / "odoo" / "clients.csv")[0])
    assert titres == ["id", "name", "ref", "zip", "city", "country_id/id"]
