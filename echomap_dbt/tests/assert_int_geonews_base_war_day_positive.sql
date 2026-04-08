-- Fails if any row has war_day_number missing or before day 1 of the window.
select news_id, war_day_number
from {{ ref('int_geonews_base') }}
where war_day_number is null
   or war_day_number < 1
