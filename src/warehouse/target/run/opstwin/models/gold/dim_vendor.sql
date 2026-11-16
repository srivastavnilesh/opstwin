
    

    create  table
      "opstwin"."gold"."dim_vendor__dbt_tmp"
  
    
    as (
      select
    row_number() over (order by vendor_id) as vendor_key,
    vendor_id, vendor_name, service_tier
from "opstwin"."seeds"."vendors"
    );
    
  