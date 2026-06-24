# Prédiction du résultat d'un match de football (Premier League)

Projet de machine learning **supervisé + non supervisé** : prédire, *avant le coup d'envoi*, si l'équipe à domicile va gagner.

## Démarche
- **Données** : football-data.co.uk, Premier League (E0), 5 saisons (2020-21 → 2024-25), ~1 900 matchs.
- **Cible** : binaire — victoire à domicile (1) vs nul/défaite (0).
- **Anti-fuite de données** : les variables sont calculées uniquement sur la **forme récente** (moyennes glissantes des 5 derniers matchs, via `shift(1)`), donc connues avant le match.
- **Modèles** : régression logistique + random forest (supervisé), KMeans (clustering des styles d'équipes).
- **Validation** : split chronologique train/test + validation croisée 5 plis.

## Résultats
| Métrique | Rég. logistique | Random Forest |
|---|---|---|
| Accuracy | 0.58 | **0.60** |
| AUC | 0.64 | **0.65** |

Référence naïve (classe majoritaire) : 0.57. Le **Random Forest** est le modèle retenu et exporté.

## Fichiers
- `01_pipeline_modelisation.py` — préparation, feature engineering, entraînement des 3 modèles, export du modèle optimal.
- `02_predire_nouveau_match.py` — prédit sur de nouvelles entrées à partir du modèle exporté.
- `03_figures.py` — génère les graphiques.
- `04_generer_pdf.py` — génère le rapport PDF LinkedIn.
- `modele/modele_optimal.pkl` — modèle prêt à l'emploi.
- `Rapport_LinkedIn_Prediction_Foot.pdf` — synthèse pro.
- `Post_LinkedIn.md` — brouillon de publication.

## Lancer
```bash
pip install pandas scikit-learn matplotlib seaborn joblib reportlab pillow
python 01_pipeline_modelisation.py
python 03_figures.py
python 04_generer_pdf.py
python 02_predire_nouveau_match.py   # démo de prédiction
```
