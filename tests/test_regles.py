from pathlib import Path

import pytest
from pydantic import ValidationError

from src.regles import charger_regles

RACINE = Path(__file__).parent.parent


def test_le_fichier_regles_du_depot_est_lisible():
    regles = charger_regles(RACINE / "regles.yaml")
    assert regles.plafond_quantite_par_ligne > 0


def test_une_valeur_mal_ecrite_arrete_le_script(tmp_path):
    fichier = tmp_path / "regles.yaml"
    fichier.write_text(
        "plafond_quantite_par_ligne: beaucoup\n"
        "colisage_obligatoire: true\n"
        "unites_acceptees: [unité]\n"
        "seuil_ressemblance: 0.8\n",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        charger_regles(fichier)


def test_une_regle_oubliee_arrete_le_script(tmp_path):
    fichier = tmp_path / "regles.yaml"
    fichier.write_text("plafond_quantite_par_ligne: 100\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        charger_regles(fichier)
