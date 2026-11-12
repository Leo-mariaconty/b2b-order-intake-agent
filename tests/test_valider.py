import json
from pathlib import Path

from src.schema import Extraction
from src.valider import valider_extraction

RACINE = Path(__file__).parent.parent
NOM_EMAIL = "10_test.txt"


def extraction_correcte() -> dict:
    return {
        "email_source": NOM_EMAIL,
        "lisible": True,
        "motif_illisible": None,
        "client": {"code_client": "C1003", "nom": None, "code_postal": None, "ville": None},
        "reference_commande": None,
        "date_email": "03/11/2026 09:12",
        "lignes": [
            {
                "texte_source": "12 x Crème mains",
                "reference": None,
                "ean": "2055501001023",
                "libelle": "Crème mains",
                "quantite": "12",
                "unite": None,
            }
        ],
    }


def ecrire(dossier: Path, contenu) -> None:
    texte = contenu if isinstance(contenu, str) else json.dumps(contenu)
    (dossier / "10_test.json").write_text(texte, encoding="utf-8")


def test_extraction_correcte(tmp_path):
    ecrire(tmp_path, extraction_correcte())
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert raison is None
    assert extraction.lignes[0].quantite == "12"


def test_quantite_ecrite_en_nombre_est_convertie_en_texte(tmp_path):
    contenu = extraction_correcte()
    contenu["lignes"][0]["quantite"] = 12
    ecrire(tmp_path, contenu)
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert raison is None
    assert extraction.lignes[0].quantite == "12"


def test_json_absent(tmp_path):
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert extraction is None
    assert "Aucun fichier d'extraction" in raison


def test_json_mal_forme(tmp_path):
    ecrire(tmp_path, "{ ceci n'est pas du JSON")
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert extraction is None
    assert "n'est pas un JSON lisible" in raison


def test_champ_manquant(tmp_path):
    contenu = extraction_correcte()
    del contenu["lignes"][0]["ean"]
    ecrire(tmp_path, contenu)
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert extraction is None
    assert "lignes.0.ean" in raison


def test_champ_en_trop(tmp_path):
    contenu = extraction_correcte()
    contenu["lignes"][0]["commentaire"] = "je pense que c'est le produit VB-102"
    ecrire(tmp_path, contenu)
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert extraction is None
    assert "ne respecte pas le format" in raison


def test_json_qui_ne_parle_pas_du_bon_email(tmp_path):
    contenu = extraction_correcte()
    contenu["email_source"] = "autre_email.txt"
    ecrire(tmp_path, contenu)
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert extraction is None
    assert "autre_email.txt" in raison


def test_email_signale_illisible_par_exemple_pdf_vide(tmp_path):
    contenu = extraction_correcte()
    contenu.update(lisible=False, motif_illisible="PDF vide", lignes=[])
    ecrire(tmp_path, contenu)
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert extraction is None
    assert "PDF vide" in raison


def test_aucune_ligne_trouvee(tmp_path):
    contenu = extraction_correcte()
    contenu["lignes"] = []
    ecrire(tmp_path, contenu)
    extraction, raison = valider_extraction(NOM_EMAIL, tmp_path)
    assert extraction is None
    assert "Aucune ligne de commande" in raison


def test_exemple_du_skill_respecte_le_schema():
    # Garde-fou : si on change le schéma sans mettre à jour l'exemple donné au
    # LLM (ou l'inverse), ce test échoue.
    chemin = RACINE / ".claude" / "skills" / "traiter-commandes" / "exemple.json"
    Extraction.model_validate(json.loads(chemin.read_text(encoding="utf-8")))
