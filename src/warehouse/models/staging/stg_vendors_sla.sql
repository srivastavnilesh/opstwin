select
    vendor_id,
    strptime(month || '-01', '%Y-%m-%d')::date as month_start,
    cast(avg_response_h as double)             as avg_response_h,
    cast(avg_resolution_h as double)           as avg_resolution_h,
    cast(sla_breach_pct as double)             as sla_breach_pct,
    cast(invoices_inr as bigint)               as invoices_inr
from read_csv('{{ var("bronze_root") }}/vendor_sla/vendor_sla.csv', header = true, auto_detect = true)