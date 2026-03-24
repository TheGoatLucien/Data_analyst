#  Guide d'utilisation — Script de détection de faux billets

##  Prérequis

Le script nécessite les bibliothèques Python suivantes :
```bash
pip install pandas numpy scikit-learn
```

## Fichiers nécessaires

Le script a besoin du fichier d'entraînement dans le **même répertoire** :
- `billets.csv` (le fichier original avec les 1500 billets)

##  Utilisation

Le script propose **2 modes d'utilisation** :

---

### Mode 1 : Analyse d'un fichier CSV

Pour analyser plusieurs billets d'un coup à partir d'un fichier CSV :

```bash
python script_detection_faux_billets.py --fichier exemple_fichier_test.csv
```

**Format du fichier CSV attendu** (séparateur point-virgule `;`) :
```csv
diagonal;height_left;height_right;margin_low;margin_up;length
171.81;104.86;104.95;4.52;2.89;112.83
172.10;104.20;104.15;5.20;3.35;111.60
```

**Résultat** :
- Le script affiche les résultats dans le terminal
- Un fichier de sortie est créé automatiquement : `billets_production_resultats.csv`

#### Exemple de sortie :

```
╔══════════════════════════════════════════════════════════════════╗
║     ONCFM — Détection automatique de faux billets              ║
║     Organisation nationale de lutte contre le faux-monnayage   ║
╚══════════════════════════════════════════════════════════════════╝

 Fichier chargé : billets_production.csv
   Nombre de billets à analyser : 5
======================================================================
Entraînement du modèle en cours...
Modèle entraîné avec succès (Régression Logistique)
======================================================================

RÉSULTATS DE L'ANALYSE :
----------------------------------------------------------------------
   diagonal  height_left  height_right  margin_low  margin_up  length Résultat  Confiance (%)
0    171.81       104.86        104.95        4.52       2.89  112.83   VRAI ✓          67.54
1    172.10       104.20        104.15        5.20       3.35  111.60   FAUX ✗          99.96
2    171.95       103.90        103.85        4.10       3.05  113.20   VRAI ✓          99.90
3    170.50       104.50        104.40        5.50       3.40  110.80   FAUX ✗         100.00
4    172.30       104.00        103.95        4.05       2.95  113.40   VRAI ✓          99.98
----------------------------------------------------------------------

 RÉSUMÉ :
   Billets identifiés comme VRAIS  : 3
   Billets identifiés comme FAUX   : 2
   Taux de faux détectés           : 40.0%

💾 Résultats sauvegardés dans : billets_production_resultats.csv
```

---

### Mode 2 : Saisie manuelle (interactive)

Pour vérifier un billet individuellement en saisissant ses dimensions :

```bash
python script_detection_faux_billets.py --manuel
```

Le script vous demandera de saisir les 6 dimensions une par une :

```
======================================================================
  ONCFM — Vérification manuelle d'un billet
======================================================================

Entrez les dimensions géométriques du billet (en mm) :
--------------------------------------------------
  Diagonale du billet (diagonal) : 171.81
  Hauteur côté gauche (height_left) : 104.86
  Hauteur côté droit (height_right) : 104.95
  Marge inférieure (margin_low) : 4.52
  Marge supérieure (margin_up) : 2.89
  Longueur du billet (length) : 112.83

Entraînement du modèle en cours...
Modèle entraîné avec succès

======================================================================
    Le billet est identifié comme : VRAI
    Niveau de confiance : 67.54%
======================================================================

Voulez-vous vérifier un autre billet ? (o/n) :
```

---

##  Interprétation des résultats

### Résultat
- **VRAI ✓** : Le billet est identifié comme authentique
- **FAUX ✗** : Le billet est identifié comme contrefait

### Confiance (%)
Le pourcentage de confiance indique à quel point le modèle est sûr de sa prédiction :
- **> 95%** : Très haute confiance
- **80-95%** : Bonne confiance
- **< 80%** : Confiance modérée (cas limite, vérification manuelle recommandée)

---

##  Comment ça marche ?

1. **Entraînement automatique** : À chaque exécution, le script charge `billets.csv`, nettoie les données (imputation des valeurs manquantes), et entraîne un modèle de régression logistique.

2. **Prédiction** : Le modèle analyse les 6 dimensions géométriques du billet et calcule une probabilité que le billet soit vrai ou faux.

3. **Le modèle utilisé** : Régression Logistique (99.33% d'accuracy sur les tests)

---

##  Aide

Pour voir l'aide complète :
```bash
python Nzeutom_Lucien_script_detection_032026.py --help
```

---

##  Dépannage

### Erreur : "Le fichier 'billets.csv' n'existe pas"
**Solution** : Assurez-vous que le fichier `billets.csv` est dans le même répertoire que le script.

### Erreur : "Colonnes manquantes dans le fichier"
**Solution** : Vérifiez que votre fichier CSV contient exactement ces colonnes :
- diagonal
- height_left
- height_right
- margin_low
- margin_up
- length

### Le fichier de sortie n'est pas créé
**Solution** : Vérifiez que vous avez les droits d'écriture dans le répertoire courant.

---

##  Notes techniques

- **Modèle** : Régression Logistique avec standardisation StandardScaler
- **Entraînement** : Train/Test 70/30, stratifié
- **Performance** : 99.33% accuracy, 1 FP, 2 FN sur 450 billets testés
- **Temps d'exécution** : ~1-2 secondes pour l'entraînement + prédiction

---

##  Support

En cas de problème, vérifiez que :
1. Python 3.7+ est installé
2. Toutes les dépendances sont installées (`pip install -r requirements.txt`)
3. Le fichier `billets.csv` est bien présent

---

**Bonne détection ! :)**
