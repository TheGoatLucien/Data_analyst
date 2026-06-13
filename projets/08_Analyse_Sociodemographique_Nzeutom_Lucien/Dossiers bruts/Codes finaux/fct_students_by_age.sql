{{
    config(
        materialized='table',
        tags=['marts', 'analytics', 'age']
    )
}}

with students_data as (
    select * from {{ ref('stg_students') }}
),

demographics_by_age as (
    select
        age_group,
        
        -- Totaux
        count(*) as total_etudiants,
        
        -- Répartition par genre (pourcentages)
        round(100.0 * sum(case when gender = 'Homme' then 1 else 0 end) / count(*), 2) as pct_hommes,
        round(100.0 * sum(case when gender = 'Femme' then 1 else 0 end) / count(*), 2) as pct_femmes,
        round(100.0 * sum(case when gender = 'Non renseigné' then 1 else 0 end) / count(*), 2) as pct_non_renseignes,
        
        -- Répartition par genre (nombres absolus)
        sum(case when gender = 'Homme' then 1 else 0 end) as nb_hommes,
        sum(case when gender = 'Femme' then 1 else 0 end) as nb_femmes,
        sum(case when gender = 'Non renseigné' then 1 else 0 end) as nb_non_renseignes,
        
        -- Répartition par année
        sum(case when year_path_started = 2022 then 1 else 0 end) as nb_2022,
        sum(case when year_path_started = 2023 then 1 else 0 end) as nb_2023,
        sum(case when year_path_started = 2024 then 1 else 0 end) as nb_2024,
        sum(case when year_path_started = 2025 then 1 else 0 end) as nb_2025,
        
        -- Pourcentage par année
        round(100.0 * sum(case when year_path_started = 2022 then 1 else 0 end) / count(*), 2) as pct_2022,
        round(100.0 * sum(case when year_path_started = 2023 then 1 else 0 end) / count(*), 2) as pct_2023,
        round(100.0 * sum(case when year_path_started = 2024 then 1 else 0 end) / count(*), 2) as pct_2024,
        round(100.0 * sum(case when year_path_started = 2025 then 1 else 0 end) / count(*), 2) as pct_2025
        
    from students_data
    group by age_group
)

select * from demographics_by_age
order by total_etudiants desc