
  
  create view "opstwin"."staging"."stg_telemetry__dbt_tmp" as (
    with src as (
    select *
    from read_csv(
        'data/bronze/telemetry/site=*/month=*/part.csv',
        header = true,
        auto_detect = true,
        hive_partitioning = true,
        union_by_name = true
    )
)
select
    cast(ts_utc as timestamptz) at time zone 'UTC'           as ts_utc,
    cast(ingested_at_utc as timestamptz) at time zone 'UTC'  as ingested_at_utc,
    site_id,
    sensor_id,
    asset_id,
    metric,
    cast(value as double)                                    as value_raw,
    unit                                                     as unit_raw,
    cast(battery_pct as double)                              as battery_pct,
    firmware,
    month                                                    as partition_month
from src
  );
