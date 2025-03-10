-- Insert sample sessions
INSERT INTO sessions (session_id, created_at, last_interaction, metadata)
VALUES
    ('test-session-1', '2025-02-15 14:00:00', '2025-02-15 14:10:00', '{"user_agent": "Chrome", "ip": "192.168.1.1"}'),
    ('test-session-2', '2025-02-20 09:00:00', '2025-02-20 09:05:00', '{"user_agent": "Firefox", "ip": "192.168.1.2"}');

-- Insert sample conversation messages for session 1
INSERT INTO conversation_messages (session_id, message_type, content, query_type, sql_query, timestamp)
VALUES
    ('test-session-1', 'user', 'How many visitors were there in the US market in January 2025?', 'analytical', NULL, '2025-02-15 14:00:00'),
    ('test-session-1', 'assistant', 'Here''s the SQL query to find the number of visitors in the US market in January 2025:', 'analytical', 'SELECT COUNT(DISTINCT visitor_id) AS visitor_count FROM GA4_session WHERE market_code = ''US'' AND visit_start_date BETWEEN ''2025-01-01'' AND ''2025-01-31''', '2025-02-15 14:00:05'),
    ('test-session-1', 'user', 'Can you break that down by device category?', 'analytical', NULL, '2025-02-15 14:05:00'),
    ('test-session-1', 'assistant', 'Here''s the SQL query to break down visitors by device category:', 'analytical', 'SELECT device_category, COUNT(DISTINCT visitor_id) AS visitor_count FROM GA4_session WHERE market_code = ''US'' AND visit_start_date BETWEEN ''2025-01-01'' AND ''2025-01-31'' GROUP BY device_category ORDER BY visitor_count DESC', '2025-02-15 14:05:05');

-- Insert sample conversation messages for session 2
INSERT INTO conversation_messages (session_id, message_type, content, query_type, sql_query, timestamp)
VALUES
    ('test-session-2', 'user', 'What capabilities do you have?', 'informational', NULL, '2025-02-20 09:00:00'),
    ('test-session-2', 'assistant', 'I can help you analyze your GA4 data by generating SQL queries. You can ask me to retrieve metrics like visitor counts, session durations, and engagement rates. I can break down data by dimensions like market, device, campaign, and time periods. Just describe what you''d like to analyze in plain language, and I''ll generate the appropriate SQL query for you.', 'informational', NULL, '2025-02-20 09:00:05');

-- Insert sample SQL queries
INSERT INTO sql_queries (session_id, query_hash, natural_language_query, sql_query, complexity, timestamp)
VALUES
    ('test-session-1', 'e9c12d738cc940fe8d1fd881d7da500b', 'How many visitors were there in the US market in January 2025?', 'SELECT COUNT(DISTINCT visitor_id) AS visitor_count FROM GA4_session WHERE market_code = ''US'' AND visit_start_date BETWEEN ''2025-01-01'' AND ''2025-01-31''', 'SIMPLE', '2025-02-15 14:00:05'),
    ('test-session-1', 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6', 'Can you break that down by device category?', 'SELECT device_category, COUNT(DISTINCT visitor_id) AS visitor_count FROM GA4_session WHERE market_code = ''US'' AND visit_start_date BETWEEN ''2025-01-01'' AND ''2025-01-31'' GROUP BY device_category ORDER BY visitor_count DESC', 'SIMPLE', '2025-02-15 14:05:05');