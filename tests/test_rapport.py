from src.rapport import ecrire_rapport
from tests.fabrique import commande_avec_une_ligne_en_exception, commande_valide


def test_rapport_compte_les_commandes_les_lignes_et_les_motifs(tmp_path):
    chemin = tmp_path / "rapport.md"
    ecrire_rapport([commande_valide("a.txt"), commande_avec_une_ligne_en_exception("b.txt")], chemin)
    texte = chemin.read_text(encoding="utf-8")

    assert "Emails traités : 2" in texte
    assert "Lignes de commande extraites : 4" in texte
    assert "Commandes passées sans intervention : 1 sur 2 (50 %)" in texte
    assert "Lignes passées sans intervention : 2 sur 4 (50 %)" in texte
    assert "| Quantité refusée | 1 |" in texte
    assert "| b.txt | 2 | Exceptions | 1 |" in texte


def test_rapport_sans_aucun_email(tmp_path):
    chemin = tmp_path / "rapport.md"
    ecrire_rapport([], chemin)
    texte = chemin.read_text(encoding="utf-8")
    assert "Emails traités : 0" in texte
    assert "sans objet" in texte
