select
    row_number() over (order by a.asset_id) as asset_key,
    a.asset_id, s.site_key, a.asset_type, a.commissioned_year
from "opstwin"."staging"."stg_assets" a
join "opstwin"."gold"."dim_site" s on s.site_id = a.site_id