
-- MODÈLE MART : ANALYSE DÉMOGRAPHIQUE PAR ANNÉE

-- Description:
--   Ce modèle agrège les données étudiants par année pour produire
--   des statistiques démographiques (effectifs, répartition par genre).
--
-- Métriques calculées:
--   - Nombre total d'étudiants par année
--   - Pourcentage et nombre d'hommes, femmes, non renseignés
--
-- Input:  DBT_NLUCIEN.stg_students (table staging nettoyée)
-- Output: DBT_NLUCIEN.fct_students_demo (table analytique)
--
-- Utilisation:
--   - Graphiques d'évolution temporelle
--   - Analyse de la féminisation des parcours Data
--   - Tableau de bord KPI
--
-- Auteur: Nzeutom Lucien
-- Date: Janvier 2026


{{
    config(
        materialized='table',
        tags=['marts', 'analytics', 'demo']
    )
}}

-- CTE 1: Récupération des données staging

-- Lecture de la table staging nettoyée

with students_data as (
    select * from {{ ref('stg_students') }}
),

-- CTE 2: Agrégations démographiques par année
-- Calcule toutes les métriques démographiques pour chaque année

demographics_by_year as (
    select
       
        -- Dimension : Année
    
        year_path_started,
        
       
        -- Métrique 1 : Effectif total

        -- Nombre total d'étudiants inscrits cette année
        count(*) as total_etudiants,
        
      
        -- Métriques 2-4 : Répartition par genre (%)

        -- Pourcentage d'hommes
        -- Calcul: (nombre d'hommes / total) * 100
        -- Arrondi à 2 décimales pour la lisibilité
        round(
            100.0 * sum(case when gender = 'Homme' then 1 else 0 end) / count(*), 
            2
        ) as pct_hommes,
        
        -- Pourcentage de femmes
        round(
            100.0 * sum(case when gender = 'Femme' then 1 else 0 end) / count(*), 
            2
        ) as pct_femmes,
        
        -- Pourcentage de genres non renseignés
        round(
            100.0 * sum(case when gender = 'Non renseigné' then 1 else 0 end) / count(*), 
            2
        ) as pct_non_renseignes,
   
        -- Métriques 5-7 : Nombre absolu par genre
        -- Ces métriques complètent les pourcentages avec les effectifs réels
        
        -- Nombre d'hommes
        sum(case when gender = 'Homme' then 1 else 0 end) as nb_hommes,
        
        -- Nombre de femmes
        sum(case when gender = 'Femme' then 1 else 0 end) as nb_femmes,
        
        -- Nombre de genres non renseignés
        sum(case when gender = 'Non renseigné' then 1 else 0 end) as nb_non_renseignes
        
    from students_data
    -- Agrégation par année
    group by year_path_started
)


-- RÉSULTAT FINAL
-- Retourne les statistiques triées par année croissante

select * from demographics_by_year
order by year_path_started



-- INSIGHTS CLÉS

--
-- 1. ÉVOLUTION DES EFFECTIFS:
--    - Baisse de 50% entre 2022 (1696) et 2024 (850)
--    - Légère reprise en 2025 (+12% vs 2024)
--
-- 2. FÉMINISATION PROGRESSIVE:
--    - Part des femmes: 17.81% (2022) → 30.60% (2025)
--    - Croissance relative: +72%
--    - Tendance positive et continue
--
-- 3. AMÉLIORATION DE LA QUALITÉ DES DONNÉES:
--    - Non renseignés: 41.63% (2022) → 6.73% (2025)
--    - Réduction spectaculaire de 84%
--    - Meilleure collecte des informations à l'inscription
--
-- 4. PRÉDOMINANCE MASCULINE DÉCROISSANTE:
--    - Part des hommes stable autour de 60-65%
--    - Léger recul en valeur absolue mais maintien en proportion
--

-- RECOMMANDATIONS

--
-- 1. Continuer les efforts de féminisation:
--    - Témoignages de femmes data analysts
--    - Communication ciblée sur les réseaux sociaux
--    - Partenariats avec associations de femmes dans la tech
--
-- 2. Analyser les causes de la baisse d'effectifs:
--    - Concurrence accrue d'autres formations ?
--    - Prix perçu comme élevé ?
--    - Saturation du marché de la reconversion data ?
--
-- 3. Maintenir la qualité de la collecte de données:
--    - Champs obligatoires lors de l'inscription
--    - Validation des données saisies
--

-- UTILISATION DANS LES ANALYSES

--
-- Cette table est utilisée pour:
-- 1. Graphiques de la présentation PowerPoint
-- 2. Tableau de bord de suivi des KPI
-- 3. Rapport annuel de l'équipe pédagogique
-- 4. Benchmarks avec d'autres formations data

