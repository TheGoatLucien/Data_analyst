# Légende du post LinkedIn (carrousel)

> Document à publier : `Carrousel_LinkedIn_Prediction_Foot.pdf` (post type « document »).


---

Peut-on prédire le résultat d'un match de foot AVANT le coup d'envoi ?

J'ai voulu tester, proprement. 1 900 matchs de Premier League, 3 modèles de machine learning, et une règle que je me suis fixée : ne jamais tricher avec le futur.

Le piège classique, c'est d'utiliser les tirs ou les buts du match pour prédire son résultat. Sauf que ces stats n'existent qu'une fois le match joué — le modèle aurait l'air brillant et serait inutilisable le jour J. J'ai donc tout construit à partir de la forme récente des équipes (leurs 5 derniers matchs), connue avant le coup d'envoi.

Résultat : ~60% de bons pronostics avec un Random Forest, contre 57% pour un réflexe naïf. Mieux que le hasard, mais le foot garde sa part d'imprévu — et c'est très bien comme ça.

Ce qui m'a marqué : le modèle a appris seul que c'est l'écart de forme entre les deux équipes qui compte, pas la forme d'une équipe isolée. En bonus, un KMeans non supervisé redessine tout seul 4 styles d'équipes, des cadors au bas de tableau.

Un modèle honnête, ce n'est pas un modèle qui promet 100%. C'est un modèle qui sait ce qu'il ignore.

Stack : Python, pandas, scikit-learn. Données publiques (football-data.co.uk).

#DataScience #MachineLearning #Python #Football #DataAnalysis
