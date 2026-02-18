{{
    config(
        materialized='table',
        tags=['marts', 'analytics', 'comparison']
    )
}}

with oc_data as (
    select * from {{ ref('fct_students_by_region') }}
),

insee_data as (
    select * from {{ ref('insee_population_regions') }}
),

comparison as (
    select
        coalesce(oc.region, insee.region) as region,
        
        -- Données OpenClassrooms
        coalesce(oc.total_etudiants, 0) as oc_total_etudiants,
        coalesce(oc.pct_hommes, 0) as oc_pct_hommes,
        coalesce(oc.pct_femmes, 0) as oc_pct_femmes,
        
        -- Données INSEE
        coalesce(insee.population_totale, 0) as insee_population,
        coalesce(insee.pct_hommes_insee, 0) as insee_pct_hommes,
        coalesce(insee.pct_femmes_insee, 0) as insee_pct_femmes,
        
        -- Comparaisons
        round(oc.pct_hommes - insee.pct_hommes_insee, 2) as diff_pct_hommes,
        round(oc.pct_femmes - insee.pct_femmes_insee, 2) as diff_pct_femmes,
        
        -- Part des étudiants OC dans la population régionale (pour 100 000 habitants)
        round((oc.total_etudiants::float / insee.population_totale) * 100000, 2) as etudiants_pour_100k_hab
        
    from oc_data oc
    full outer join insee_data insee
        on oc.region = insee.region
)

select * from comparison
order by oc_total_etudiants desc nulls last