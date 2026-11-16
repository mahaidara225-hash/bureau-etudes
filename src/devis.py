"""
devis.py
--------
Métré (quantités de béton, coffrage, acier) et génération du devis
estimatif à partir du bordereau de prix unitaires (donnees/bordereau.csv).
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List

from elements import Projet

HAUTEUR_SEMELLE_M = 0.5  # hypothèse d'épaisseur de semelle


def calculer_metre(projet: Projet, resultats_predim: dict, materiaux: dict) -> dict:
    """Calcule les quantités (m3 béton, m2 coffrage, kg acier) pour
    l'ensemble des poteaux et semelles du projet.
    """
    ratio_acier = materiaux.get("acier", {}).get("ratio_kg_par_m3_beton", 100)
    hauteur_totale = projet.hauteur_totale_m()

    quantites = {
        "beton_poteaux_m3": 0.0,
        "beton_semelles_m3": 0.0,
        "coffrage_poteaux_m2": 0.0,
        "acier_kg": 0.0,
        "terrassement_m3": 0.0,
        "remblai_m3": 0.0,
        "details_par_type": {},
    }

    for poteau in projet.poteaux:
        predim = resultats_predim.get(poteau.type)
        if predim is None:
            continue

        cote_poteau_m = predim["poteau"]["cote_retenu_cm"] / 100.0
        cote_semelle_m = predim["semelle"]["B_retenu_m"]

        vol_poteau = (cote_poteau_m ** 2) * hauteur_totale
        vol_semelle = (cote_semelle_m ** 2) * HAUTEUR_SEMELLE_M
        coffrage = 4 * cote_poteau_m * hauteur_totale
        vol_fouille = (cote_semelle_m + 0.20) ** 2 * (HAUTEUR_SEMELLE_M + 0.10)
        vol_remblai = max(vol_fouille - vol_semelle, 0.0)

        quantites["beton_poteaux_m3"] += vol_poteau
        quantites["beton_semelles_m3"] += vol_semelle
        quantites["coffrage_poteaux_m2"] += coffrage
        quantites["terrassement_m3"] += vol_fouille
        quantites["remblai_m3"] += vol_remblai

        quantites["details_par_type"][poteau.type] = {
            "cote_poteau_m": round(cote_poteau_m, 2),
            "cote_semelle_m": round(cote_semelle_m, 2),
            "volume_beton_poteau_m3": round(vol_poteau, 3),
            "volume_beton_semelle_m3": round(vol_semelle, 3),
        }

    volume_beton_total = quantites["beton_poteaux_m3"] + quantites["beton_semelles_m3"]
    quantites["acier_kg"] = volume_beton_total * ratio_acier

    for cle in ("beton_poteaux_m3", "beton_semelles_m3", "coffrage_poteaux_m2",
                "acier_kg", "terrassement_m3", "remblai_m3"):
        quantites[cle] = round(quantites[cle], 2)

    return quantites


def charger_bordereau(chemin: str | Path) -> List[dict]:
    chemin = Path(chemin)
    with chemin.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generer_devis(quantites: dict, bordereau: List[dict]) -> dict:
    """Associe les quantités du métré aux prix unitaires du bordereau et
    calcule le total estimatif (en FCFA).
    """
    prix = {ligne["designation"].strip().lower(): ligne for ligne in bordereau}

    correspondances = {
        "beton_poteaux_m3": "beton dose a 350 kg/m3 (poteaux)",
        "beton_semelles_m3": "beton dose a 350 kg/m3 (semelles)",
        "coffrage_poteaux_m2": "coffrage poteaux",
        "acier_kg": "acier ha",
        "terrassement_m3": "terrassement fouilles",
        "remblai_m3": "remblai compacte",
    }

    lignes_devis: List[dict] = []
    total = 0.0

    for cle_quantite, designation in correspondances.items():
        ligne_prix = prix.get(designation)
        quantite = quantites.get(cle_quantite, 0.0)
        if ligne_prix is None or quantite <= 0:
            continue
        prix_unitaire = float(ligne_prix["prix_unitaire_fcfa"])
        montant = quantite * prix_unitaire
        total += montant
        lignes_devis.append({
            "designation": ligne_prix["designation"],
            "unite": ligne_prix["unite"],
            "quantite": round(quantite, 2),
            "prix_unitaire_fcfa": prix_unitaire,
            "montant_fcfa": round(montant, 0),
        })

    main_oeuvre = prix.get("main d'oeuvre")
    if main_oeuvre:
        montant_mo = float(main_oeuvre["prix_unitaire_fcfa"])
        total += montant_mo
        lignes_devis.append({
            "designation": main_oeuvre["designation"],
            "unite": main_oeuvre["unite"],
            "quantite": 1,
            "prix_unitaire_fcfa": montant_mo,
            "montant_fcfa": montant_mo,
        })

    return {"lignes": lignes_devis, "total_fcfa": round(total, 0)}
