
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    site_key as unique_field,
    count(*) as n_records

from "opstwin"."gold"."dim_site"
where site_key is not null
group by site_key
having count(*) > 1



  
  
      
    ) dbt_internal_test