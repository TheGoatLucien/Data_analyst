{{
    config(
        materialized='table',
        tags=['marts', 'analytics']
    )
}}

with students_data as (
    select * from {{ ref('stg_students') }}
),

demographics_by_year as (
    select
        year_path_started,
        count(*) as total_etudiants,
        
        -- Pourcentages par genre
        round(100.0 * sum(case when gender = 'Homme' then 1 else 0 end) / count(*), 2) as pct_hommes,
        round(100.0 * sum(case when gender = 'Femme' then 1 else 0 end) / count(*), 2) as pct_femmes,
        round(100.0 * sum(case when gender = 'Non renseigné' then 1 else 0 end) / count(*), 2) as pct_non_renseignes,
        
        -- Nombres absolus par genre
        sum(case when gender = 'Homme' then 1 else 0 end) as nb_hommes,
        sum(case when gender = 'Femme' then 1 else 0 end) as nb_femmes,
        sum(case when gender = 'Non renseigné' then 1 else 0 end) as nb_non_renseignes
        
    from students_data
    group by year_path_started
)

select * from demographics_by_year
order by year_path_started