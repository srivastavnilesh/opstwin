with bounds as (
    select min(ts_utc)::date as d_min, max(ts_utc)::date as d_max
    from {{ ref('silver_telemetry') }}
),
days as (
    select unnest(generate_series(d_min, d_max, interval 1 day))::date as date_day
    from bounds
)
select
    cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
    date_day,
    year(date_day)      as year,
    quarter(date_day)   as quarter,
    month(date_day)     as month,
    day(date_day)       as day_of_month,
    dayofweek(date_day) as day_of_week,
    dayofweek(date_day) in (0, 6) as is_weekend,
    date_trunc('month', date_day)::date as month_start
from days