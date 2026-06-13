{{
    config(
        materialized='table',
        tags=['staging', 'openclassrooms', 'students']
    )
}}

WITH source AS (
    SELECT * FROM {{ source('openclassrooms', 'students') }}
),

dedup AS (
    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY year_path_started DESC) AS rn
        FROM source
    ) 
    WHERE rn = 1  -- garde la ligne la plus récente si doublon
),

cleaned AS (
    SELECT
        user_id,  -- RGPD : pseudonymisé
        UPPER(TRIM(path_category_name)) AS path_category_name,
        TRIM(age_group) AS age_group,
        CASE 
            WHEN gender IS NULL OR TRIM(gender) = '' THEN 'Non renseigné'
            WHEN UPPER(TRIM(gender)) = 'M' THEN 'Homme'
            WHEN UPPER(TRIM(gender)) = 'F' THEN 'Femme'
            ELSE 'Autre'
        END AS gender,
        TRIM(region) AS region,
        year_path_started
    FROM dedup
    WHERE year_path_started BETWEEN 2022 AND 2025
)

SELECT * FROM cleaned