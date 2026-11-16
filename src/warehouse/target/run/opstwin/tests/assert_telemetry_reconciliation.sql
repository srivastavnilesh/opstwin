
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Fails if any bronze row is unaccounted for after dedup, quarantine, and silver load.
with b as (select count(*) as n from "opstwin"."staging"."stg_telemetry"),
     c as (select count(*) as n from "opstwin"."silver"."int_telemetry_clean"),
     s as (select count(*) as n from "opstwin"."silver"."silver_telemetry"),
     q as (select count(*) as n from "opstwin"."silver"."silver_telemetry_quarantine")
select b.n as bronze_rows, c.n as deduped_rows, s.n as silver_rows, q.n as quarantine_rows
from b, c, s, q
where c.n <> s.n + q.n
   or b.n <= c.n
  
  
      
    ) dbt_internal_test