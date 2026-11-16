
    

    create  table
      "opstwin"."gold"."fact_bookings__dbt_tmp"
  
    
    as (
      -- Grain: one unit per day.
select
    cast(strftime(b.booking_date, '%Y%m%d') as integer) as date_key,
    s.site_key, b.unit_id, b.is_occupied, b.adr_inr, b.revenue_inr, b.channel
from "opstwin"."silver"."silver_bookings" b
join "opstwin"."gold"."dim_site" s on s.site_id = b.site_id
    );
    
  