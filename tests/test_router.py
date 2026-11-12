import csv
import pytest

from src.resultats import CommandeControlee, ExceptionControle, LigneControlee
from src.router import ColonnesOdoo, ecrire_exceptions, ecrire_import_odoo, router
from tests.fabrique import commande_avec_une_ligne_en_exception, commande_valide

def lire_csv(chemin, encodage="utf-8"):
    with open(chemin, newline="", encoding=encodage) as fichier:
        return list(csv.reader(fichier))


# --- Routage ----------------------------------------------------------------


def test_une_commande_valide_va_a_l_import():
    valides, en_exception = router([commande_valide()])
    assert len(valides) == 1 and en_exception == []


def test_une_seule_ligne_en_exception_envoie_toute_la_commande_en_exception():
    valides, en_exception = router([commande_avec_une_ligne_en_exception()])
    assert valides == []
    assert len(en_exception[0].lignes) == 2  # la commande n'est pas coupée en deux


def test_une_exception_sur_le_client_envoie_la_commande_en_exception():
    commande = commande_valide()
    commande.client = None
    commande.exceptions_commande.append(ExceptionControle("client", "Client inconnu."))
    valides, en_exception = router([commande])
    assert valides == [] and len(en_exception) == 1


def test_chaque_commande_va_a_un_seul_endroit():
    commandes = [commande_valide("a.txt"), commande_avec_une_ligne_en_exception("b.txt")]
    valides, en_exception = router(commandes)
    assert [c.email_source for c in valides] == ["a.txt"]
    assert [c.email_source for c in en_exception] == ["b.txt"]


# --- CSV Odoo ---------------------------------------------------------------


def test_csv_odoo_champs_de_commande_sur_la_premiere_ligne_seulement(tmp_path, colonnes_odoo):
    chemin = tmp_path / "import_odoo.csv"
    ecrire_import_odoo([commande_valide("a.txt"), commande_valide("c.txt")], chemin, colonnes_odoo)
    lignes = lire_csv(chemin)

    assert lignes[0] == [
        "Customer/External ID", "Customer Reference", "Order Date",
        "Order Lines/Product Template", "Order Lines/Quantity", "Order Lines/Unit Price",
    ]
    assert lignes[1] == ["client_C1003", "CDE-1", "2026-11-03 09:12:00",
                         "[VB-102] Crème mains réparatrice 75 ml", "12", "4.20"]
    assert lignes[2] == ["", "", "", "[VB-104] Gel douche surgras 400 ml", "6", "5.90"]
    # la deuxième commande recommence avec ses champs de commande remplis
    assert lignes[3][0] == "client_C1003"
    assert len(lignes) == 5


def test_csv_odoo_sans_commande_contient_seulement_les_titres(tmp_path, colonnes_odoo):
    chemin = tmp_path / "import_odoo.csv"
    ecrire_import_odoo([], chemin, colonnes_odoo)
    assert len(lire_csv(chemin)) == 1


def test_csv_odoo_les_colonnes_se_changent_dans_le_fichier_de_reglage(tmp_path):
    colonnes = ColonnesOdoo(
        separateur=";",
        format_date="%d/%m/%Y",
        colonnes_commande={"Client": "{nom_client}", "Date": "{date_commande}"},
        colonnes_ligne={"Code-barres": "{ean}", "Qté": "{quantite}"},
    )
    chemin = tmp_path / "import_odoo.csv"
    ecrire_import_odoo([commande_valide()], chemin, colonnes)
    texte = chemin.read_text(encoding="utf-8").splitlines()
    assert texte[0] == "Client;Date;Code-barres;Qté"
    assert texte[1] == "Pharmacie des Tilleuls;03/11/2026;2055501001023;12"


def test_csv_odoo_un_mot_inconnu_dans_le_reglage_donne_une_erreur_claire(tmp_path):
    colonnes = ColonnesOdoo(
        separateur=",", format_date="%Y-%m-%d",
        colonnes_commande={"Client": "{nom_du_client}"}, colonnes_ligne={"Qté": "{quantite}"},
    )
    with pytest.raises(ValueError, match="nom_du_client"):
        ecrire_import_odoo([commande_valide()], tmp_path / "import_odoo.csv", colonnes)


# --- CSV des exceptions -----------------------------------------------------


def test_exceptions_contient_toutes_les_lignes_de_la_commande(tmp_path, catalogue, clients):
    chemin = tmp_path / "exceptions.csv"
    ecrire_exceptions([commande_avec_une_ligne_en_exception()], chemin, catalogue, clients)
    lignes = lire_csv(chemin, "utf-8-sig")

    assert lignes[0][0] == "email_source"
    # ligne 1 : correcte, mais retenue avec le reste de la commande
    assert lignes[1][:6] == ["b.txt", "1", "12 x crème", "VB-102", "12", "en attente"]
    # ligne 2 : l'exception, sa raison et la suggestion
    assert lignes[2][5:] == ["à traiter", "quantite",
                             "La quantité 10 n'est pas un multiple du colisage (6).", "6 ou 12"]
    assert len(lignes) == 3


def test_exceptions_suggestions_avec_le_nom_a_cote_du_code(tmp_path, catalogue, clients):
    commande = CommandeControlee(
        email_source="c.txt",
        exceptions_commande=[ExceptionControle("client", "Deux homonymes.", ["C1001", "C1002"])],
        lignes=[LigneControlee(1, "du déo", None, 2, [
            ExceptionControle("reference", "Aucun code produit.", ["VB-105", "VB-106"])])],
    )
    chemin = tmp_path / "exceptions.csv"
    ecrire_exceptions([commande], chemin, catalogue, clients)
    lignes = lire_csv(chemin, "utf-8-sig")

    assert lignes[1][1] == "commande entière"
    assert lignes[1][8] == ("C1001 Pharmacie du Centre (31990 Valbrune-sur-Orve) ; "
                            "C1002 Pharmacie du Centre (69990 Montclar-le-Lac)")
    assert lignes[2][8] == ("VB-105 Déodorant bille douceur 50 ml ; "
                            "VB-106 Déodorant spray fraîcheur 100 ml")
