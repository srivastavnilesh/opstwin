
  
  create view "opstwin"."staging"."stg_assets__dbt_tmp" as (
    select
    asset_id,
    site_id,
    asset_type,
    health_state,
    cast(commissioned_year as integer) as commissioned_year
from read_csv('data/bronze/operational/assets.csv', header = true, auto_detect = true)
  );
