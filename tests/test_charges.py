"""
tests/test_charges.py
----------------------
Vérifie que predimensionnement.py retrouve EXACTEMENT les valeurs de
contrôle données par l'énoncé (séance 6, §6.3), ainsi que le bon
fonctionnement de base de charges.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from charges import coefficient_degression, descente_de_charges  # noqa: E402
from predimensionnement import (  # noqa: E402
    predimensionner_poteau,
    predimensionner_semelle,
)
from elements import Projet, Niveau, DonneesPoteau  # noqa: E402


# ----------------------------------------------------------------------
# Valeurs de contrôle de l'énoncé
# ----------------------------------------------------------------------
CONTROLE_POTEAUX = {
    "angle":   {"N_ELU_kN": 168.4, "A_min_m2": 0.017, "cote_retenu_cm": 20},
    "rive":    {"N_ELU_kN": 317.8, "A_min_m2": 0.032, "cote_retenu_cm": 20},
    "central": {"N_ELU_kN": 616.6, "A_min_m2": 0.062, "cote_retenu_cm": 25},
}

CONTROLE_SEMELLES = {
    "angle":   {"G_plus_Q_kN": 122.1, "B_min_m": 0.81, "B_retenu_m": 0.85},
    "rive":    {"G_plus_Q_kN": 230.1, "B_min_m": 1.11, "B_retenu_m": 1.15},
    "central": {"G_plus_Q_kN": 446.1, "B_min_m": 1.54, "B_retenu_m": 1.55},
}


def test_predimensionnement_poteaux_valeurs_de_controle():
    for type_, attendu in CONTROLE_POTEAUX.items():
        resultat = predimensionner_poteau(attendu["N_ELU_kN"])
        assert resultat["A_min_m2"] == attendu["A_min_m2"], type_
        assert resultat["cote_retenu_cm"] == attendu["cote_retenu_cm"], type_


def test_predimensionnement_semelles_valeurs_de_controle():
    for type_, attendu in CONTROLE_SEMELLES.items():
        resultat = predimensionner_semelle(attendu["G_plus_Q_kN"])
        assert resultat["B_min_m"] == attendu["B_min_m"], type_
        assert resultat["B_retenu_m"] == attendu["B_retenu_m"], type_


def test_coefficient_degression():
    assert coefficient_degression(1) == 1.0
    assert coefficient_degression(2) == 1.0
    assert round(coefficient_degression(3), 3) == round(6 / 6, 3)


def test_descente_de_charges_structure():
    projet = Projet(
        nom_projet="Projet test",
        niveaux=[
            Niveau("RDC", 3.0, 5.0, 2.0),
            Niveau("Etage 1", 3.0, 5.0, 1.5),
        ],
        poteaux=[
            DonneesPoteau("angle", 6.0),
            DonneesPoteau("rive", 11.3),
            DonneesPoteau("central", 22.6),
        ],
    )
    resultats = descente_de_charges(projet)
    assert set(resultats.keys()) == {"angle", "rive", "central"}
    for r in resultats.values():
        assert r["N_ELU_kN"] > 0
        assert r["G_plus_Q_kN"] > 0
