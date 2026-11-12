import pytest

from src.ean import calculer_cle_ean13, ean13_est_valide


def test_cle_calculee_a_la_main():
    # 2 0 5 5 5 0 1 0 0 1 0 1  avec les poids 1 3 1 3 ...
    # 2 + 0 + 5 + 15 + 5 + 0 + 1 + 0 + 0 + 3 + 0 + 3 = 34 -> il manque 6 pour 40
    assert calculer_cle_ean13("205550100101") == 6


def test_cle_zero_quand_la_somme_est_deja_une_dizaine():
    # 12 zéros : somme 0, donc clé 0 (et pas 10)
    assert calculer_cle_ean13("000000000000") == 0


def test_cle_refuse_autre_chose_que_12_chiffres():
    with pytest.raises(ValueError):
        calculer_cle_ean13("12345")
    with pytest.raises(ValueError):
        calculer_cle_ean13("20555010010A")


def test_ean_valide():
    assert ean13_est_valide("2055501001016")


def test_ean_avec_un_chiffre_faux():
    # même code, le 9e chiffre passe de 0 à 8
    assert not ean13_est_valide("2055501081016")


def test_ean_trop_court_ou_avec_lettres():
    assert not ean13_est_valide("205550100101")
    assert not ean13_est_valide("20555010010AB")
    assert not ean13_est_valide("")
