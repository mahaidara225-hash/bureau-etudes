"""
predimensionnement.py
----------------------
Prédimensionnement des poteaux (section carrée en béton armé) et des
semelles isolées, à partir des résultats de la descente de charges.

Valeurs de contrôle de l'énoncé (séance 6, §6.3) — ce module doit les
retrouver EXACTEMENT (voir tests/test_charges.py) :

  Poteau    N_ELU (kN)   A_min (m²)   Côté retenu
  Angle        168.4        0.017        20 cm
  Rive         317.8        0.032        20 cm
  Central      616.6        0.062        25 cm

  Semelle    G+Q (kN)    Côté minimal   Côté retenu
  Angle        122.1        0.81 m         0.85 m
  Rive         230.1        1.11 m         1.15 m
  Central      446.1        1.54 m         1.55 m

Formule de la semelle (donnée par l'énoncé) :
    (G + Q + 12.5 x B²) / B² ≤ 200   =>   B ≥ sqrt((G+Q) / 187.5)
Le terme 12.5 kN/m² représente le poids propre de la semelle + le
remblai au-dessus (≈ 0.5 m x 25 kN/m³).
"""
from __future__ import annotations

import math
from typing import Dict

# --- Hypothèses de prédimensionnement -------------------------------
SIGMA_ADM_BETON_MPa = 10.0      # contrainte béton admissible (prédim rapide)
SECTION_MIN_CM = 20.0           # section minimale réglementaire d'un poteau
PAS_POTEAU_CM = 5.0             # on retient un multiple de 5 cm

SIGMA_SOL_KPA = 200.0           # contrainte admissible du sol
TERME_CORRECTIF_KN_M2 = 12.5    # poids semelle + remblai (≈ 0.5 m x 25 kN/m3)
PAS_SEMELLE_M = 0.05            # on retient un multiple de 5 cm


def _arrondi_sup(valeur: float, pas: float) -> float:
    """Arrondit `valeur` au multiple de `pas` immédiatement supérieur."""
    return math.ceil(round(valeur / pas, 6)) * pas


def predimensionner_poteau(N_ELU_kN: float) -> Dict[str, float]:
    """A_min (m²) = N_ELU (kN) / sigma_adm (kPa).

    Le côté minimal est arrondi au centimètre SUPÉRIEUR (dimension
    minimale requise), puis le côté retenu est arrondi au multiple de
    5 cm supérieur, avec un plancher de 20 cm.
    """
    sigma_adm_kPa = SIGMA_ADM_BETON_MPa * 1000.0
    A_min_m2 = N_ELU_kN / sigma_adm_kPa

    cote_min_cm = math.ceil(math.sqrt(A_min_m2) * 100.0)
    cote_retenu_cm = max(_arrondi_sup(cote_min_cm, PAS_POTEAU_CM), SECTION_MIN_CM)

    return {
        "N_ELU_kN": round(N_ELU_kN, 1),
        "A_min_m2": round(A_min_m2, 3),
        "cote_min_cm": cote_min_cm,
        "cote_retenu_cm": cote_retenu_cm,
    }


def predimensionner_semelle(G_plus_Q_kN: float) -> Dict[str, float]:
    """B_min (m) = sqrt((G+Q) / (sigma_sol - terme_correctif)).

    Le côté minimal est arrondi au centimètre le plus proche, puis le
    côté retenu est arrondi au multiple de 5 cm supérieur.
    """
    denominateur = SIGMA_SOL_KPA - TERME_CORRECTIF_KN_M2  # = 187.5
    B_min_m = round(math.sqrt(G_plus_Q_kN / denominateur), 2)
    B_retenu_m = round(_arrondi_sup(B_min_m, PAS_SEMELLE_M), 2)

    return {
        "G_plus_Q_kN": round(G_plus_Q_kN, 1),
        "B_min_m": B_min_m,
        "B_retenu_m": B_retenu_m,
    }


def predimensionner_tout(resultats_charges: dict) -> dict:
    """Applique le prédimensionnement poteau + semelle à chaque type
    (angle, rive, central) à partir des résultats de descente de charges.
    """
    sortie = {}
    for type_poteau, res in resultats_charges.items():
        sortie[type_poteau] = {
            "poteau": predimensionner_poteau(res["N_ELU_kN"]),
            "semelle": predimensionner_semelle(res["G_plus_Q_kN"]),
        }
    return sortie
