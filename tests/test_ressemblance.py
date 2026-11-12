from src.ressemblance import mots_utiles, score_ressemblance, suggerer_produits


def test_mots_utiles_retire_accents_majuscules_et_petits_mots():
    assert mots_utiles("2 cartons du Déo") == ["cartons", "deo"]


def test_abreviation_reconnue():
    assert score_ressemblance("déo", "Déodorant bille douceur 50 ml") == 1.0


def test_pluriel_reconnu():
    assert score_ressemblance("gels douche", "Gel douche surgras 400 ml") == 1.0


def test_produit_sans_rapport_a_un_score_faible():
    assert score_ressemblance("crème mains", "Savon surgras 100 g") < 0.5


def test_libelle_ambigu_propose_plusieurs_candidats(catalogue):
    assert suggerer_produits("déo", catalogue, seuil=0.8) == ["VB-105", "VB-106"]


def test_libelle_precis_propose_un_seul_candidat(catalogue):
    assert suggerer_produits("crème mains", catalogue, seuil=0.8) == ["VB-102"]


def test_libelle_inconnu_ou_absent_ne_propose_rien(catalogue):
    assert suggerer_produits("parfum d'ambiance", catalogue, seuil=0.8) == []
    assert suggerer_produits(None, catalogue, seuil=0.8) == []
