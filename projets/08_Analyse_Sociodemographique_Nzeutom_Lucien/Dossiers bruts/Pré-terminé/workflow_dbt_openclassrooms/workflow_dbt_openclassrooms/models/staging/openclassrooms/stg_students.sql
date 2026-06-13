
-- MODÈLE STAGING : NETTOYAGE ET NORMALISATION DES DONNÉES ÉTUDIANTS

-- Description:
--   Ce modèle transforme les données brutes de la table STUDENTS en données
--   propres et normalisées, prêtes pour l'analyse.

-- Transformations appliquées:
--   1. Normalisation des genres (M à Homme, F à Femme, vide à Non renseigné)
--   2. Nettoyage des valeurs textuelles (trim, uppercase)
--   3. Filtrage des années valides (2022-2025)
--   4. Dédoublonnage des USER_ID (garde la ligne la plus récente)

-- Input:  OC_DATA_PROJECT.RAW.STUDENTS (table source brute)
-- Output: DBT_NLUCIEN.stg_students (table staging nettoyée)



{{
    config(
        materialized='table',
        tags=['staging', 'openclassrooms', 'students']
    )
}}


-- CTE 1: Lecture de la source brute

-- Récupère toutes les données de la table source déclarée dans source.yml

with source as (
    select * from {{ source('openclassrooms', 'students') }}
),


-- CTE 2: Dédoublonnage

-- Certains USER_ID apparaissent plusieurs fois dans les données sources.
-- Cette étape garde uniquement la ligne la plus récente (année la plus élevée)
-- pour chaque étudiant.
-- Logique: row_number() attribue un numéro à chaque ligne par USER_ID,
-- ordonné par année décroissante. La ligne avec row_num=1 est la plus récente.

deduplicated as (
    select *,
        row_number() over (
            partition by user_id 
            order by year_path_started desc
        ) as row_num
    from source
    -- Filtrage préliminaire: on garde seulement les années d'analyse valides
    where year_path_started between 2022 and 2025
),


-- CTE 3: Nettoyage et normalisation

-- Transforme les données pour les rendre cohérentes et exploitables

cleaned as (
    select

        -- Identifiant étudiant

        -- Conservé tel quel (déjà pseudonymisé , conforme RGPD)
        user_id,
        
    
        -- Parcours
  
        -- Normalisation: conversion en majuscules et suppression des espaces
        -- Exple: "data" à "DATA", " Data " à "DATA"
        upper(trim(path_category_name)) as path_category_name,
        

        -- Classe d'âge

        -- Nettoyage: suppression des espaces superflus
        -- Exemple: " 30-34 ans " à"30-34 ans"
        trim(age_group) as age_group,
        

        -- Genre
   
        -- Normalisation et gestion des valeurs manquantes:
        --   - M → "Homme"
        --   - F → "Femme"
        --   - NULL ou vide à "Non renseigné"
     
        -- Cette normalisation facilite l'analyse et la lecture des résultats
        case 
            when gender is null or trim(gender) = '' then 'Non renseigné'
            when upper(trim(gender)) = 'M' then 'Homme'
            when upper(trim(gender)) = 'F' then 'Femme'
            else 'Autre'  -- Cas rare, par sécurité
        end as gender,
        
     
        -- Région
  
        -- Nettoyage: suppression des espaces superflus
        trim(region) as region,
        
        -- Année de début du parcours

        -- Conservée telle quelle (déjà validée par le filtrage dans deduplicated)
        year_path_started
        
    from deduplicated
    -- Garde seulement la ligne la plus récente par étudiant
    where row_num = 1
)


-- RÉSULTAT FINAL
-- Retourne les données nettoyées et normalisées

select * from cleaned




