
-- MODÈLE MART : ANALYSE PAR TRANCHE D'ÂGE

-- Description:
--   Ce modèle agrège les données étudiants par tranche d'âge pour identifier
--   le profil d'âge typique des étudiants en reconversion data.
--
-- Métriques calculées:
--   - Nombre total d'étudiants par tranche d'âge
--   - Répartition par genre par tranche d'âge
--   - Répartition par année par tranche d'âge
--
-- Input:  DBT_NLUCIEN.stg_students
-- Output: DBT_NLUCIEN.fct_students_by_age
--
-- Utilisation:
--   - Pyramide des âges
--   - Ciblage marketing par âge
--   - Adaptation du contenu pédagogique
--
-- Auteur: Nzeutom Lucien
-- Date: Janvier 2026


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
        -- Dimension : Tranche d'âge
        age_group,
        
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
        sum(case when year_path_started = 2022 then 1 else 0 end) as nb_2022,
        sum(case when year_path_started = 2023 then 1 else 0 end) as nb_2023,
        sum(case when year_path_started = 2024 then 1 else 0 end) as nb_2024,
        sum(case when year_path_started = 2025 then 1 else 0 end) as nb_2025,
        
        -- Répartition par année (pourcentages)
        -- Permet de voir l'évolution du profil d'âge dans le temps
        round(100.0 * sum(case when year_path_started = 2022 then 1 else 0 end) / count(*), 2) as pct_2022,
        round(100.0 * sum(case when year_path_started = 2023 then 1 else 0 end) / count(*), 2) as pct_2023,
        round(100.0 * sum(case when year_path_started = 2024 then 1 else 0 end) / count(*), 2) as pct_2024,
        round(100.0 * sum(case when year_path_started = 2025 then 1 else 0 end) / count(*), 2) as pct_2025
        
    from students_data
    group by age_group
)

select * from demographics_by_age
-- Tri par effectif décroissant
order by total_etudiants desc


-- INSIGHTS ATTENDUS

--
-- 1. PROFIL D'ÂGE CIBLE:
--    - 25-34 ans devrait être la tranche dominante (~55-60%)
--    - Âge idéal pour la reconversion professionnelle
--    - Déjà quelques années d'expérience + capacité d'apprentissage
--
-- 2. TRANCHES SECONDAIRES:
--    - 35-44 ans: ~25-30% (reconversion milieu de carrière)
--    - 45+ ans: ~10-15% (reconversion tardive, plus rare)
--
-- 3. JEUNES DIPLÔMÉS:
--    - 18-24 ans: faible proportion (<5%)
--    - Préfèrent généralement formation initiale classique
--
-- 4. SENIORS:
--    - 55+ ans: très faible (<2%)
--    - Proche de la retraite, moins enclins à la reconversion
--

-- RECOMMANDATIONS

--
-- 1. COMMUNICATION CIBLÉE:
--    - Messages adaptés aux 25-34 ans (motivation, success stories)
--    - Rassurer les 35+ sur leur capacité d'apprentissage
--
-- 2. CONTENU PÉDAGOGIQUE:
--    - Exemples de cas d'usage variés (startup, grands groupes, freelance)
--    - Accompagnement renforcé pour les profils 45+
--
-- 3. PARTENARIATS:
--    - Entreprises qui recrutent des juniors (25-34 ans)
--    - Programmes de reconversion interne (35-44 ans)
--

