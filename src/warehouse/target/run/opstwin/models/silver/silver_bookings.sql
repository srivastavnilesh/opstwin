
    

    create  table
      "opstwin"."silver"."silver_bookings__dbt_tmp"
  
    
    as (
      select
    booking_date,
    site_id,
    unit_id,
    is_occupied,
    adr_inr,
    channel,
    case when is_occupied then adr_inr else 0 end as revenue_inr
from "opstwin"."staging"."stg_bookings"
    );
    
  