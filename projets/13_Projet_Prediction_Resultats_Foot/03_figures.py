# -*- coding: utf-8 -*-
"""Generation des figures (PNG) pour le rapport LinkedIn."""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc

BASE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(BASE, "figures")
os.makedirs(FIG, exist_ok=True)

C_PRIMARY, C_SECOND, C_ACCENT, C_GREY = "#0A66C2", "#F39C12", "#2ECC71", "#7F8C8D"
plt.rcParams.update({"font.size": 11, "axes.titleweight": "bold", "figure.dpi": 130})

res = json.load(open(os.path.join(BASE, "resultats.json"), encoding="utf-8"))
d = np.load(os.path.join(BASE, "_plotdata.npz"), allow_pickle=True)
y_test, proba, pred = d["y_test"], d["proba_best"], d["pred_best"]
best = res["meilleur_modele"]

# --- Fig 1 : Comparaison des modeles ---
modeles = list(res["resultats"].keys())
metr = ["accuracy", "f1", "auc"]
labels_metr = ["Accuracy", "F1-score", "AUC"]
x = np.arange(len(metr)); w = 0.35
fig, ax = plt.subplots(figsize=(8, 5))
for i, m in enumerate(modeles):
    vals = [res["resultats"][m][k] for k in metr]
    ax.bar(x + i*w, vals, w, label=m, color=[C_PRIMARY, C_SECOND][i])
    for j, v in enumerate(vals):
        ax.text(x[j]+i*w, v+0.01, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
ax.axhline(res["accuracy_naif"], ls="--", color=C_GREY, lw=1.5,
           label=f"Reference naive ({res['accuracy_naif']:.2f})")
ax.set_xticks(x + w/2); ax.set_xticklabels(labels_metr)
ax.set_ylim(0, 0.85); ax.set_ylabel("Score (jeu de test)")
ax.set_title("Comparaison des modeles supervises")
ax.legend(loc="upper right", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "01_comparaison_modeles.png")); plt.close()

# --- Fig 2 : Matrice de confusion (meilleur modele) ---
cm = confusion_matrix(y_test, pred)
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(cm, cmap="Blues")
for i in range(2):
    for j in range(2):
        ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=18, fontweight="bold",
                color="white" if cm[i, j] > cm.max()/2 else "black")
ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
ax.set_xticklabels(["Pas victoire", "Victoire dom."])
ax.set_yticklabels(["Pas victoire", "Victoire dom."])
ax.set_xlabel("Prediction"); ax.set_ylabel("Realite")
ax.set_title(f"Matrice de confusion — {best}")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "02_matrice_confusion.png")); plt.close()

# --- Fig 3 : Courbe ROC ---
fpr, tpr, _ = roc_curve(y_test, proba)
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(fpr, tpr, color=C_PRIMARY, lw=2.5, label=f"{best} (AUC = {auc(fpr,tpr):.3f})")
ax.plot([0, 1], [0, 1], ls="--", color=C_GREY, label="Hasard (AUC = 0.5)")
ax.set_xlabel("Taux de faux positifs"); ax.set_ylabel("Taux de vrais positifs")
ax.set_title("Courbe ROC"); ax.legend(loc="lower right")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "03_courbe_roc.png")); plt.close()

# --- Fig 4 : Importance des variables ---
keys = list(res["top_importances"].keys())[::-1]
vals = list(res["top_importances"].values())[::-1]
jolis = {"diff_points": "Diff. points (forme)", "diff_buts_marques": "Diff. buts marques",
         "diff_buts_encaisses": "Diff. buts encaisses", "diff_tirs_cadres": "Diff. tirs cadres",
         "diff_tirs": "Diff. tirs", "diff_corners": "Diff. corners", "diff_fautes": "Diff. fautes",
         "dom_forme_points": "Forme points (dom.)", "ext_forme_points": "Forme points (ext.)",
         "dom_forme_buts_marques": "Buts marques (dom.)", "ext_forme_buts_encaisses": "Buts encaisses (ext.)",
         "dom_forme_buts_encaisses": "Buts encaisses (dom.)", "ext_forme_buts_marques": "Buts marques (ext.)",
         "dom_forme_tirs_cadres": "Tirs cadres (dom.)", "ext_forme_tirs_cadres": "Tirs cadres (ext.)"}
noms = [jolis.get(k, k) for k in keys]
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(noms, vals, color=C_ACCENT)
ax.set_title(f"Top 10 des variables — {best}")
ax.set_xlabel("Importance relative")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "04_importance_variables.png")); plt.close()

# --- Fig 5 : Clusters KMeans ---
px, py, cl = d["prof_x"], d["prof_y"], d["prof_cluster"]
fig, ax = plt.subplots(figsize=(7, 5.5))
palette = [C_PRIMARY, C_SECOND, C_ACCENT, "#E74C3C"]
for c in np.unique(cl):
    ax.scatter(px[cl == c], py[cl == c], s=90, color=palette[c % len(palette)],
               label=f"Cluster {c}", edgecolor="white", linewidth=0.7)
ax.set_xlabel("Composante 1 (force globale)"); ax.set_ylabel("Composante 2")
ax.set_title("KMeans — 4 styles d'equipes (Premier League)")
ax.legend()
plt.tight_layout(); plt.savefig(os.path.join(FIG, "05_clusters_kmeans.png")); plt.close()

print("5 figures generees dans /figures.")
for f in sorted(os.listdir(FIG)):
    print("  -", f)
