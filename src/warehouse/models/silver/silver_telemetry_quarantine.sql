select
    reading_id,
    ts_utc,
    site_id,
    sensor_id,
    asset_id,
    metric,
    unit_raw,
    'NULL_VALUE'::varchar as quarantine_reason,
    current_timestamp     as quarantined_at_utc
from {{ ref('int_telemetry_clean') }}
where value_normalized is null