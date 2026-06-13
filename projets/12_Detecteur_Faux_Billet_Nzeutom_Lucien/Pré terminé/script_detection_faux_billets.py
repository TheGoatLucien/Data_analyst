#!/usr/bin/env python3
"""
ONCFM — Algorithme de détection automatique de faux billets
Script de production pour prédire si des billets sont vrais ou faux

Modes d'utilisation :
    python script_detection_faux_billets.py --fichier billets.csv
    python script_detection_faux_billets.py --manuel

Auteur : Projet 12 - Détection de faux billets
"""

import pandas as pd
import numpy as np
import argparse
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION
# ============================================================================
FEATURES = ['diagonal', 'height_left', 'height_right', 'margin_low', 'margin_up', 'length']
TRAINING_FILE = 'billets.csv'


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def detect_csv_separator(filepath):
    """
    Détecte automatiquement le séparateur d'un fichier CSV.
    Gère les cas : virgule (,) et point-virgule (;)
    """
    with open(filepath, 'r') as f:
        first_line = f.readline()
    
    # Compte les séparateurs dans la première ligne
    comma_count = first_line.count(',')
    semicolon_count = first_line.count(';')
    
    if semicolon_count > comma_count:
        return ';'
    else:
        return ','


def load_csv_smart(filepath):
    """
    Charge un CSV avec détection automatique du séparateur.
    Gère les cas avec ou sans colonne 'is_genuine'.
    """
    separator = detect_csv_separator(filepath)
    df = pd.read_csv(filepath, sep=separator)
    
    print(f"   Format détecté : séparateur '{separator}'")
    print(f"   Colonnes trouvées : {', '.join(df.columns)}")
    
    return df


def validate_features(df, features_required):
    """
    Vérifie que toutes les colonnes nécessaires sont présentes.
    """
    missing = [f for f in features_required if f not in df.columns]
    if missing:
        print(f"\n ERREUR : Colonnes manquantes dans le fichier : {', '.join(missing)}")
        print(f"\nColonnes attendues : {', '.join(features_required)}")
        print(f"Colonnes trouvées   : {', '.join(df.columns)}")
        return False
    return True


def clean_data(df):
    """
    Nettoie les données : impute les valeurs manquantes par la médiane globale.
    """
    df = df.copy()  # Important: work on a copy
    n_missing_total = 0
    
    for col in FEATURES:
        n_missing = df[col].isnull().sum()
        if n_missing > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            n_missing_total += n_missing
            print(f"   → {n_missing} valeurs manquantes imputées dans '{col}' (médiane={median_val:.2f})")
    
    if n_missing_total == 0:
        print("   ✓ Aucune valeur manquante détectée")
    
    # Vérification finale
    remaining_nan = df[FEATURES].isnull().sum().sum()
    if remaining_nan > 0:
        print(f"    Attention : {remaining_nan} valeurs NaN restantes après imputation")
        # Imputation de secours : remplacer par 0
        df[FEATURES] = df[FEATURES].fillna(0)
        print(f"   → Imputation de secours appliquée (remplacement par 0)")
    
    return df


def train_model():
    """
    Entraîne le modèle de régression logistique sur le dataset d'entraînement.
    """
    # Vérifier que le fichier d'entraînement existe
    if not Path(TRAINING_FILE).exists():
        print(f"\n ERREUR : Le fichier d'entraînement '{TRAINING_FILE}' n'existe pas.")
        print(f"\nCe fichier est OBLIGATOIRE pour entraîner le modèle.")
        print(f"Assurez-vous qu'il est dans le même répertoire que le script.\n")
        sys.exit(1)
    
    # Charger les données d'entraînement
    df = load_csv_smart(TRAINING_FILE)
    
    # Vérifier que is_genuine existe
    if 'is_genuine' not in df.columns:
        print(f"\n ERREUR : Le fichier d'entraînement doit contenir la colonne 'is_genuine'.")
        sys.exit(1)
    
    # Vérifier les features
    if not validate_features(df, FEATURES):
        sys.exit(1)
    
    # Nettoyer les données
    df = clean_data(df)
    
    # Préparer X et y
    X = df[FEATURES]
    y = df['is_genuine'].astype(int)
    
    # Split train/test (pour afficher l'accuracy)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # Standardisation
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)
    
    # Entraînement
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_sc, y_train)
    
    # Évaluation sur le test
    accuracy = model.score(X_test_sc, y_test)
    
    return model, scaler, accuracy


def predict_bills(model, scaler, df):
    """
    Fait des prédictions sur un dataframe de billets.
    Retourne le dataframe avec les colonnes Résultat et Confiance (%).
    """
    X = df[FEATURES]
    X_scaled = scaler.transform(X)
    
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)
    
    # Ajouter les résultats
    df['Résultat'] = ['VRAI ✓' if p == 1 else 'FAUX ✗' for p in predictions]
    df['Confiance (%)'] = [max(proba) * 100 for proba in probabilities]
    
    return df


# ============================================================================
# MODE FICHIER
# ============================================================================

def mode_fichier(filepath):
    """
    Mode fichier : analyse un CSV contenant plusieurs billets.
    """
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     ONCFM — Détection automatique de faux billets              ║")
    print("║     Organisation nationale de lutte contre le faux-monnayage   ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")
    
    # Vérifier que le fichier existe
    if not Path(filepath).exists():
        print(f" Erreur : Le fichier '{filepath}' n'existe pas.\n")
        sys.exit(1)
    
    # Charger le fichier à analyser
    print(f" Fichier chargé : {filepath}")
    df = load_csv_smart(filepath)
    print(f"   Nombre de billets à analyser : {len(df)}")
    
    # Vérifier les colonnes
    if not validate_features(df, FEATURES):
        sys.exit(1)
    
    # Nettoyer si nécessaire
    has_missing = df[FEATURES].isnull().sum().sum() > 0
    if has_missing:
        print("\n  Valeurs manquantes détectées. Imputation en cours...")
        df = clean_data(df)
    
    print("=" * 70)
    
    # Entraîner le modèle
    print(" Entraînement du modèle en cours...")
    model, scaler, accuracy = train_model()
    print(f" Modèle entraîné avec succès (Régression Logistique)")
    print(f"   Accuracy sur le test : {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("=" * 70)
    print("\n RÉSULTATS DE L'ANALYSE :")
    print("-" * 70)
    
    # Faire les prédictions
    df_results = predict_bills(model, scaler, df)
    
    # Afficher les résultats
    display_cols = FEATURES + ['Résultat', 'Confiance (%)']
    if 'id' in df_results.columns:
        display_cols = ['id'] + display_cols
    
    print(df_results[display_cols].to_string(index=True))
    print("-" * 70)
    
    # Résumé
    n_vrais = (df_results['Résultat'] == 'VRAI ✓').sum()
    n_faux = (df_results['Résultat'] == 'FAUX ✗').sum()
    taux_faux = n_faux / len(df_results) * 100
    
    print("\n RÉSUMÉ :")
    print(f"    Billets identifiés comme VRAIS  : {n_vrais}")
    print(f"    Billets identifiés comme FAUX   : {n_faux}")
    print(f"     Taux de faux détectés           : {taux_faux:.1f}%")
    
    # Sauvegarder les résultats
    output_file = filepath.replace('.csv', '_resultats.csv')
    
    # Déterminer le séparateur pour la sortie (même que l'entrée)
    separator = detect_csv_separator(filepath)
    df_results.to_csv(output_file, index=False, sep=separator)
    
    print(f"\n Résultats sauvegardés dans : {output_file}")
    print()


# ============================================================================
# MODE MANUEL
# ============================================================================

def mode_manuel():
    """
    Mode manuel : saisie interactive des dimensions d'un billet.
    """
    print("=" * 70)
    print("  ONCFM — Vérification manuelle d'un billet")
    print("=" * 70)
    
    dimensions = {}
    labels = {
        'diagonal': 'Diagonale du billet (diagonal)',
        'height_left': 'Hauteur côté gauche (height_left)',
        'height_right': 'Hauteur côté droit (height_right)',
        'margin_low': 'Marge inférieure (margin_low)',
        'margin_up': 'Marge supérieure (margin_up)',
        'length': 'Longueur du billet (length)'
    }
    
    while True:
        print("\nEntrez les dimensions géométriques du billet (en mm) :")
        print("-" * 50)
        
        try:
            for feat in FEATURES:
                while True:
                    try:
                        value = float(input(f"  {labels[feat]} : "))
                        dimensions[feat] = value
                        break
                    except ValueError:
                        print("       Valeur invalide. Entrez un nombre (ex: 171.5)")
            
            # Créer un DataFrame
            df = pd.DataFrame([dimensions])
            
            # Entraîner le modèle
            print("\n Entraînement du modèle en cours...")
            model, scaler, accuracy = train_model()
            print(" Modèle entraîné avec succès")
            
            # Prédiction
            df_result = predict_bills(model, scaler, df)
            
            print("\n" + "=" * 70)
            resultat = df_result['Résultat'].values[0]
            confiance = df_result['Confiance (%)'].values[0]
            
            if resultat == 'VRAI ✓':
                print(f"    Le billet est identifié comme : {resultat}")
            else:
                print(f"    Le billet est identifié comme : {resultat}")
            
            print(f"    Niveau de confiance : {confiance:.2f}%")
            print("=" * 70)
            
            # Demander si l'utilisateur veut continuer
            continuer = input("\nVoulez-vous vérifier un autre billet ? (o/n) : ")
            if continuer.lower() != 'o':
                print("\nMerci d'avoir utilisé le système de détection ONCFM ! 👋\n")
                break
                
        except KeyboardInterrupt:
            print("\n\n  Opération annulée par l'utilisateur.\n")
            sys.exit(0)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ONCFM — Algorithme de détection automatique de faux billets",
        epilog="""
Exemples d'utilisation :
  python script_detection_faux_billets.py --fichier billets_production.csv
  python script_detection_faux_billets.py --manuel
        """
    )
    
    parser.add_argument(
        '--fichier', '-f',
        type=str,
        help="Chemin vers un fichier CSV contenant les dimensions des billets"
    )
    
    parser.add_argument(
        '--manuel', '-m',
        action='store_true',
        help="Mode manuel : saisie interactive des dimensions"
    )
    
    args = parser.parse_args()
    
    # Vérifier qu'au moins un mode est spécifié
    if not args.fichier and not args.manuel:
        parser.print_help()
        sys.exit(1)
    
    # Exécuter le mode approprié
    if args.fichier:
        mode_fichier(args.fichier)
    elif args.manuel:
        mode_manuel()


if __name__ == "__main__":
    main()
