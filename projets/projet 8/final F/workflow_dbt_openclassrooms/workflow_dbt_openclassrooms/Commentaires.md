# Workflow dbt - Analyse Sociodémographique OpenClassrooms

##  Description du projet

Pipeline de transformation et d'analyse des données des étudiants inscrits aux parcours Data d'OpenClassrooms sur la période 2022-2025.

**Objectif** : Analyser l'évolution du profil sociodémographique (âge, genre, région) pour alimenter les réflexions stratégiques de l'entreprise.



##  Architecture technique

- **Entrepôt de données** : Snowflake
- **Base de données** : `OC_DATA_PROJECT`
- **Schéma source** : `RAW` (données brutes)
- **Schéma cible** : `DBT_NLUCIEN` (données transformées)
- **Outil de transformation** : dbt Cloud
- **Période analysée** : 2022-2025
- **Volume** : +4 000 étudiants



##  Structure du projet


workflow_dbt_openclassrooms/
├── Commentaires.md                                    # Ce fichier
├── dbt_project.yml                              # Configuration du projet dbt
├── models/
│   ├── staging/
│   │   └── openclassrooms/
│   │       ├── source.yml                       # Déclaration des sources de données
│   │       └── stg_students.sql                 # Nettoyage et normalisation
│   └── marts/
│       └── openclassrooms/
│           ├── fct_students_demo.sql            # Analyse par année
│           ├── fct_students_by_region.sql       # Analyse par région
│           ├── fct_students_by_age.sql          # Analyse par âge
│           └── fct_comparison_oc_insee.sql      # Comparaison avec INSEE
└── seeds/
    └── insee_population_regions.csv             # Données démographiques de référence




##  Pipeline de transformation

### 1️ **Staging (Nettoyage)**

**Fichier** : `models/staging/openclassrooms/stg_students.sql`

**Transformations appliquées** :
- Normalisation des genres (M → Homme, F → Femme, vide → Non renseigné)
- Nettoyage des valeurs textuelles (trim, uppercase)
- Filtrage des années valides (2022-2025)
- Dédoublonnage des USER_ID (garde la ligne la plus récente)

**Input** : Table brute `RAW.STUDENTS`  
**Output** : Table staging `DBT_NLUCIEN.stg_students`



### 2️ **Marts (Analyses)**

####  A. Démographie par année
**Fichier** : `models/marts/openclassrooms/fct_students_demo.sql`

**Agrégations** :
- Nombre total d'étudiants par année
- Pourcentage et nombre par genre (Homme, Femme, Non renseigné)

**Output** : `DBT_NLUCIEN.fct_students_demo`



####  B. Analyse par région
**Fichier** : `models/marts/openclassrooms/fct_students_by_region.sql`

**Agrégations** :
- Nombre total d'étudiants par région
- Répartition par genre par région
- Répartition par année par région

**Output** : `DBT_NLUCIEN.fct_students_by_region`



####  C. Analyse par âge
**Fichier** : `models/marts/openclassrooms/fct_students_by_age.sql`

**Agrégations** :
- Nombre total d'étudiants par tranche d'âge
- Répartition par genre par tranche d'âge
- Répartition par année par tranche d'âge

**Output** : `DBT_NLUCIEN.fct_students_by_age`



#### D. Comparaison INSEE
**Fichier** : `models/marts/openclassrooms/fct_comparison_oc_insee.sql`

**Enrichissement** :
- Jointure avec données démographiques INSEE
- Calcul des écarts de répartition hommes/femmes
- Ratio étudiants OC pour 100 000 habitants par région

**Output** : `DBT_NLUCIEN.fct_comparison_oc_insee`



### 3️ **Seeds (Données de référence)**

**Fichier** : `seeds/insee_population_regions.csv`

Données démographiques officielles INSEE 2023 :
- Population totale par région
- Pourcentage hommes/femmes par région



##  Exécution du pipeline

### Installation des dépendances
bash
dbt deps


### Chargement des données de référence
bash
dbt seed


### Exécution complète du pipeline
bash
dbt run


### Exécution ciblée
bash
# Seulement le staging
dbt run --select stg_students

# Seulement les marts
dbt run --select fct_students_demo fct_students_by_region fct_students_by_age fct_comparison_oc_insee

# Seulement une table spécifique
dbt run --select fct_students_demo


### Tests de qualité
bash
dbt test




##  Tests de qualité des données

### Tests appliqués sur les sources :
- `user_id` : unicité, non-nullité
- `year_path_started` : non-nullité, valeurs acceptables (2022, 2023, 2024, 2025)

### Tests appliqués sur les modèles :
- `stg_students.user_id` : unicité, non-nullité
- `fct_students_demo.year_path_started` : non-nullité, valeurs acceptables
- `fct_students_demo.total_etudiants` : non-nullité

**Tous les tests doivent passer avant la mise en production.**



##  Conformité RGPD

### Principes appliqués :

**Pseudonymisation**
- Les `USER_ID` sont pseudonymisés et ne permettent pas d'identifier directement les étudiants

 **Minimisation des données**
- Seules les données nécessaires à l'analyse sont collectées et conservées
- Pas de données sensibles (nom, prénom, email, adresse)

**Agrégation**
- Les analyses portent sur des groupes, pas sur des individus identifiables
- Les tables marts contiennent uniquement des statistiques agrégées

**Sécurité**
- Données stockées dans Snowflake avec contrôle d'accès
- Accès restreint aux seuls utilisateurs autorisés
- Logs d'accès et d'utilisation

 **Finalité**
- Les données sont utilisées uniquement pour l'analyse sociodémographique
- Pas de réutilisation à des fins commerciales ou marketing direct




##  Méthodologie de collecte

1. **Extraction** : Données extraites des bases internes OpenClassrooms (période 2022-2025)
2. **Import** : Chargement dans Snowflake (base `OC_DATA_PROJECT`, schéma `RAW`)
3. **Transformation** : Pipeline dbt pour nettoyage et agrégation
4. **Enrichissement** : Intégration des données démographiques INSEE
5. **Validation** : Tests de qualité et cohérence
6. **Export** : Tables analytiques finales + fichiers CSV



##  Technologies utilisées

- **Snowflake** : Entrepôt de données cloud
- **dbt Cloud** : Outil de transformation ELT
- **SQL** : Langage de transformation
- **Git** : Versioning du code
- **CSV** : Format d'export des résultats



##  Auteur

**Nzeutom Lucien**  
Data Analyst - Projet OpenClassrooms  
Date : Fevrier 2026



## Documentation complémentaire

- [dbt Documentation](https://docs.getdbt.com/)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [INSEE - Statistiques](https://www.insee.fr/fr/statistiques) sacahnt que ce fichier date de la population de 2021



##  Livrables du projet

1. **Workflow dbt** (ce dossier)
2. **Fichier CSV** consolidé 
3. **Présentation** PowerPoint (15 slides)



**Projet réalisé dans le cadre du parcours Data Analyst - OpenClassrooms :)**
