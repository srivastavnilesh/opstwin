-- Energy: hourly mean kW summed = kWh. Water: hourly mean L/min x 60 = litres.
with b as (
    select date_key, site_key,
           count(*)                                     as unit_days,
           sum(case when is_occupied then 1 else 0 end) as occupied_units,
           sum(revenue_inr)                             as revenue_inr
    from "opstwin"."gold"."fact_bookings" group by 1, 2
),
t as (
    select date_key, site_key,
           sum(case when metric = 'power' then value_normalized else 0 end)      as energy_kwh,
           sum(case when metric = 'water' then value_normalized * 60 else 0 end) as water_litres,
           avg(case when metric = 'temperature' then value_normalized end)       as avg_temp_c,
           sum(case when is_outlier then 1 else 0 end)                           as outlier_readings
    from "opstwin"."gold"."fact_telemetry" group by 1, 2
),
w as (
    select opened_date_key as date_key, site_key, count(*) as tickets_opened
    from "opstwin"."gold"."fact_work_orders" group by 1, 2
)
select
    d.date_day, s.site_id, s.site_name,
    b.unit_days, b.occupied_units,
    round(100.0 * b.occupied_units / nullif(b.unit_days, 0), 2) as occupancy_pct,
    b.revenue_inr,
    round(t.energy_kwh, 2)       as energy_kwh,
    round(t.water_litres, 2)     as water_litres,
    round(t.avg_temp_c, 2)       as avg_temp_c,
    t.outlier_readings,
    coalesce(w.tickets_opened, 0) as tickets_opened
from b
join t on t.date_key = b.date_key and t.site_key = b.site_key
join "opstwin"."gold"."dim_date" d on d.date_key = b.date_key
join "opstwin"."gold"."dim_site" s on s.site_key = b.site_key
left join w on w.date_key = b.date_key and w.site_key = b.site_key