# -*- coding: utf-8 -*-
"""Figures en theme sombre, assorties au carrousel LinkedIn (fond #0E1412)."""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures_dark")
os.makedirs(FIG, exist_ok=True)

FOND   = "#0E1412"
SURF   = "#141D18"
OR     = "#E9B03B"
VERT   = "#2ECC71"
ROUGE  = "#E74C3C"
BLANC  = "#F4F6F5"
GRIS   = "#9AA5A0"

plt.rcParams.update({
    "figure.facecolor": FOND, "axes.facecolor": FOND, "savefig.facecolor": FOND,
    "text.color": BLANC, "axes.labelcolor": BLANC, "xtick.color": GRIS, "ytick.color": GRIS,
    "axes.edgecolor": "#2A332E", "grid.color": "#1E2823", "font.size": 12,
    "axes.titleweight": "bold", "axes.titlecolor": BLANC, "figure.dpi": 160,
})

res = json.load(open(os.path.join(BASE, "resultats.json"), encoding="utf-8"))
d = np.load(os.path.join(BASE, "_plotdata.npz"), allow_pickle=True)
y_test, proba, pred = d["y_test"], d["proba_best"], d["pred_best"]
best = res["meilleur_modele"]

# --- Fig 1 : comparaison modeles ---
modeles = list(res["resultats"].keys())
metr, labels_metr = ["accuracy", "f1", "auc"], ["Accuracy", "F1-score", "AUC"]
x = np.arange(len(metr)); w = 0.35
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for i, m in enumerate(modeles):
    vals = [res["resultats"][m][k] for k in metr]
    ax.bar(x + i*w, vals, w, label=m, color=[OR, VERT][i], zorder=3)
    for j, v in enumerate(vals):
        ax.text(x[j]+i*w, v+0.012, f"{v:.2f}", ha="center", fontsize=10, fontweight="bold", color=BLANC)
ax.axhline(res["accuracy_naif"], ls="--", color=GRIS, lw=1.4, label=f"Reference naive ({res['accuracy_naif']:.2f})")
ax.set_xticks(x + w/2); ax.set_xticklabels(labels_metr)
ax.set_ylim(0, 0.82); ax.set_ylabel("Score (jeu de test)")
ax.grid(axis="y", zorder=0)
leg = ax.legend(loc="upper right", fontsize=9, facecolor=SURF, edgecolor="#2A332E")
for t in leg.get_texts(): t.set_color(BLANC)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "comparaison.png")); plt.close()

# --- Fig 2 : courbe ROC ---
fpr, tpr, _ = roc_curve(y_test, proba)
fig, ax = plt.subplots(figsize=(6.4, 4.8))
ax.plot(fpr, tpr, color=OR, lw=3, label=f"{best} (AUC = {auc(fpr,tpr):.2f})", zorder=3)
ax.fill_between(fpr, tpr, alpha=0.12, color=OR)
ax.plot([0,1],[0,1], ls="--", color=GRIS, label="Hasard (0.50)")
ax.set_xlabel("Taux de faux positifs"); ax.set_ylabel("Taux de vrais positifs")
ax.grid(True)
leg = ax.legend(loc="lower right", facecolor=SURF, edgecolor="#2A332E")
for t in leg.get_texts(): t.set_color(BLANC)
for s in ["top","right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "roc.png")); plt.close()

# --- Fig 3 : importance des variables ---
keys = list(res["top_importances"].keys())[::-1]
vals = list(res["top_importances"].values())[::-1]
jolis = {"diff_points":"Diff. points (forme)","diff_buts_marques":"Diff. buts marques",
         "diff_buts_encaisses":"Diff. buts encaisses","diff_tirs_cadres":"Diff. tirs cadres",
         "diff_tirs":"Diff. tirs","diff_corners":"Diff. corners","diff_fautes":"Diff. fautes",
         "dom_forme_points":"Forme points (dom.)","ext_forme_points":"Forme points (ext.)",
         "dom_forme_buts_marques":"Buts marques (dom.)","ext_forme_buts_encaisses":"Buts encaisses (ext.)",
         "dom_forme_buts_encaisses":"Buts encaisses (dom.)","ext_forme_buts_marques":"Buts marques (ext.)",
         "dom_forme_tirs_cadres":"Tirs cadres (dom.)","ext_forme_tirs_cadres":"Tirs cadres (ext.)"}
noms = [jolis.get(k,k) for k in keys]
cols = [OR if i >= len(noms)-3 else "#3E8E5F" for i in range(len(noms))]
fig, ax = plt.subplots(figsize=(7.2, 4.8))
ax.barh(noms, vals, color=cols, zorder=3)
ax.set_xlabel("Importance relative"); ax.grid(axis="x", zorder=0)
for s in ["top","right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "importance.png")); plt.close()

# --- Fig 4 : clusters KMeans ---
px, py, cl = d["prof_x"], d["prof_y"], d["prof_cluster"]
fig, ax = plt.subplots(figsize=(6.6, 5.0))
palette = [OR, VERT, "#5DADE2", ROUGE]
noms_cl = ["Cadors", "Haut de tableau", "Milieu", "Bas de tableau"]
# ordre par force (composante 1 moyenne) pour des labels coherents
ordre = sorted(np.unique(cl), key=lambda c: -px[cl==c].mean())
for rank, c in enumerate(ordre):
    ax.scatter(px[cl==c], py[cl==c], s=130, color=palette[rank % 4],
               label=noms_cl[rank], edgecolor=FOND, linewidth=1.2, zorder=3)
ax.set_xlabel("Composante 1 (force globale)"); ax.set_ylabel("Composante 2")
ax.grid(True)
leg = ax.legend(facecolor=SURF, edgecolor="#2A332E", fontsize=9)
for t in leg.get_texts(): t.set_color(BLANC)
for s in ["top","right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "clusters.png")); plt.close()

print("Figures sombres generees :", os.listdir(FIG))
