# -*- coding: utf-8 -*-
"""
==========================================================================================
 PREDICTION D'UN NOUVEAU MATCH avec le modele optimal exporte (modele_optimal.pkl)
==========================================================================================
On fournit la FORME RECENTE (moyenne sur les 5 derniers matchs) de l'equipe a domicile
et de l'equipe a l'exterieur. Le modele renvoie la probabilite d'une victoire a domicile.

Comme dans le projet 12 (detection de faux billets), on charge le modele entraine et on
predit sur de nouvelles entrees. Aucune statistique du match a venir n'est requise :
seulement la dynamique recente des deux equipes.

Usage : python 02_predire_nouveau_match.py
==========================================================================================
"""

import os
import joblib
import pandas as pd


BASE = os.path.dirname(os.path.abspath(__file__))
bundle = joblib.load(os.path.join(BASE, "modele", "modele_optimal.pkl"))
modele, FEATURES = bundle["modele"], bundle["features"]
STATS = ["buts_marques", "buts_encaisses", "tirs", "tirs_cadres", "corners", "fautes", "points"]


def construire_ligne(forme_dom: dict, forme_ext: dict) -> pd.DataFrame:
    """forme_dom / forme_ext : dictionnaires {stat: moyenne sur les 5 derniers matchs}."""
    ligne = {}
    for s in STATS:
        ligne[f"dom_forme_{s}"] = forme_dom[s]
        ligne[f"ext_forme_{s}"] = forme_ext[s]
        ligne[f"diff_{s}"] = forme_dom[s] - forme_ext[s]
    return pd.DataFrame([ligne])[FEATURES]


def predire(nom_dom, nom_ext, forme_dom, forme_ext):
    X = construire_ligne(forme_dom, forme_ext)
    proba = float(modele.predict_proba(X)[:, 1][0])
    verdict = "VICTOIRE a domicile probable" if proba >= 0.5 else "Pas de victoire a domicile (nul ou defaite plus probable)"
    print(f"\n  {nom_dom} (domicile)  vs  {nom_ext} (exterieur)")
    print(f"  Probabilite de victoire de {nom_dom} : {proba:.1%}")
    print(f"  -> {verdict}")
    return proba


if __name__ == "__main__":
    print("=" * 70)
    print(" DEMO — Prediction d'un nouveau match")
    print(f" Modele utilise : {bundle['nom']}")
    print("=" * 70)

    # --- Exemple 1 : une grosse equipe en forme recoit une equipe en difficulte ---
    forme_domicile = {"buts_marques": 2.4, "buts_encaisses": 0.8, "tirs": 16, "tirs_cadres": 6.5,
                      "corners": 7, "fautes": 9, "points": 2.4}
    forme_exterieur = {"buts_marques": 0.9, "buts_encaisses": 2.1, "tirs": 8, "tirs_cadres": 2.5,
                       "corners": 3.5, "fautes": 12, "points": 0.7}
    predire("Equipe A (cador en forme)", "Equipe B (en difficulte)", forme_domicile, forme_exterieur)

    # --- Exemple 2 : deux equipes de niveau equivalent ---
    forme_domicile = {"buts_marques": 1.4, "buts_encaisses": 1.4, "tirs": 12, "tirs_cadres": 4,
                      "corners": 5, "fautes": 11, "points": 1.3}
    forme_exterieur = {"buts_marques": 1.5, "buts_encaisses": 1.3, "tirs": 13, "tirs_cadres": 4.5,
                       "corners": 5.5, "fautes": 10, "points": 1.5}
    predire("Equipe C", "Equipe D", forme_domicile, forme_exterieur)

    print("\n" + "=" * 70)
    print(" Pour tester vos propres equipes : modifiez les dictionnaires 'forme_*' ci-dessus")
    print(" (moyennes sur les 5 derniers matchs de chaque equipe).")
    print("=" * 70)
