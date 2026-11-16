

with deduped as (
    select *
    from "opstwin"."staging"."stg_telemetry"
    qualify row_number() over (
        partition by sensor_id, ts_utc
        order by ingested_at_utc asc
    ) = 1
)
select
    sensor_id || '|' || strftime(ts_utc, '%Y-%m-%dT%H:%M:%S') as reading_id,
    ts_utc,
    ingested_at_utc,
    site_id,
    sensor_id,
    asset_id,
    metric,
    case
        when metric = 'temperature' and unit_raw = 'F' then (value_raw - 32.0) * 5.0 / 9.0
        else value_raw
    end                                                     as value_normalized,
    case
        when metric = 'temperature' then 'C'
        else unit_raw
    end                                                     as unit_normalized,
    value_raw,
    unit_raw,
    battery_pct,
    firmware,
    partition_month,
    (ingested_at_utc > ts_utc)                              as is_late_arrival,
    date_diff('hour', ts_utc, ingested_at_utc)              as hours_late
from deduped