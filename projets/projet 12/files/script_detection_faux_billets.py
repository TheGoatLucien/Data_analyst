#!/usr/bin/env python3
"""
============================================================
  ONCFM — Algorithme de détection automatique de faux billets
============================================================
  Organisation nationale de lutte contre le faux-monnayage

  UTILISATION :
  -------------
  1) Prédiction à partir d'un fichier CSV :
       python script_detection_faux_billets.py --fichier billets_production.csv

  2) Prédiction à partir de valeurs saisies manuellement :
       python script_detection_faux_billets.py --manuel

  FORMAT CSV ATTENDU (séparateur point-virgule) :
       diagonal;height_left;height_right;margin_low;margin_up;length
       171.81;104.86;104.95;4.52;2.89;112.83

  SORTIE :
  --------
  Pour chaque billet, le script affiche :
    - VRAI  ou  FAUX
    - La probabilité associée (confidence)
============================================================
"""

import sys
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import argparse
import warnings

warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================
FEATURES = ['diagonal', 'height_left', 'height_right', 'margin_low', 'margin_up', 'length']
TRAINING_DATA_PATH = 'billets.csv'  # Fichier d'entraînement

# ============================================================
# ENTRAÎNEMENT DU MODÈLE (fait une seule fois au démarrage)
# ============================================================
def entrainer_modele():
    """
    Charge les données d'entraînement, impute les valeurs manquantes,
    standardise et entraîne un modèle de régression logistique.
    Retourne le modèle et le scaler.
    """
    # Charger les données
    df = pd.read_csv(TRAINING_DATA_PATH, sep=';')

    # Imputation des valeurs manquantes (margin_low) par médiane par groupe
    df_clean = df.copy()
    for label in [True, False]:
        mask = (df_clean['is_genuine'] == label) & (df_clean['margin_low'].isnull())
        median_val = df_clean.loc[df_clean['is_genuine'] == label, 'margin_low'].median()
        df_clean.loc[mask, 'margin_low'] = median_val

    # Séparation X / y
    X = df_clean[FEATURES]
    y = df_clean['is_genuine'].astype(int)

    # Standardisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Entraînement du modèle (Régression Logistique — meilleure performance : 99.33%)
    modele = LogisticRegression(max_iter=1000, random_state=42)
    modele.fit(X_scaled, y)

    return modele, scaler


def predire(modele, scaler, X_input):
    """
    Prend un DataFrame avec les 6 caractéristiques géométriques.
    Retourne un DataFrame avec les prédictions et probabilités.
    """
    # Vérification des colonnes
    missing_cols = [c for c in FEATURES if c not in X_input.columns]
    if missing_cols:
        raise ValueError(f"Colonnes manquantes dans l'entrée : {missing_cols}")

    X = X_input[FEATURES].copy()

    # Imputation des valeurs manquantes (médiane globale du training — approche rapide)
    for col in FEATURES:
        if X[col].isnull().any():
            X[col].fillna(X[col].median(), inplace=True)

    # Standardisation
    X_scaled = scaler.transform(X)

    # Prédiction
    y_pred = modele.predict(X_scaled)
    y_prob = modele.predict_proba(X_scaled)

    # Construction du résultat
    resultats = pd.DataFrame({
        'diagonal': X_input['diagonal'].values,
        'height_left': X_input['height_left'].values,
        'height_right': X_input['height_right'].values,
        'margin_low': X_input['margin_low'].values,
        'margin_up': X_input['margin_up'].values,
        'length': X_input['length'].values,
        'Résultat': ['VRAI ✓' if p == 1 else 'FAUX ✗' for p in y_pred],
        'Confiance (%)': (np.max(y_prob, axis=1) * 100).round(2)
    })

    return resultats


def mode_fichier(chemin_fichier):
    """
    Mode fichier : lit un CSV et prédit pour tous les billets.
    """
    if not os.path.exists(chemin_fichier):
        print(f"❌ Erreur : Le fichier '{chemin_fichier}' n'existe pas.")
        sys.exit(1)

    try:
        X_input = pd.read_csv(chemin_fichier, sep=';')
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {e}")
        sys.exit(1)

    # Vérification du format
    missing = [c for c in FEATURES if c not in X_input.columns]
    if missing:
        print(f"❌ Colonnes manquantes dans le fichier : {missing}")
        print(f"   Colonnes attendues : {FEATURES}")
        sys.exit(1)

    print(f"\n📂 Fichier chargé : {chemin_fichier}")
    print(f"   Nombre de billets à analyser : {len(X_input)}")
    print("=" * 70)

    # Entraînement du modèle
    print("🔄 Entraînement du modèle en cours...")
    modele, scaler = entrainer_modele()
    print("✅ Modèle entraîné avec succès (Régression Logistique)")
    print("=" * 70)

    # Prédiction
    resultats = predire(modele, scaler, X_input)

    # Affichage
    print("\n📊 RÉSULTATS DE L'ANALYSE :")
    print("-" * 70)
    print(resultats.to_string(index=True))
    print("-" * 70)

    # Résumé
    n_vrais = (resultats['Résultat'] == 'VRAI ✓').sum()
    n_faux = (resultats['Résultat'] == 'FAUX ✗').sum()
    print(f"\n📋 RÉSUMÉ :")
    print(f"   ✅ Billets identifiés comme VRAIS  : {n_vrais}")
    print(f"   ❌ Billets identifiés comme FAUX   : {n_faux}")
    print(f"   📊 Taux de faux détectés           : {n_faux/len(resultats)*100:.1f}%")

    # Sauvegarde des résultats
    output_file = chemin_fichier.replace('.csv', '_resultats.csv')
    resultats.to_csv(output_file, sep=';', index=False)
    print(f"\n💾 Résultats sauvegardés dans : {output_file}")

    return resultats


def mode_manuel():
    """
    Mode manuel : l'utilisateur saisit les dimensions d'un billet.
    """
    print("\n" + "=" * 70)
    print("  ONCFM — Vérification manuelle d'un billet")
    print("=" * 70)
    print("\nEntrez les dimensions géométriques du billet (en mm) :")
    print("-" * 50)

    valeurs = {}
    descriptions = {
        'diagonal': 'Diagonale du billet',
        'height_left': 'Hauteur côté gauche',
        'height_right': 'Hauteur côté droit',
        'margin_low': 'Marge inférieure',
        'margin_up': 'Marge supérieure',
        'length': 'Longueur du billet'
    }

    for feat in FEATURES:
        while True:
            try:
                val = input(f"  {descriptions[feat]} ({feat}) : ")
                valeurs[feat] = float(val)
                break
            except ValueError:
                print("  ⚠️  Veuillez entrer un nombre valide.")

    # Créer le DataFrame
    X_input = pd.DataFrame([valeurs])

    # Entraînement du modèle
    print("\n🔄 Entraînement du modèle en cours...")
    modele, scaler = entrainer_modele()
    print("✅ Modèle entraîné avec succès")

    # Prédiction
    resultats = predire(modele, scaler, X_input)

    # Affichage du résultat
    resultat = resultats.iloc[0]
    print("\n" + "=" * 70)
    if 'VRAI' in resultat['Résultat']:
        print(f"  ✅  Le billet est identifié comme : VRAI")
    else:
        print(f"  ❌  Le billet est identifié comme : FAUX")
    print(f"  📊  Niveau de confiance : {resultat['Confiance (%)']}%")
    print("=" * 70)

    # Option : vérifier un autre billet
    while True:
        autre = input("\nVoulez-vous vérifier un autre billet ? (o/n) : ").strip().lower()
        if autre in ['o', 'oui', 'yes', 'y']:
            mode_manuel()
            return
        elif autre in ['n', 'non', 'no']:
            print("\n👋 Au revoir !")
            return
        else:
            print("  Répondez par 'o' (oui) ou 'n' (non).")


def main():
    """
    Point d'entrée principal du script.
    """
    parser = argparse.ArgumentParser(
        description='ONCFM — Algorithme de détection automatique de faux billets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python script_detection_faux_billets.py --fichier billets_production.csv
  python script_detection_faux_billets.py --manuel
        """
    )

    parser.add_argument(
        '--fichier', '-f',
        type=str,
        help='Chemin vers un fichier CSV contenant les dimensions des billets'
    )
    parser.add_argument(
        '--manuel', '-m',
        action='store_true',
        help='Mode manuel : saisie interactive des dimensions'
    )

    args = parser.parse_args()

    # Vérification que le fichier d'entraînement existe
    if not os.path.exists(TRAINING_DATA_PATH):
        print(f"❌ Erreur : Le fichier d'entraînement '{TRAINING_DATA_PATH}' n'existe pas.")
        print("   Assurez-vous que 'billets.csv' est dans le même répertoire que ce script.")
        sys.exit(1)

    # Affichage de la bannière
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║     ONCFM — Détection automatique de faux billets              ║")
    print("║     Organisation nationale de lutte contre le faux-monnayage   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    if args.fichier:
        mode_fichier(args.fichier)
    elif args.manuel:
        mode_manuel()
    else:
        # Si aucun argument : afficher l'aide
        parser.print_help()
        print("\n💡 Conseil : utilisez '--fichier' pour un fichier CSV ou '--manuel' pour une saisie interactive.")


if __name__ == '__main__':
    main()
