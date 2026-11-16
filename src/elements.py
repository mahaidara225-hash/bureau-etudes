"""
elements.py
-----------
Structures de données du projet (niveaux, poteaux) et chargement /
sauvegarde du projet au format JSON.

Réutilisé par : charges.py, predimensionnement.py, devis.py, main.py
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any

TYPES_POTEAUX = ("angle", "rive", "central")


@dataclass
class Niveau:
    nom: str
    hauteur_m: float
    charge_permanente_kN_m2: float
    charge_exploitation_kN_m2: float


@dataclass
class DonneesPoteau:
    type: str
    surface_influence_m2: float
    section_cm: float = 20.0

    def __post_init__(self) -> None:
        if self.type not in TYPES_POTEAUX:
            raise ValueError(
                f"Type de poteau inconnu : '{self.type}'. "
                f"Valeurs attendues : {TYPES_POTEAUX}"
            )


@dataclass
class Projet:
    nom_projet: str
    description: str = ""
    niveaux: List[Niveau] = field(default_factory=list)
    poteaux: List[DonneesPoteau] = field(default_factory=list)
    resultats: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Chargement / sauvegarde
    # ------------------------------------------------------------------
    @classmethod
    def charger(cls, chemin: str | Path) -> "Projet":
        chemin = Path(chemin)
        if not chemin.exists():
            raise FileNotFoundError(f"Fichier projet introuvable : {chemin}")
        data = json.loads(chemin.read_text(encoding="utf-8"))
        niveaux = [Niveau(**n) for n in data.get("niveaux", [])]
        poteaux = [DonneesPoteau(**p) for p in data.get("poteaux", [])]
        return cls(
            nom_projet=data.get("nom_projet", "Projet sans nom"),
            description=data.get("description", ""),
            niveaux=niveaux,
            poteaux=poteaux,
            resultats=data.get("resultats", {}),
        )

    def sauvegarder(self, chemin: str | Path) -> None:
        chemin = Path(chemin)
        data = {
            "nom_projet": self.nom_projet,
            "description": self.description,
            "niveaux": [asdict(n) for n in self.niveaux],
            "poteaux": [asdict(p) for p in self.poteaux],
            "resultats": self.resultats,
        }
        chemin.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------
    def hauteur_totale_m(self) -> float:
        return sum(n.hauteur_m for n in self.niveaux)

    def poteau_par_type(self, type_: str) -> DonneesPoteau | None:
        for p in self.poteaux:
            if p.type == type_:
                return p
        return None


def charger_materiaux(chemin: str | Path) -> dict:
    """Charge les hypothèses béton / sol / acier depuis materiaux.json."""
    chemin = Path(chemin)
    return json.loads(chemin.read_text(encoding="utf-8"))
