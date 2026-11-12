"""Chaque contrôle est testé seul : au moins un cas qui passe, un cas qui échoue."""

from src.controler import (
    controler_client,
    controler_commande,
    controler_quantite,
    controler_reference,
)
from src.schema import ClientExtrait, Extraction, LigneExtraite


def ligne(reference=None, ean=None, libelle=None, quantite="12", unite=None) -> LigneExtraite:
    return LigneExtraite(
        texte_source="ligne de test",
        reference=reference,
        ean=ean,
        libelle=libelle,
        quantite=quantite,
        unite=unite,
    )


def client(code_client=None, nom=None, code_postal=None, ville=None) -> ClientExtrait:
    return ClientExtrait(code_client=code_client, nom=nom, code_postal=code_postal, ville=ville)


# --- Contrôle a : référence -------------------------------------------------


def test_reference_trouvee_par_ean(catalogue, regles):
    produit, exception = controler_reference(ligne(ean="2055501001023"), catalogue, regles)
    assert produit["reference"] == "VB-102"
    assert exception is None


def test_reference_trouvee_par_reference_interne(catalogue, regles):
    produit, exception = controler_reference(ligne(reference="VB-103"), catalogue, regles)
    assert produit["reference"] == "VB-103"
    assert exception is None


def test_reference_et_ean_coherents(catalogue, regles):
    produit, exception = controler_reference(
        ligne(reference="VB-102", ean="2055501001023"), catalogue, regles
    )
    assert produit["reference"] == "VB-102"
    assert exception is None


def test_ean_avec_faute_de_frappe(catalogue, regles):
    produit, exception = controler_reference(
        ligne(ean="2055501001192", libelle="Crème solaire SPF50 visage 50 ml"), catalogue, regles
    )
    assert produit is None
    assert exception.controle == "reference"
    assert "faute de frappe" in exception.raison
    assert exception.suggestion == ["VB-109"]


def test_ean_valide_mais_absent_du_catalogue(catalogue, regles):
    # 2055501009999 a une clé juste, mais ce produit n'existe pas chez nous
    produit, exception = controler_reference(ligne(ean="2055501009999"), catalogue, regles)
    assert produit is None
    assert "n'existe pas dans notre catalogue" in exception.raison


def test_reference_interne_inconnue(catalogue, regles):
    produit, exception = controler_reference(ligne(reference="VB-999"), catalogue, regles)
    assert produit is None
    assert "VB-999" in exception.raison


def test_reference_et_ean_qui_se_contredisent(catalogue, regles):
    produit, exception = controler_reference(
        ligne(reference="VB-101", ean="2055501001023"), catalogue, regles
    )
    assert produit is None
    assert "deux produits différents" in exception.raison


def test_libelle_seul_ne_valide_jamais_meme_s_il_est_exact(catalogue, regles):
    produit, exception = controler_reference(
        ligne(libelle="Crème mains réparatrice 75 ml"), catalogue, regles
    )
    assert produit is None
    assert exception.suggestion == ["VB-102"]


# --- Contrôle b : client ----------------------------------------------------


def test_client_trouve_par_code(clients):
    trouve, exception = controler_client(client(code_client="C1003"), clients)
    assert trouve["nom"] == "Pharmacie des Tilleuls"
    assert exception is None


def test_client_trouve_par_nom_et_code_postal(clients):
    trouve, exception = controler_client(
        client(nom="Pharmacie Saint-Roch", code_postal="13990"), clients
    )
    assert trouve["code_client"] == "C1005"
    assert exception is None


def test_homonymes_departages_par_le_code_postal(clients):
    trouve, exception = controler_client(
        client(nom="pharmacie du centre", code_postal="69990"), clients
    )
    assert trouve["code_client"] == "C1002"
    assert exception is None


def test_homonymes_sans_code_postal(clients):
    trouve, exception = controler_client(client(nom="Pharmacie du Centre"), clients)
    assert trouve is None
    assert exception.controle == "client"
    assert exception.suggestion == ["C1001", "C1002"]


def test_nom_unique_mais_sans_code_postal_reste_a_confirmer(clients):
    trouve, exception = controler_client(client(nom="Pharmacie du Marché"), clients)
    assert trouve is None
    assert "à confirmer" in exception.raison
    assert exception.suggestion == ["C1006"]


def test_code_client_inconnu(clients):
    trouve, exception = controler_client(client(code_client="C9999"), clients)
    assert trouve is None
    assert "C9999" in exception.raison


def test_nom_connu_mais_mauvais_code_postal(clients):
    trouve, exception = controler_client(
        client(nom="Pharmacie Saint-Roch", code_postal="75990"), clients
    )
    assert trouve is None
    assert exception.suggestion == ["C1005"]


def test_ni_code_ni_nom(clients):
    trouve, exception = controler_client(client(), clients)
    assert trouve is None
    assert exception.controle == "client"


# --- Contrôle c : quantité --------------------------------------------------

PRODUIT_COLISAGE_6 = {"reference": "VB-103", "colisage": 6}


def test_quantite_correcte(regles):
    quantite, exception = controler_quantite(ligne(quantite="12"), PRODUIT_COLISAGE_6, regles)
    assert quantite == 12
    assert exception is None


def test_quantite_hors_colisage(regles):
    quantite, exception = controler_quantite(ligne(quantite="10"), PRODUIT_COLISAGE_6, regles)
    assert quantite == 10
    assert exception.controle == "quantite"
    assert exception.suggestion == ["6", "12"]


def test_quantite_hors_colisage_acceptee_si_la_regle_est_desactivee(regles):
    regles.colisage_obligatoire = False
    quantite, exception = controler_quantite(ligne(quantite="10"), PRODUIT_COLISAGE_6, regles)
    assert quantite == 10
    assert exception is None


def test_quantite_au_dessus_du_plafond(regles):
    quantite, exception = controler_quantite(ligne(quantite="120"), PRODUIT_COLISAGE_6, regles)
    assert quantite == 120
    assert "dépasse le maximum" in exception.raison


def test_quantite_egale_au_plafond_acceptee(regles):
    produit_colisage_10 = {"reference": "X", "colisage": 10}
    quantite, exception = controler_quantite(ligne(quantite="100"), produit_colisage_10, regles)
    assert quantite == 100
    assert exception is None


def test_quantite_en_cartons(regles):
    quantite, exception = controler_quantite(
        ligne(quantite="2", unite="cartons"), PRODUIT_COLISAGE_6, regles
    )
    assert quantite == 2
    assert "cartons" in exception.raison


def test_quantite_avec_unite_acceptee(regles):
    quantite, exception = controler_quantite(
        ligne(quantite="6", unite="Unités"), PRODUIT_COLISAGE_6, regles
    )
    assert quantite == 6
    assert exception is None


def test_quantites_qui_ne_sont_pas_des_entiers_positifs(regles):
    for texte in ["0", "-6", "12,5", "une douzaine", "", None]:
        quantite, exception = controler_quantite(ligne(quantite=texte), PRODUIT_COLISAGE_6, regles)
        assert quantite is None, texte
        assert exception.controle == "quantite", texte


def test_sans_produit_reconnu_le_colisage_n_est_pas_verifie(regles):
    quantite, exception = controler_quantite(ligne(quantite="7"), None, regles)
    assert quantite == 7
    assert exception is None


# --- Assemblage -------------------------------------------------------------


def test_commande_entierement_valide(catalogue, clients, regles):
    extraction = Extraction(
        email_source="test.txt",
        lisible=True,
        motif_illisible=None,
        client=client(code_client="C1003"),
        reference_commande="CDE-1",
        date_email="03/11/2026 09:12",
        lignes=[ligne(ean="2055501001023", quantite="12")],
    )
    commande = controler_commande(extraction, catalogue, clients, regles)
    assert commande.est_valide()
    assert commande.client["code_client"] == "C1003"
    assert commande.lignes[0].numero == 1


def test_une_ligne_peut_cumuler_deux_exceptions(catalogue, clients, regles):
    extraction = Extraction(
        email_source="test.txt",
        lisible=True,
        motif_illisible=None,
        client=client(code_client="C1003"),
        reference_commande=None,
        date_email=None,
        lignes=[ligne(libelle="déo", quantite="2", unite="cartons")],
    )
    commande = controler_commande(extraction, catalogue, clients, regles)
    assert not commande.est_valide()
    assert [e.controle for e in commande.lignes[0].exceptions] == ["reference", "quantite"]
