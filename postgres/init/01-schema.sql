-- Create tables for conversation sessions
CREATE TABLE sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create table for conversation messages
CREATE TABLE conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    message_type VARCHAR(50) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    query_type VARCHAR(50), -- 'analytical', 'informational', 'conversational', 'existing_analysis'
    sql_query TEXT, -- Only for analytical responses
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for generated SQL queries (distinct from conversation)
CREATE TABLE sql_queries (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    query_hash VARCHAR(255) NOT NULL,
    natural_language_query TEXT NOT NULL,
    sql_query TEXT NOT NULL,
    complexity VARCHAR(50), -- 'SIMPLE' or 'COMPLEX'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(query_hash)
);

CREATE TABLE user_feedback (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES sessions(session_id),
    message_id INTEGER REFERENCES conversation_messages(id),
    rating INTEGER,
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indices for better query performance
CREATE INDEX idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX idx_conversation_messages_timestamp ON conversation_messages(timestamp);
CREATE INDEX idx_sql_queries_session_id ON sql_queries(session_id);
CREATE INDEX idx_sql_queries_query_hash ON sql_queries(query_hash);
CREATE INDEX idx_sessions_last_interaction ON sessions(last_interaction);

-- Create user roles
CREATE ROLE nl2sql_reader WITH LOGIN PASSWORD 'reader_password';
CREATE ROLE nl2sql_writer WITH LOGIN PASSWORD 'writer_password';

-- Grant permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO nl2sql_reader;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO nl2sql_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nl2sql_writer;