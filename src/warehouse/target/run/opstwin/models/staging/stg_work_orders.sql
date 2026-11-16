
  
  create view "opstwin"."staging"."stg_work_orders__dbt_tmp" as (
    select
    ticket_id,
    site_id,
    asset_id,
    category,
    priority,
    status,
    vendor_id,
    cast(opened_at_utc as timestamptz) at time zone 'UTC' as opened_at_utc,
    cast(closed_at_utc as timestamptz) at time zone 'UTC' as closed_at_utc,
    cast(cost_inr as double)                              as cost_inr
from read_csv('data/bronze/operational/work_orders.csv', header = true, auto_detect = true)
  );
