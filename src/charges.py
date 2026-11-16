"""
charges.py
----------
Descente de charges (séance 3) : calcule, pour chaque type de poteau
(angle, rive, central), les charges permanentes (G) et d'exploitation (Q)
cumulées en pied, ainsi que l'effort normal à l'ELU (N_ELU).

Méthode
-------
Pour chaque niveau, la charge reprise par un poteau = charge unitaire
(kN/m²) x surface d'influence du poteau (m²). Les charges sont cumulées
du dernier niveau (toiture) vers le pied du bâtiment.

Une dégression forfaitaire des charges d'exploitation est appliquée à
partir du 3ᵉ niveau cumulé (règle simplifiée inspirée de la méthode
Caquot) : coefficient = (3 + n) / (2n) pour n >= 3, et 1.0 pour n <= 2.

Combinaison ELU : N_ELU = 1.35 x G + 1.5 x Q
"""
from __future__ import annotations

from typing import Dict, List

from elements import Projet

COMBINAISON_ELU = {"G": 1.35, "Q": 1.5}


def coefficient_degression(n: int) -> float:
    """Coefficient de dégression des charges d'exploitation.

    n = nombre de niveaux cumulés (toiture comprise).
    """
    if n <= 2:
        return 1.0
    return (3 + n) / (2 * n)


def descente_de_charges(projet: Projet) -> Dict[str, dict]:
    """Calcule G, Q et N_ELU en pied pour chaque type de poteau du projet.

    Retourne un dict :
        {
          "angle":   {"G_kN": ..., "Q_kN": ..., "G_plus_Q_kN": ...,
                      "N_ELU_kN": ..., "details": [...]},
          "rive":    {...},
          "central": {...},
        }
    """
    if not projet.niveaux:
        raise ValueError("Le projet ne contient aucun niveau.")
    if not projet.poteaux:
        raise ValueError("Le projet ne contient aucun poteau.")

    resultats: Dict[str, dict] = {}

    for poteau in projet.poteaux:
        G_cumule = 0.0
        Q_brut_cumule = 0.0
        Q_cumule = 0.0
        details: List[dict] = []

        # On parcourt les niveaux du haut (toiture) vers le bas (pied) :
        # le dernier niveau de la liste projet.niveaux est supposé être
        # le plus haut.
        for i, niveau in enumerate(reversed(projet.niveaux), start=1):
            g_niveau = niveau.charge_permanente_kN_m2 * poteau.surface_influence_m2
            q_niveau = niveau.charge_exploitation_kN_m2 * poteau.surface_influence_m2

            G_cumule += g_niveau
            Q_brut_cumule += q_niveau

            coef = coefficient_degression(i)
            Q_cumule = Q_brut_cumule * coef

            details.append({
                "niveau": niveau.nom,
                "G_niveau_kN": round(g_niveau, 2),
                "Q_niveau_kN": round(q_niveau, 2),
                "coef_degression": round(coef, 3),
                "G_cumule_kN": round(G_cumule, 2),
                "Q_cumule_kN": round(Q_cumule, 2),
            })

        N_ELU = COMBINAISON_ELU["G"] * G_cumule + COMBINAISON_ELU["Q"] * Q_cumule

        resultats[poteau.type] = {
            "G_kN": round(G_cumule, 1),
            "Q_kN": round(Q_cumule, 1),
            "G_plus_Q_kN": round(G_cumule + Q_cumule, 1),
            "N_ELU_kN": round(N_ELU, 1),
            "details": details,
        }

    return resultats
