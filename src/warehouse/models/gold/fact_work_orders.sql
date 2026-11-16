-- Grain: one maintenance ticket.
select
    w.ticket_id,
    cast(strftime(w.opened_at_utc::date, '%Y%m%d') as integer) as opened_date_key,
    s.site_key, a.asset_key, v.vendor_key,
    w.category, w.priority, w.status,
    w.opened_at_utc, w.closed_at_utc,
    w.resolution_hours, w.target_resolution_hours,
    w.is_sla_breach, w.is_open, w.cost_inr
from {{ ref('silver_work_orders') }} w
join {{ ref('dim_site') }}   s on s.site_id   = w.site_id
join {{ ref('dim_asset') }}  a on a.asset_id  = w.asset_id
join {{ ref('dim_vendor') }} v on v.vendor_id = w.vendor_id