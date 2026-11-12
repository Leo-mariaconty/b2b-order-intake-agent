"""Test de bout en bout : des emails jusqu'aux fichiers de sortie.

Le premier test rejoue le pipeline sur les 5 emails du dépôt, à partir des
extractions réelles du skill, et compare le résultat à la vérité terrain de
data/attendu/. Les suivants vérifient qu'aucun email n'est perdu quand
l'extraction manque ou est abîmée.
"""

import csv
import json
import shutil
from pathlib import Path

from src.main import traiter
from src.resultats import CommandeControlee

RACINE = Path(__file__).parent.parent
DATA = RACINE / "data"


def resume(commande: CommandeControlee) -> dict:
    """Met une commande contrôlée sous la même forme que les fichiers attendu/."""
    return {
        "email_source": commande.email_source,
        "destination": "import_odoo" if commande.est_valide() else "exceptions",
        "client": commande.client["code_client"] if commande.client else None,
        "exceptions_commande": [
            {"controle": e.controle, "suggestion": e.suggestion} for e in commande.exceptions_commande
        ],
        "lignes": [
            {
                "ligne": ligne.numero,
                "produit": ligne.produit["reference"] if ligne.produit else None,
                "quantite": ligne.quantite,
                "exceptions": [{"controle": e.controle, "suggestion": e.suggestion} for e in ligne.exceptions],
            }
            for ligne in commande.lignes
        ],
    }


def sans_les_pourquoi(attendu: dict) -> dict:
    """Retire les explications en clair, qui ne sont pas comparées."""
    for exception in attendu["exceptions_commande"]:
        del exception["pourquoi"]
    for ligne in attendu["lignes"]:
        for exception in ligne["exceptions"]:
            del exception["pourquoi"]
    return attendu


def lire_csv(chemin, encodage="utf-8-sig"):
    with open(chemin, newline="", encoding=encodage) as fichier:
        return list(csv.DictReader(fichier))


def test_les_5_emails_donnent_le_resultat_attendu(tmp_path, catalogue, clients, regles, colonnes_odoo):
    commandes = traiter(DATA / "inbox", DATA / "extractions", tmp_path, catalogue, clients, regles, colonnes_odoo)

    assert len(commandes) == 5
    for commande in commandes:
        fichier_attendu = DATA / "attendu" / (Path(commande.email_source).stem + ".json")
        attendu = sans_les_pourquoi(json.loads(fichier_attendu.read_text(encoding="utf-8")))
        assert resume(commande) == attendu, commande.email_source

    # Les fichiers écrits disent la même chose que les commandes contrôlées
    import_odoo = lire_csv(tmp_path / "import_odoo.csv")
    assert len(import_odoo) == 7  # 3 lignes (email 1) + 4 lignes (email 5)
    assert [l["partner_id/id"] for l in import_odoo if l["partner_id/id"]] == [
        "client_C1003", "client_C1007"]

    exceptions = lire_csv(tmp_path / "exceptions.csv", "utf-8-sig")
    assert {l["email_source"] for l in exceptions} == {
        "02_centre_texte_flou.txt", "03_halle_tableau_html.html", "04_saint_roch_tableau_erreurs.txt"}

    assert (tmp_path / "rapport.md").exists()


def test_aucun_email_n_est_perdu_quand_l_extraction_manque_ou_est_abimee(
    tmp_path, catalogue, clients, regles, colonnes_odoo
):
    inbox = tmp_path / "inbox"
    extractions = tmp_path / "extractions"
    sorties = tmp_path / "sorties"
    inbox.mkdir()
    extractions.mkdir()

    # Email 1 : normal, avec son extraction réelle
    shutil.copy(DATA / "inbox" / "01_tilleuls_texte_propre.txt", inbox)
    shutil.copy(DATA / "extractions" / "01_tilleuls_texte_propre.json", extractions)
    # Email 2 : le skill n'a rien écrit
    (inbox / "20_sans_extraction.txt").write_text("Bonjour, une commande.", encoding="utf-8")
    # Email 3 : le JSON est abîmé
    (inbox / "21_json_abime.txt").write_text("Bonjour, une commande.", encoding="utf-8")
    (extractions / "21_json_abime.json").write_text('{"email_source": ', encoding="utf-8")
    # Email 4 : la pièce jointe était un PDF vide, le skill l'a signalé
    (inbox / "22_pdf_vide.txt").write_text("Voir le bon de commande joint.", encoding="utf-8")
    (extractions / "22_pdf_vide.json").write_text(
        json.dumps({
            "email_source": "22_pdf_vide.txt", "lisible": False, "motif_illisible": "PDF vide",
            "client": {"code_client": None, "nom": None, "code_postal": None, "ville": None},
            "reference_commande": None, "date_email": None, "lignes": [],
        }),
        encoding="utf-8",
    )

    commandes = traiter(inbox, extractions, sorties, catalogue, clients, regles, colonnes_odoo)

    assert len(commandes) == 4
    import_odoo = lire_csv(sorties / "import_odoo.csv")
    exceptions = lire_csv(sorties / "exceptions.csv", "utf-8-sig")

    assert len(import_odoo) == 3  # les 3 lignes de l'email 1
    emails_en_exception = {l["email_source"]: l for l in exceptions}
    assert set(emails_en_exception) == {"20_sans_extraction.txt", "21_json_abime.txt", "22_pdf_vide.txt"}
    for ligne in exceptions:
        assert ligne["controle"] == "extraction"
        assert ligne["raison"].startswith("Extraction illisible.")
    assert "PDF vide" in emails_en_exception["22_pdf_vide.txt"]["raison"]


def test_un_dossier_d_emails_vide_ne_fait_pas_planter_le_script(
    tmp_path, catalogue, clients, regles, colonnes_odoo
):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    commandes = traiter(inbox, tmp_path / "extractions", tmp_path / "sorties", catalogue, clients, regles, colonnes_odoo)
    assert commandes == []
    assert (tmp_path / "sorties" / "import_odoo.csv").exists()
