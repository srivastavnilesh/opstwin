with wo as (select * from "opstwin"."staging"."stg_work_orders"),
targets as (select * from "opstwin"."seeds"."sla_targets")
select
    wo.ticket_id,
    wo.site_id,
    wo.asset_id,
    wo.vendor_id,
    wo.category,
    wo.priority,
    wo.status,
    wo.opened_at_utc,
    wo.closed_at_utc,
    wo.cost_inr,
    t.target_resolution_hours,
    case when wo.closed_at_utc is not null
         then date_diff('minute', wo.opened_at_utc, wo.closed_at_utc) / 60.0
    end                                                        as resolution_hours,
    (wo.status = 'OPEN')                                       as is_open,
    case when wo.closed_at_utc is not null
         then date_diff('minute', wo.opened_at_utc, wo.closed_at_utc) / 60.0
              > t.target_resolution_hours
         else false
    end                                                        as is_sla_breach
from wo
left join targets t on t.priority = wo.priority