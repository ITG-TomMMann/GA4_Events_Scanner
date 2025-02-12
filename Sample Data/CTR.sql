DECLARE start_date_pre_change DATE DEFAULT DATE('2025-01-01'); 

DECLARE end_date_post_change DATE DEFAULT DATE('2025-01-30');

WITH CTE_sessions AS (
    SELECT DISTINCT
        h.market_code,
        h.visitor_id,
        h.session_id,
        h.page_path,
        s.device_category,
        s.channel_grouping,
        s.medium,
        h.hit_datetime AS visit_datetime,
        h.visit_start_date,

    FROM `jlr-dl-dxa.PRD_GA4.GA4_hit` h
    LEFT JOIN `jlr-dl-dxa.PRD_GA4.GA4_session` s
        ON h.session_id = s.session_id
    WHERE 
         h.visit_start_date BETWEEN start_date_pre_change AND end_date_post_change
        AND s.visit_start_date BETWEEN start_date_pre_change AND end_date_post_change
        AND h.market_code IN ("US", 'CA', 'GB')
        AND h.page_path IN ('www.landrover.ca/en/index.html', 'www.landrover.co.uk/index.html', 'www.landroverusa.com/index.html')
        AND h.brand = "Land Rover"
),

CTE_events AS (
    SELECT
        s.market_code,
        s.visitor_id,
        s.device_category,
        s.channel_grouping,
        s.medium,
        s.visit_start_date,
        s.session_id,
        hit.hit_datetime,
        CASE 
            WHEN hit.event_label LIKE "%ENTER :: HouseOfBrandHome__single-cta%" THEN "HouseOfBrands"
        END AS event_type,
        CASE 
            WHEN hit.entrance = 1 THEN hit.visitor_id
        END as bounced_visitor

    FROM CTE_sessions s
    JOIN `jlr-dl-dxa.PRD_GA4.GA4_hit` hit
        ON s.session_id = hit.session_id
        AND hit.hit_datetime > s.visit_datetime
    WHERE 
         hit.visit_start_date BETWEEN start_date_pre_change AND end_date_post_change
)

SELECT
    rc.market_code,
    rc.device_category,
    rc.channel_grouping,
    rc.medium, 
    COUNT(DISTINCT rc.visitor_id) AS total_page_visitors,
    COUNT(DISTINCT CASE WHEN e.event_type = "HouseOfBrands" THEN e.visitor_id END) AS HouseOfBrands,
    COUNT(DISTINCT e.bounced_visitor) AS total_bounced_visitor,
FROM CTE_sessions rc
LEFT JOIN CTE_events e 
    ON rc.visitor_id = e.visitor_id 

GROUP BY  1,2,3,4
