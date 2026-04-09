#  Guide d'utilisation — Script de détection de faux billets

##  Prérequis

Le script nécessite les bibliothèques Python suivantes :
```bash
pip install pandas numpy scikit-learn
```

##  Fichiers nécessaires

Le script a besoin du fichier d'entraînement dans le **même répertoire** :
- **`billets.csv`** (le fichier original avec les 1500 billets et la colonne `is_genuine`)

 **IMPORTANT** : Sans ce fichier, le script ne peut pas fonctionner car il doit entraîner le modèle à chaque exécution.

---

##  Utilisation

Le script propose **2 modes d'utilisation** :

---

### Mode 1 : Analyse d'un fichier CSV

Pour analyser plusieurs billets d'un coup à partir d'un fichier CSV :

```bash
python script_detection_faux_billets.py --fichier billets_production.csv
```

####  Formats CSV acceptés

Le script **détecte automatiquement** le format de votre fichier CSV et accepte les deux formats suivants :

##### **Format A : Séparateur virgule** (`,`)
```csv
diagonal,height_left,height_right,margin_low,margin_up,length
171.81,104.86,104.95,4.52,2.89,112.83
172.10,104.20,104.15,5.20,3.35,111.60
```

##### **Format B : Séparateur point-virgule** (`;`)
```csv
diagonal;height_left;height_right;margin_low;margin_up;length
171.81;104.86;104.95;4.52;2.89;112.83
172.10;104.20;104.15;5.20;3.35;111.60
```

**Le script détecte automatiquement lequel vous utilisez !** 

#### Colonne `id` (optionnelle)

Si votre fichier contient une colonne `id`, elle sera automatiquement affichée dans les résultats :

```csv
diagonal,height_left,height_right,margin_low,margin_up,length,id
171.81,104.86,104.95,4.52,2.89,112.83,A_1
172.10,104.20,104.15,5.20,3.35,111.60,A_2
```

####  Exemple de sortie :

```
╔══════════════════════════════════════════════════════════════════╗
║     ONCFM — Détection automatique de faux billets              ║
║     Organisation nationale de lutte contre le faux-monnayage   ║
╚══════════════════════════════════════════════════════════════════╝

 Fichier chargé : billets_production.csv
   Format détecté : séparateur ','
   Colonnes trouvées : diagonal, height_left, height_right, margin_low, margin_up, length, id
   Nombre de billets à analyser : 5
======================================================================
Entraînement du modèle en cours...
 Modèle entraîné avec succès (Régression Logistique)
   Accuracy sur le test : 0.9933 (99.33%)
======================================================================

 RÉSULTATS DE L'ANALYSE :
----------------------------------------------------------------------
    id  diagonal  height_left  height_right  margin_low  margin_up  length Résultat  Confiance (%)
0  A_1    171.76       104.01        103.54        5.21       3.30  111.42   FAUX ✗      99.84
1  A_2    171.87       104.17        104.13        6.00       3.31  112.09   FAUX ✗      99.98
2  A_3    172.00       104.58        104.29        4.99       3.39  111.57   FAUX ✗      99.97
3  A_4    172.49       104.55        104.34        4.44       3.03  113.20   VRAI ✓      97.78
4  A_5    171.65       103.63        103.56        3.77       3.16  113.33   VRAI ✓      99.98
----------------------------------------------------------------------

 RÉSUMÉ :
    Billets identifiés comme VRAIS  : 2
    Billets identifiés comme FAUX   : 3
    Taux de faux détectés           : 60.0%

 Résultats sauvegardés dans : billets_production_resultats.csv
```

**Résultat** :
- Le script affiche les résultats dans le terminal
- Un fichier de sortie est créé automatiquement : `[nom_fichier]_resultats.csv`
- Le fichier de sortie utilise le **même séparateur** que le fichier d'entrée

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
    Le billet est identifié comme : VRAI ✓
    Niveau de confiance : 55.81%
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

2. **Détection automatique du format** : Le script analyse votre fichier CSV et détecte automatiquement si vous utilisez des virgules (`,`) ou des points-virgules (`;`) comme séparateur.

3. **Prédiction** : Le modèle analyse les 6 dimensions géométriques du billet et calcule une probabilité que le billet soit vrai ou faux.

4. **Le modèle utilisé** : Régression Logistique (99.33% d'accuracy sur les tests)

---

##  Aide

Pour voir l'aide complète :
```bash
python script_detection_faux_billets.py --help
```

Ou utilisez les raccourcis :
```bash
python script_detection_faux_billets.py -f billets_production.csv  # Mode fichier
python script_detection_faux_billets.py -m                          # Mode manuel
```

---

##  Dépannage

### Erreur : "Le fichier 'billets.csv' n'existe pas"
**Solution** : Assurez-vous que le fichier `billets.csv` (le fichier d'entraînement) est dans le même répertoire que le script. Ce fichier est **OBLIGATOIRE**.

### Erreur : "Colonnes manquantes dans le fichier"
**Solution** : Vérifiez que votre fichier CSV contient exactement ces colonnes :
- `diagonal`
- `height_left`
- `height_right`
- `margin_low`
- `margin_up`
- `length`

La colonne `id` est optionnelle.

### Le fichier de sortie n'est pas créé
**Solution** : Vérifiez que vous avez les droits d'écriture dans le répertoire courant.

### Mon fichier CSV utilise un autre séparateur (tabulation, espace, etc.)
**Solution** : Le script ne supporte actuellement que les virgules (`,`) et points-virgules (`;`). Si vous utilisez un autre séparateur, convertissez votre fichier en utilisant l'un de ces deux formats.

---

##  Exemples complets

### Exemple 1 : Fichier avec virgules et identifiants
```bash
python script_detection_faux_billets.py --fichier billets_production.csv
```
→ Analyse un fichier avec séparateur `,` et colonne `id`

### Exemple 2 : Fichier avec points-virgules
```bash
python script_detection_faux_billets.py --fichier mes_billets.csv
```
→ Analyse un fichier avec séparateur `;`

### Exemple 3 : Vérification manuelle d'un billet
```bash
python script_detection_faux_billets.py --manuel
```
→ Mode interactif pour saisir les dimensions

---

##  Notes techniques

- **Modèle** : Régression Logistique avec standardisation StandardScaler
- **Entraînement** : Train/Test 70/30, stratifié
- **Performance** : 99.33% accuracy, 1 FP, 2 FN sur 450 billets testés
- **Temps d'exécution** : ~1-2 secondes pour l'entraînement + prédiction
- **Formats CSV** : Détection automatique virgule/point-virgule
- **Gestion des valeurs manquantes** : Imputation par la médiane

---

##  Support

En cas de problème, vérifiez que :
1. Python 3.7+ est installé
2. Toutes les dépendances sont installées (`pip install pandas numpy scikit-learn`)
3. Le fichier `billets.csv` est bien présent dans le même répertoire que le script
4. Votre fichier CSV contient les 6 colonnes requises (dans n'importe quel ordre)
5. Votre fichier CSV utilise bien la virgule `,` ou le point-virgule `;` comme séparateur

---

**Bonne détection ! **
