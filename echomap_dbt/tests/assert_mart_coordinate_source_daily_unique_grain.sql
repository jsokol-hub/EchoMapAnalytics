select published_date_il, coordinate_source, count(*) as row_count
from {{ ref('mart_coordinate_source_daily') }}
group by 1, 2
having count(*) > 1
