with t as (
    select a.asset_key, d.month_start,
           avg(case when f.metric = 'vibration' then f.value_normalized end) as avg_vibration,
           max(case when f.metric = 'vibration' then f.value_normalized end) as max_vibration,
           avg(case when f.metric = 'power'     then f.value_normalized end) as avg_power_kw,
           sum(case when f.is_outlier then 1 else 0 end)                     as outlier_readings
    from "opstwin"."gold"."fact_telemetry" f
    join "opstwin"."gold"."dim_asset" a on a.asset_key = f.asset_key
    join "opstwin"."gold"."dim_date"  d on d.date_key  = f.date_key
    group by 1, 2
),
w as (
    select asset_key, date_trunc('month', opened_at_utc)::date as month_start,
           count(*) as tickets, avg(resolution_hours) as mttr_hours, sum(cost_inr) as maintenance_cost_inr
    from "opstwin"."gold"."fact_work_orders" group by 1, 2
)
select
    a.asset_id, a.asset_type, s.site_id, t.month_start,
    round(t.avg_vibration, 3) as avg_vibration,
    round(t.max_vibration, 3) as max_vibration,
    round(t.avg_power_kw, 3)  as avg_power_kw,
    t.outlier_readings,
    coalesce(w.tickets, 0)    as tickets,
    round(w.mttr_hours, 2)    as mttr_hours,
    w.maintenance_cost_inr
from t
join "opstwin"."gold"."dim_asset" a on a.asset_key = t.asset_key
join "opstwin"."gold"."dim_site"  s on s.site_key  = a.site_key
left join w on w.asset_key = t.asset_key and w.month_start = t.month_start