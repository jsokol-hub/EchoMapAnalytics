select
    geoname,
    final_lat,
    final_lon,
    final_geom,
    coordinate_source,
    count(*) as row_count
from {{ ref('mart_location_summary') }}
group by 1, 2, 3, 4, 5
having count(*) > 1
