
    

    create  table
      "opstwin"."silver"."silver_telemetry__dbt_tmp"
  
    
    as (
      select
    c.reading_id,
    c.ts_utc,
    c.ingested_at_utc,
    c.site_id,
    c.sensor_id,
    c.asset_id,
    c.metric,
    c.value_normalized,
    c.unit_normalized,
    c.battery_pct,
    c.firmware,
    c.partition_month,
    c.is_late_arrival,
    c.hours_late,
    (abs(c.value_normalized - s.med_value)
        > greatest(4 * s.mad_value, 0.30 * s.med_value))    as is_outlier
from "opstwin"."silver"."int_telemetry_clean" c
join "opstwin"."silver"."int_sensor_stats" s on s.sensor_id = c.sensor_id
where c.value_normalized is not null
    );
    
  