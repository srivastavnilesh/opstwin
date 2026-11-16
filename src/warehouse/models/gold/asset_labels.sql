select
    row_number() over (order by a.asset_id) as asset_key,
    a.asset_id, s.site_key, a.asset_type, a.commissioned_year
from {{ ref('stg_assets') }} a
join {{ ref('dim_site') }} s on s.site_id = a.site_id