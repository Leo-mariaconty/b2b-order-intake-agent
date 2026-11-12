"""Ce que produit l'étape de contrôle : des commandes avec leurs exceptions.

Ce sont de simples fiches (dataclasses) que les étapes suivantes relisent.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExceptionControle:
    controle: str  # "extraction", "client", "reference" ou "quantite"
    raison: str  # phrase lisible par une personne de l'ADV
    suggestion: list[str] = field(default_factory=list)  # pistes, jamais appliquées seules


@dataclass
class LigneControlee:
    numero: int  # 1 pour la première ligne de l'email
    texte_source: str  # le passage de l'email, pour que l'humain s'y retrouve
    produit: dict | None  # le produit du catalogue, ou None s'il n'est pas reconnu
    quantite: int | None  # la quantité lue, ou None si ce n'est pas un entier
    exceptions: list[ExceptionControle] = field(default_factory=list)


@dataclass
class CommandeControlee:
    email_source: str
    client: dict | None = None  # le client du fichier clients, ou None
    reference_commande: str | None = None
    date_commande: datetime | None = None  # la date de l'email, une fois comprise
    exceptions_commande: list[ExceptionControle] = field(default_factory=list)
    lignes: list[LigneControlee] = field(default_factory=list)

    def est_valide(self) -> bool:
        """Vrai si aucun contrôle n'a échoué, ni sur la commande ni sur une ligne."""
        if self.exceptions_commande:
            return False
        return all(not ligne.exceptions for ligne in self.lignes)
