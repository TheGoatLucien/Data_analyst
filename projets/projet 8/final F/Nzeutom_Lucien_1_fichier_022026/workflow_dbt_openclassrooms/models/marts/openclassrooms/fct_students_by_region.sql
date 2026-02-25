
-- MODÈLE MART : ANALYSE PAR RÉGION

-- Description:
--   Ce modèle agrège les données étudiants par région pour identifier
--   les territoires avec le plus d'étudiants Data et analyser les disparités.
-- Métriques calculées:
--   - Nombre total d'étudiants par région
--   - Répartition par genre par région
--   - Répartition par année par région

-- Input:  DBT_NLUCIEN.stg_students
-- Output: DBT_NLUCIEN.fct_students_by_region

-- Utilisation:
--   - Cartes géographiques
--   - Top 10 des régions
--   - Stratégie de déploiement territorial



{{
    config(
        materialized='table',
        tags=['marts', 'analytics', 'region']
    )
}}

with students_data as (
    select * from {{ ref('stg_students') }}
),

demographics_by_region as (
    select
        -- Dimension : Région
        region,
        
        -- Métrique principale : Effectif total
        count(*) as total_etudiants,
        
        -- Répartition par genre (pourcentages)
        round(100.0 * sum(case when gender = 'Homme' then 1 else 0 end) / count(*), 2) as pct_hommes,
        round(100.0 * sum(case when gender = 'Femme' then 1 else 0 end) / count(*), 2) as pct_femmes,
        round(100.0 * sum(case when gender = 'Non renseigné' then 1 else 0 end) / count(*), 2) as pct_non_renseignes,
        
        -- Répartition par genre (nombres absolus)
        sum(case when gender = 'Homme' then 1 else 0 end) as nb_hommes,
        sum(case when gender = 'Femme' then 1 else 0 end) as nb_femmes,
        sum(case when gender = 'Non renseigné' then 1 else 0 end) as nb_non_renseignes,
        
        -- Répartition par année (nombres absolus)
        -- Utile pour voir l'évolution régionale dans le temps
        sum(case when year_path_started = 2022 then 1 else 0 end) as nb_2022,
        sum(case when year_path_started = 2023 then 1 else 0 end) as nb_2023,
        sum(case when year_path_started = 2024 then 1 else 0 end) as nb_2024,
        sum(case when year_path_started = 2025 then 1 else 0 end) as nb_2025
        
    from students_data
    group by region
)

select * from demographics_by_region
-- Tri par effectif décroissant pour faciliter l'identification du top régions
order by total_etudiants desc

