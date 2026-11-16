
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- Star joins must not drop or duplicate any silver reading.
with s as (select count(*) as n from "opstwin"."silver"."silver_telemetry"),
     f as (select count(*) as n from "opstwin"."gold"."fact_telemetry")
select s.n as silver_rows, f.n as fact_rows from s, f where s.n <> f.n
  
  
      
    ) dbt_internal_test