
-- MODÈLE MART : COMPARAISON OPENCLASSROOMS VS INSEE

-- Description:
--   Ce modèle enrichit les données OpenClassrooms avec les données
--   démographiques de l'INSEE pour contextualiser les résultats.

-- Enrichissements:
--   - Jointure avec données population INSEE par région
--   - Calcul des écarts de répartition hommes/femmes
--   - Calcul du ratio étudiants pour 100 000 habitants
-- Input:  - DBT_NLUCIEN.fct_students_by_region
--         - DBT_NLUCIEN.insee_population_regions (seed)
-- Output: DBT_NLUCIEN.fct_comparison_oc_insee

-- Utilisation:
--   - Benchmark avec la population française
--   - Identification des sur/sous-représentations
--   - Contextualisation des résultats



{{
    config(
        materialized='table',
        tags=['marts', 'analytics', 'comparison', 'insee']
    )
}}


-- CTE 1: Données OpenClassrooms par région


with oc_data as (
    select * from {{ ref('fct_students_by_region') }}
),


-- CTE 2: Données INSEE (population par région)


insee_data as (
    select * from {{ ref('insee_population_regions') }}
),


-- CTE 3: Comparaison et enrichissement


comparison as (
    select
        -- Dimension : Région
        -- coalesce() gère le cas où une région serait présente dans une source mais pas l'autre
        coalesce(oc.region, insee.region) as region,
        
      
        -- Données OpenClassrooms
      
        coalesce(oc.total_etudiants, 0) as oc_total_etudiants,
        coalesce(oc.pct_hommes, 0) as oc_pct_hommes,
        coalesce(oc.pct_femmes, 0) as oc_pct_femmes,
        
      
        -- Données INSEE
      
        coalesce(insee.population_totale, 0) as insee_population,
        coalesce(insee.pct_hommes_insee, 0) as insee_pct_hommes,
        coalesce(insee.pct_femmes_insee, 0) as insee_pct_femmes,
        
      
        -- Comparaisons calculées
      
        
        -- Écart de répartition hommes (OpenClassrooms vs France)
        -- Valeur positive = surreprésentation masculine chez OC
        -- Valeur négative = sous-représentation masculine chez OC
        round(oc.pct_hommes - insee.pct_hommes_insee, 2) as diff_pct_hommes,
        
        -- Écart de répartition femmes (OpenClassrooms vs France)
        -- Valeur positive = surreprésentation féminine chez OC
        -- Valeur négative = sous-représentation féminine chez OC
        round(oc.pct_femmes - insee.pct_femmes_insee, 2) as diff_pct_femmes,
        
      
        -- Métrique de pénétration
      
        
        -- Nombre d'étudiants OpenClassrooms pour 100 000 habitants
        -- Indicateur de "pénétration" d'OpenClassrooms dans la région
        -- Plus la valeur est élevée, plus OC est présent dans cette région
        --
        -- Exemple: Si 150, cela signifie qu'il y a 150 étudiants OC
        -- pour 100 000 habitants dans cette région
        round(
            (oc.total_etudiants::float / nullif(insee.population_totale, 0)) * 100000, 
            2
        ) as etudiants_pour_100k_hab
        
    from oc_data oc
    -- Full outer join pour inclure toutes les régions (OC et/ou INSEE)
    full outer join insee_data insee
        on oc.region = insee.region
)


-- RÉSULTAT FINAL


select * from comparison
-- Tri par effectif OC décroissant, en mettant les valeurs NULL à la fin
order by oc_total_etudiants desc nulls last




