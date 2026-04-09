
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



