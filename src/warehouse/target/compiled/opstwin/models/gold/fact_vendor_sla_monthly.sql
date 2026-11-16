-- Grain: one vendor per calendar month.
select
    cast(strftime(m.month_start, '%Y%m%d') as integer) as date_key,
    v.vendor_key, m.month_start,
    m.avg_response_h, m.avg_resolution_h, m.sla_breach_pct, m.invoices_inr
from "opstwin"."staging"."stg_vendors_sla" m
join "opstwin"."gold"."dim_vendor" v on v.vendor_id = m.vendor_id