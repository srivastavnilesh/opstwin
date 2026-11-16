select
    row_number() over (order by se.sensor_id) as sensor_key,
    se.sensor_id, a.asset_key, s.site_key, se.metric, se.unit_nominal
from {{ ref('stg_sensors') }} se
join {{ ref('dim_asset') }} a on a.asset_id = se.asset_id
join {{ ref('dim_site') }}  s on s.site_id  = se.site_id