-- Grain: one sensor reading per hour.
select
    t.reading_id,
    cast(strftime(t.ts_utc::date, '%Y%m%d') as integer) as date_key,
    s.site_key, a.asset_key, se.sensor_key,
    t.ts_utc, t.metric, t.value_normalized, t.unit_normalized,
    t.battery_pct, t.firmware, t.is_late_arrival, t.hours_late, t.is_outlier
from {{ ref('silver_telemetry') }} t
join {{ ref('dim_site') }}   s  on s.site_id    = t.site_id
join {{ ref('dim_asset') }}  a  on a.asset_id   = t.asset_id
join {{ ref('dim_sensor') }} se on se.sensor_id = t.sensor_id