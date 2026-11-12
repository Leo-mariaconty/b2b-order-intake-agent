"""Vérifie que les données de démonstration respectent le cahier des charges."""

from pathlib import Path

from src.ean import ean13_est_valide
from src.referentiel import charger_catalogue, charger_clients

DATA = Path(__file__).parent.parent / "data"


def test_catalogue_12_produits_aux_ean_valides_et_uniques():
    catalogue = charger_catalogue(DATA / "catalogue.csv")
    assert len(catalogue) == 12
    for produit in catalogue:
        assert ean13_est_valide(produit["ean"]), produit["reference"]
        assert produit["colisage"] > 0
    assert len({p["ean"] for p in catalogue}) == 12
    assert len({p["reference"] for p in catalogue}) == 12


def test_clients_8_pharmacies_dont_deux_homonymes():
    clients = charger_clients(DATA / "clients.csv")
    assert len(clients) == 8
    assert len({c["code_client"] for c in clients}) == 8
    homonymes = [c for c in clients if c["nom"] == "Pharmacie du Centre"]
    assert len(homonymes) == 2
    assert homonymes[0]["ville"] != homonymes[1]["ville"]
