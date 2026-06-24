# -*- coding: utf-8 -*-
"""
==========================================================================================
 PROJET DATA SCIENCE — PREDICTION DU RESULTAT D'UN MATCH DE FOOTBALL (Premier League)
==========================================================================================
Auteur  : Lucien Nzeutom
Objectif: Predire si l'equipe a domicile gagne (oui / non) AVANT le coup d'envoi,
          en comparant deux modeles supervises (Regression logistique, Random Forest)
          et en explorant les "styles de jeu" via un modele non supervise (KMeans).

Principe methodologique central — PAS DE FUITE DE DONNEES (data leakage) :
  On n'utilise JAMAIS une statistique connue seulement APRES le match (buts, tirs,
  corners, cartons du match a predire). Les variables explicatives sont uniquement
  construites a partir de la FORME RECENTE des equipes (leurs 5 derniers matchs),
  donc disponibles avant le coup d'envoi. C'est ce qui rend la prediction credible.

Donnees : football-data.co.uk — Premier League (E0), saisons 2020-21 a 2024-25.
==========================================================================================
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix, roc_curve,
                             classification_report)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# ---- Chemins ----
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
FIG  = os.path.join(BASE, "figures")
MOD  = os.path.join(BASE, "modele")
for d in (FIG, MOD):
    os.makedirs(d, exist_ok=True)

# Palette
C_PRIMARY, C_SECOND, C_ACCENT = "#0A66C2", "#F39C12", "#2ECC71"

# ==========================================================================================
# 1. CHARGEMENT & NETTOYAGE
# ==========================================================================================
print("\n[1] Chargement des donnees...")
COLS = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
        "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR"]

frames = []
for f in sorted(os.listdir(DATA)):
    if f.endswith(".csv"):
        df = pd.read_csv(os.path.join(DATA, f))
        df = df[[c for c in COLS if c in df.columns]].copy()
        df["saison"] = f.replace("E0_", "").replace(".csv", "")
        frames.append(df)

data = pd.concat(frames, ignore_index=True)
data["Date"] = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
data = data.dropna(subset=["Date", "FTR", "HomeTeam", "AwayTeam"]).sort_values("Date").reset_index(drop=True)
print(f"    {len(data)} matchs charges sur {data['saison'].nunique()} saisons.")

# Cible binaire : victoire a domicile = 1, sinon (nul ou defaite) = 0
data["cible_victoire_domicile"] = (data["FTR"] == "H").astype(int)
taux = data["cible_victoire_domicile"].mean()
print(f"    Taux de victoires a domicile : {taux:.1%}")

# ==========================================================================================
# 2. FEATURE ENGINEERING — FORME RECENTE GLISSANTE (sans fuite de donnees)
# ==========================================================================================
print("\n[2] Construction des variables de forme (5 derniers matchs)...")
FENETRE = 5  # nombre de matchs recents pris en compte

# On construit une vue "long" : une ligne par equipe et par match, avec les stats de CE match.
def vue_equipe(df, cote):
    """cote = 'H' (domicile) ou 'A' (exterieur)."""
    if cote == "H":
        d = pd.DataFrame({
            "Date": df["Date"], "match_id": df.index, "equipe": df["HomeTeam"],
            "buts_marques": df["FTHG"], "buts_encaisses": df["FTAG"],
            "tirs": df["HS"], "tirs_cadres": df["HST"], "corners": df["HC"],
            "fautes": df["HF"], "points": np.where(df["FTR"] == "H", 3, np.where(df["FTR"] == "D", 1, 0)),
        })
    else:
        d = pd.DataFrame({
            "Date": df["Date"], "match_id": df.index, "equipe": df["AwayTeam"],
            "buts_marques": df["FTAG"], "buts_encaisses": df["FTHG"],
            "tirs": df["AS"], "tirs_cadres": df["AST"], "corners": df["AC"],
            "fautes": df["AF"], "points": np.where(df["FTR"] == "A", 3, np.where(df["FTR"] == "D", 1, 0)),
        })
    return d

longue = pd.concat([vue_equipe(data, "H"), vue_equipe(data, "A")], ignore_index=True)
longue = longue.sort_values(["equipe", "Date"]).reset_index(drop=True)

STATS = ["buts_marques", "buts_encaisses", "tirs", "tirs_cadres", "corners", "fautes", "points"]

# Moyenne glissante des N matchs PRECEDENTS (shift(1) => on exclut le match courant : ANTI-FUITE)
for s in STATS:
    longue[f"forme_{s}"] = (longue.groupby("equipe")[s]
                            .transform(lambda x: x.shift(1).rolling(FENETRE, min_periods=FENETRE).mean()))

forme_cols = [f"forme_{s}" for s in STATS]
forme = longue[["match_id", "equipe"] + forme_cols].copy()

# On rattache la forme du domicile et de l'exterieur a chaque match
data = data.reset_index().rename(columns={"index": "match_id"})
dom = forme.merge(data[["match_id", "HomeTeam"]], on="match_id")
dom = dom[dom["equipe"] == dom["HomeTeam"]].drop(columns=["equipe", "HomeTeam"])
dom = dom.rename(columns={c: f"dom_{c}" for c in forme_cols})

ext = forme.merge(data[["match_id", "AwayTeam"]], on="match_id")
ext = ext[ext["equipe"] == ext["AwayTeam"]].drop(columns=["equipe", "AwayTeam"])
ext = ext.rename(columns={c: f"ext_{c}" for c in forme_cols})

data = data.merge(dom, on="match_id").merge(ext, on="match_id")

# Variables de DIFFERENCE (force relative dom - ext) : souvent les plus parlantes
for s in STATS:
    data[f"diff_{s}"] = data[f"dom_forme_{s}"] - data[f"ext_forme_{s}"]

FEATURES = ([f"dom_forme_{s}" for s in STATS] +
            [f"ext_forme_{s}" for s in STATS] +
            [f"diff_{s}" for s in STATS])

# On retire les matchs sans historique suffisant (debut de saison)
model_df = data.dropna(subset=FEATURES).copy()
print(f"    {len(model_df)} matchs exploitables apres construction de la forme "
      f"({len(data) - len(model_df)} ecartes faute d'historique).")
print(f"    {len(FEATURES)} variables explicatives (toutes pre-match).")

# ==========================================================================================
# 3. SEPARATION TRAIN / TEST — CHRONOLOGIQUE (on n'entraine pas sur le futur)
# ==========================================================================================
model_df = model_df.sort_values("Date").reset_index(drop=True)
split = int(len(model_df) * 0.8)
train, test = model_df.iloc[:split], model_df.iloc[split:]
X_train, y_train = train[FEATURES], train["cible_victoire_domicile"]
X_test,  y_test  = test[FEATURES],  test["cible_victoire_domicile"]
print(f"\n[3] Train : {len(train)} matchs | Test : {len(test)} matchs (le plus recent).")

# ==========================================================================================
# 4. MODELES SUPERVISES
# ==========================================================================================
print("\n[4] Entrainement des modeles supervises...")
modeles = {
    "Regression logistique": Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
    ]),
    "Random Forest": Pipeline([
        ("clf", RandomForestClassifier(n_estimators=400, max_depth=6, min_samples_leaf=20,
                                       class_weight="balanced", random_state=42, n_jobs=-1)),
    ]),
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
resultats = {}
for nom, pipe in modeles.items():
    cv_auc = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="roc_auc").mean()
    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:, 1]
    pred = pipe.predict(X_test)
    resultats[nom] = {
        "cv_auc": round(float(cv_auc), 3),
        "accuracy": round(accuracy_score(y_test, pred), 3),
        "precision": round(precision_score(y_test, pred), 3),
        "recall": round(recall_score(y_test, pred), 3),
        "f1": round(f1_score(y_test, pred), 3),
        "auc": round(roc_auc_score(y_test, proba), 3),
    }
    print(f"  - {nom}: AUC test={resultats[nom]['auc']} | "
          f"Acc={resultats[nom]['accuracy']} | F1={resultats[nom]['f1']}")
    print(classification_report(y_test, pred, target_names=["Pas victoire dom.", "Victoire dom."]))

# Reference naïve : toujours predire la classe majoritaire
acc_naif = max(taux, 1 - taux)
print(f"  > Reference naive (classe majoritaire) : accuracy = {acc_naif:.3f}")

# Choix du meilleur modele (selon AUC test)
meilleur = max(resultats, key=lambda k: resultats[k]["auc"])
print(f"\n  ==> MEILLEUR MODELE : {meilleur} (AUC = {resultats[meilleur]['auc']})")

# ==========================================================================================
# 5. MODELE NON SUPERVISE — KMEANS (styles de jeu des equipes)
# ==========================================================================================
print("\n[5] Clustering KMeans des styles d'equipes (profil moyen)...")
profil = (longue.groupby(["equipe"])[STATS].mean())
Xp = StandardScaler().fit_transform(profil)
K = 4
km = KMeans(n_clusters=K, random_state=42, n_init=10)
profil["cluster"] = km.fit_predict(Xp)

# Etiquettes lisibles : on ordonne les clusters par points moyens et on decrit
# leur profil offensif/defensif dominant (interpretation a posteriori des centres).
centres = profil.groupby("cluster")[STATS].mean().sort_values("points", ascending=False)
ordre = list(centres.index)
noms_tiers = ["Cluster 1 - Cadors (offensifs & solides)",
              "Cluster 2 - Haut de tableau",
              "Cluster 3 - Milieu de tableau",
              "Cluster 4 - Bas de tableau (defense fragile)"]
labels = {cl: noms_tiers[i] for i, cl in enumerate(ordre)}
profil["style"] = profil["cluster"].map(labels)
print(profil.sort_values("points", ascending=False)[["points", "buts_marques", "buts_encaisses", "style"]].round(2).to_string())

# ==========================================================================================
# 6. SAUVEGARDE DES RESULTATS (pour le PDF) + EXPORT DU MODELE OPTIMAL
# ==========================================================================================
print("\n[6] Sauvegarde des resultats et du modele optimal...")
# Reentrainement du meilleur modele sur TOUTES les donnees pour la mise en production
modele_final = modeles[meilleur]
modele_final.fit(model_df[FEATURES], model_df["cible_victoire_domicile"])
joblib.dump({"modele": modele_final, "features": FEATURES, "fenetre": FENETRE,
             "nom": meilleur}, os.path.join(MOD, "modele_optimal.pkl"))

# Importance des variables (selon le modele)
if meilleur == "Random Forest":
    importances = dict(zip(FEATURES, modele_final.named_steps["clf"].feature_importances_))
else:
    coefs = modele_final.named_steps["clf"].coef_[0]
    importances = dict(zip(FEATURES, np.abs(coefs)))
top_imp = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10])

synthese = {
    "n_matchs": int(len(data)), "n_exploitables": int(len(model_df)),
    "n_saisons": int(data["saison"].nunique()),
    "taux_victoire_domicile": round(float(taux), 3),
    "accuracy_naif": round(float(acc_naif), 3),
    "n_features": len(FEATURES), "fenetre": FENETRE,
    "resultats": resultats, "meilleur_modele": meilleur,
    "top_importances": {k: round(float(v), 4) for k, v in top_imp.items()},
    "kmeans_k": K,
    "kmeans_styles": profil.reset_index()[["equipe", "points", "buts_marques",
                                           "buts_encaisses", "style"]]
                     .round(2).to_dict(orient="records"),
}
with open(os.path.join(BASE, "resultats.json"), "w", encoding="utf-8") as fp:
    json.dump(synthese, fp, ensure_ascii=False, indent=2)

# Sauvegarde pour les figures
np.savez(os.path.join(BASE, "_plotdata.npz"),
         y_test=y_test.values,
         proba_best=modeles[meilleur].predict_proba(X_test)[:, 1],
         pred_best=modeles[meilleur].predict(X_test),
         top_keys=np.array(list(top_imp.keys())),
         top_vals=np.array(list(top_imp.values())),
         prof_x=Xp[:, 0], prof_y=Xp[:, 1],
         prof_cluster=profil["cluster"].values)
print("    -> resultats.json, modele_optimal.pkl, _plotdata.npz ecrits.")
print("\nTermine.")
