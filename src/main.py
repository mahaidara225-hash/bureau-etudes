"""
main.py
-------
Menu console du bureau d'études. Réutilise les séances 1 à 5 :

  1. Saisir ou charger le projet        (S4 — JSON)
  2. Calculer le métré                  (S1 et S5)
  3. Descente de charges                (S3)
  4. Prédimensionner poteaux et semelles (S2 et S3)
  5. Générer le devis                   (S4)
  6. Exporter un rapport                 (S4)
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from elements import Projet, charger_materiaux
from charges import descente_de_charges
from predimensionnement import predimensionner_tout
from devis import calculer_metre, charger_bordereau, generer_devis

BASE_DIR = Path(__file__).resolve().parent.parent
CHEMIN_PROJET = BASE_DIR / "donnees" / "projet.json"
CHEMIN_MATERIAUX = BASE_DIR / "donnees" / "materiaux.json"
CHEMIN_BORDEREAU = BASE_DIR / "donnees" / "bordereau.csv"


# ----------------------------------------------------------------------
# Affichage
# ----------------------------------------------------------------------
def afficher_tableau(titre: str, colonnes: list[str], lignes: list[list]) -> None:
    print(f"\n{titre}")
    largeurs = [max(len(str(colonnes[i])), *(len(str(l[i])) for l in lignes)) + 2
                if lignes else len(str(colonnes[i])) + 2
                for i in range(len(colonnes))]
    entete = "".join(str(c).ljust(largeurs[i]) for i, c in enumerate(colonnes))
    print(entete)
    print("-" * len(entete))
    for ligne in lignes:
        print("".join(str(v).ljust(largeurs[i]) for i, v in enumerate(ligne)))


# ----------------------------------------------------------------------
# Options du menu
# ----------------------------------------------------------------------
def option_charger_projet() -> Projet:
    if CHEMIN_PROJET.exists():
        projet = Projet.charger(CHEMIN_PROJET)
        print(f"Projet chargé : {projet.nom_projet}")
    else:
        print("Aucun projet existant, création d'un nouveau projet.")
        nom = input("Nom du projet : ").strip() or "Nouveau projet"
        projet = Projet(nom_projet=nom)
        projet.sauvegarder(CHEMIN_PROJET)
    return projet


def option_metre(projet: Projet) -> None:
    if "predimensionnement" not in projet.resultats:
        print("⚠ Lancez d'abord l'option 4 (prédimensionnement).")
        return
    materiaux = charger_materiaux(CHEMIN_MATERIAUX)
    quantites = calculer_metre(projet, projet.resultats["predimensionnement"], materiaux)
    projet.resultats["metre"] = quantites
    projet.sauvegarder(CHEMIN_PROJET)

    afficher_tableau(
        "Métré",
        ["Poste", "Quantité"],
        [
            ["Béton poteaux (m3)", quantites["beton_poteaux_m3"]],
            ["Béton semelles (m3)", quantites["beton_semelles_m3"]],
            ["Coffrage poteaux (m2)", quantites["coffrage_poteaux_m2"]],
            ["Acier (kg)", quantites["acier_kg"]],
            ["Terrassement (m3)", quantites["terrassement_m3"]],
            ["Remblai (m3)", quantites["remblai_m3"]],
        ],
    )


def option_descente_de_charges(projet: Projet) -> None:
    resultats = descente_de_charges(projet)
    projet.resultats["charges"] = resultats
    projet.sauvegarder(CHEMIN_PROJET)

    afficher_tableau(
        "Descente de charges",
        ["Poteau", "G (kN)", "Q (kN)", "G+Q (kN)", "N_ELU (kN)"],
        [[t.capitalize(), r["G_kN"], r["Q_kN"], r["G_plus_Q_kN"], r["N_ELU_kN"]]
         for t, r in resultats.items()],
    )


def option_predimensionnement(projet: Projet) -> None:
    if "charges" not in projet.resultats:
        print("⚠ Lancez d'abord l'option 3 (descente de charges).")
        return
    resultats = predimensionner_tout(projet.resultats["charges"])
    projet.resultats["predimensionnement"] = resultats
    projet.sauvegarder(CHEMIN_PROJET)

    afficher_tableau(
        "Prédimensionnement des poteaux",
        ["Poteau", "N_ELU (kN)", "A_min (m2)", "Côté retenu (cm)"],
        [[t.capitalize(), r["poteau"]["N_ELU_kN"], r["poteau"]["A_min_m2"],
          r["poteau"]["cote_retenu_cm"]] for t, r in resultats.items()],
    )
    afficher_tableau(
        "Prédimensionnement des semelles",
        ["Semelle", "G+Q (kN)", "B_min (m)", "B retenu (m)"],
        [[t.capitalize(), r["semelle"]["G_plus_Q_kN"], r["semelle"]["B_min_m"],
          r["semelle"]["B_retenu_m"]] for t, r in resultats.items()],
    )


def option_devis(projet: Projet) -> None:
    if "metre" not in projet.resultats:
        print("⚠ Lancez d'abord l'option 2 (métré).")
        return
    bordereau = charger_bordereau(CHEMIN_BORDEREAU)
    devis = generer_devis(projet.resultats["metre"], bordereau)
    projet.resultats["devis"] = devis
    projet.sauvegarder(CHEMIN_PROJET)

    afficher_tableau(
        "Devis estimatif",
        ["Désignation", "Unité", "Qté", "P.U. (FCFA)", "Montant (FCFA)"],
        [[l["designation"], l["unite"], l["quantite"], l["prix_unitaire_fcfa"],
          l["montant_fcfa"]] for l in devis["lignes"]],
    )
    print(f"\nTOTAL ESTIMATIF : {devis['total_fcfa']:,.0f} FCFA".replace(",", " "))


def option_export_rapport(projet: Projet) -> None:
    requis = ("charges", "predimensionnement", "metre", "devis")
    manquants = [r for r in requis if r not in projet.resultats]
    if manquants:
        print(f"⚠ Options manquantes avant export : {', '.join(manquants)}")
        return

    horodatage = datetime.now().strftime("%Y-%m-%d_%Hh%M")
    chemin_rapport = BASE_DIR / f"rapport_{horodatage}.md"

    lignes = [f"# Rapport — {projet.nom_projet}", f"_Généré le {datetime.now():%d/%m/%Y à %H:%M}_\n"]

    lignes.append("## Descente de charges\n")
    for t, r in projet.resultats["charges"].items():
        lignes.append(f"- **{t.capitalize()}** : G={r['G_kN']} kN, Q={r['Q_kN']} kN, "
                       f"N_ELU={r['N_ELU_kN']} kN")

    lignes.append("\n## Prédimensionnement\n")
    for t, r in projet.resultats["predimensionnement"].items():
        lignes.append(f"- **{t.capitalize()}** : poteau {r['poteau']['cote_retenu_cm']} cm "
                       f"| semelle {r['semelle']['B_retenu_m']} m")

    lignes.append("\n## Métré\n")
    for cle, val in projet.resultats["metre"].items():
        if cle != "details_par_type":
            lignes.append(f"- {cle} : {val}")

    lignes.append(f"\n## Devis\n\n**Total estimatif : {projet.resultats['devis']['total_fcfa']:,.0f} FCFA**".replace(",", " "))

    chemin_rapport.write_text("\n".join(lignes), encoding="utf-8")
    print(f"✔ Rapport exporté : {chemin_rapport}")


# ----------------------------------------------------------------------
# Boucle principale
# ----------------------------------------------------------------------
def menu() -> None:
    projet: Projet | None = None
    while True:
        print("\n" + "=" * 50)
        print(" BUREAU D'ÉTUDES — MENU PRINCIPAL")
        print("=" * 50)
        print("1. Saisir ou charger le projet")
        print("2. Calculer le métré")
        print("3. Descente de charges")
        print("4. Prédimensionner poteaux et semelles")
        print("5. Générer le devis")
        print("6. Exporter un rapport")
        print("0. Quitter")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            projet = option_charger_projet()
        elif projet is None:
            print("⚠ Chargez d'abord un projet (option 1).")
        elif choix == "2":
            option_metre(projet)
        elif choix == "3":
            option_descente_de_charges(projet)
        elif choix == "4":
            option_predimensionnement(projet)
        elif choix == "5":
            option_devis(projet)
        elif choix == "6":
            option_export_rapport(projet)
        elif choix == "0":
            print("Au revoir.")
            break
        else:
            print("Choix invalide.")


if __name__ == "__main__":
    menu()
