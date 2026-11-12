"""Lecture de regles.yaml, le fichier de règles métier tenu par l'équipe ADV."""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class Regles(BaseModel):
    """Les règles attendues et leur type. Une faute dans le YAML est signalée."""

    model_config = ConfigDict(extra="forbid")

    plafond_quantite_par_ligne: int = Field(gt=0)
    colisage_obligatoire: bool
    unites_acceptees: list[str]
    seuil_ressemblance: float = Field(ge=0, le=1)


def charger_regles(chemin: Path) -> Regles:
    contenu = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    return Regles.model_validate(contenu)
