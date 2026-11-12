"""Données communes à tous les tests."""

from pathlib import Path

import pytest

from src.referentiel import charger_catalogue, charger_clients
from src.regles import Regles

RACINE = Path(__file__).parent.parent


@pytest.fixture
def catalogue():
    return charger_catalogue(RACINE / "data" / "catalogue.csv")


@pytest.fixture
def clients():
    return charger_clients(RACINE / "data" / "clients.csv")


@pytest.fixture
def regles():
    # Les tests utilisent des règles fixes, écrites ici, et non regles.yaml :
    # si l'ADV change un plafond, les tests ne doivent pas se mettre à échouer.
    return Regles(
        plafond_quantite_par_ligne=100,
        colisage_obligatoire=True,
        unites_acceptees=["unité", "unités", "pièce", "pièces"],
        seuil_ressemblance=0.8,
    )
