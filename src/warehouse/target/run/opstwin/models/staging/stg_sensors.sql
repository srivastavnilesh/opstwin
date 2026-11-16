
  
  create view "opstwin"."staging"."stg_sensors__dbt_tmp" as (
    -- base_mu / base_sd are generator internals: excluded to prevent target leakage.
select
    sensor_id,
    site_id,
    asset_id,
    metric,
    unit as unit_nominal
from read_csv('data/bronze/operational/sensors.csv', header = true, auto_detect = true)
  );
