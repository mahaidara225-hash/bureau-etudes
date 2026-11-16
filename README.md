# Bureau d'études — Projet 1

Application console (Python, bibliothèque standard uniquement) qui
réutilise les séances 1 à 5 : saisie/chargement de projet, métré,
descente de charges, prédimensionnement poteaux/semelles, devis et
export d'un rapport.

## Arborescence

```
bureau-etudes/
├── README.md
├── requirements.txt
├── .gitignore
├── donnees/
│   ├── projet.json        # exemple de projet (à remplacer par vos données)
│   ├── materiaux.json      # hypothèses béton / sol
│   └── bordereau.csv       # prix unitaires pour le devis
├── src/
│   ├── elements.py         # structures de données + chargement/sauvegarde JSON
│   ├── charges.py          # descente de charges (S3)
│   ├── predimensionnement.py  # poteaux + semelles (S2 et S3)
│   ├── devis.py            # métré + devis (S1, S4, S5)
│   └── main.py             # menu console (S4)
└── tests/
    └── test_charges.py     # contrôle des valeurs de l'énoncé
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Aucune dépendance externe n'est obligatoire pour l'exécution (seul
`pytest` est utile pour les tests).

## Utilisation

```bash
cd src
python3 main.py
```

Menu affiché :

```
1. Saisir ou charger le projet
2. Calculer le métré
3. Descente de charges
4. Prédimensionner poteaux et semelles
5. Générer le devis
6. Exporter un rapport
0. Quitter
```

Le projet courant est automatiquement sauvegardé dans
`donnees/projet.json` après chaque modification.

## Lancer les tests (valeurs de contrôle)

```bash
python3 -m pytest tests/ -v
```

Les tests vérifient que `predimensionnement.py` retrouve exactement les
valeurs de l'énoncé :

| Poteau  | N_ELU (kN) | A_min (m²) | Côté retenu |
|---------|-----------:|-----------:|:-----------:|
| Angle   | 168.4      | 0.017      | 20 cm       |
| Rive    | 317.8      | 0.032      | 20 cm       |
| Central | 616.6      | 0.062      | 25 cm       |

| Semelle | G+Q (kN) | Côté minimal | Côté retenu |
|---------|---------:|:------------:|:-----------:|
| Angle   | 122.1    | 0.81 m       | 0.85 m      |
| Rive    | 230.1    | 1.11 m       | 1.15 m      |
| Central | 446.1    | 1.54 m       | 1.55 m      |

## Organisation Git / GitHub (équipe)

Critères visés : 1 module par membre, ≥ 5 commits chacun, usage réel
de branches/pull requests.

### 1. Mise en place (une seule fois, par le "chef de dépôt")

```bash
cd bureau-etudes
git init
git add .
git commit -m "Initialisation : arborescence, README, requirements"
git branch -M main
# créer le dépôt vide sur github.com puis :
git remote add origin https://github.com/<organisation>/<depot>.git
git push -u origin main
```

Chaque membre clone ensuite :

```bash
git clone https://github.com/<organisation>/<depot>.git
cd bureau-etudes
```

### 2. Répartition suggérée des modules (1 par membre)

| Membre | Fichier(s) en charge           |
|--------|---------------------------------|
| A      | `src/elements.py` + `donnees/`  |
| B      | `src/charges.py`                |
| C      | `src/predimensionnement.py`     |
| D      | `src/devis.py`                  |
| E      | `src/main.py` + `tests/`        |

### 3. Workflow quotidien par branche

```bash
git checkout -b feature/<module>        # ex : feature/predimensionnement
# ... modifications ...
git add src/<fichier>.py
git commit -m "predim: ajoute predimensionner_semelle + docstring"
git push -u origin feature/<module>
```

Sur GitHub : ouvrir une **Pull Request** de `feature/<module>` vers
`main`, demander une relecture à un coéquipier, puis **Merge**.

### 4. Convention de messages de commit

```
<module>: <action au présent, courte>

ex:
charges: ajoute la dégression des charges d'exploitation
predim: corrige l'arrondi du côté de semelle
devis: lit le bordereau.csv et calcule le total HT
main: ajoute l'option 6 export du rapport
tests: ajoute le contrôle des valeurs de l'énoncé
```

Chaque membre doit avoir **au moins 5 commits** répartis sur son
module (ne pas regrouper tout le travail en un seul commit).

### 5. Avant la soutenance

```bash
git checkout main
git pull
python3 -m pytest tests/ -v   # tout doit être vert
```

Le **lien du dépôt GitHub d'équipe** est le livrable à remettre en fin
de séance.
