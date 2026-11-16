with w as (
    select vendor_key,
           count(*)                                      as tickets,
           avg(resolution_hours)                         as avg_resolution_hours,
           sum(case when is_sla_breach then 1 else 0 end) as breaches,
           sum(cost_inr)                                 as spend_inr
    from "opstwin"."gold"."fact_work_orders" group by 1
),
m as (
    select vendor_key, avg(sla_breach_pct) as reported_breach_pct, sum(invoices_inr) as invoiced_inr
    from "opstwin"."gold"."fact_vendor_sla_monthly" group by 1
)
select
    v.vendor_id, v.vendor_name, v.service_tier,
    w.tickets,
    round(w.avg_resolution_hours, 2)                   as avg_resolution_hours,
    w.breaches,
    round(100.0 * w.breaches / nullif(w.tickets, 0), 2) as breach_pct,
    round(m.reported_breach_pct, 2)                     as reported_breach_pct,
    w.spend_inr, m.invoiced_inr
from w
join "opstwin"."gold"."dim_vendor" v on v.vendor_key = w.vendor_key
left join m on m.vendor_key = w.vendor_key