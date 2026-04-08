select published_date_il, data_source_clean, count(*) as row_count
from {{ ref('mart_data_source_daily') }}
group by 1, 2
having count(*) > 1
