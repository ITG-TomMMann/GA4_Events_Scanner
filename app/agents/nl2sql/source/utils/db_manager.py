import os
import psycopg2
import psycopg2.extras
import hashlib
import json
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Tuple
import datetime

class DatabaseManager:
    """
    Handles database operations for NL2SQL conversation history.
    """
    def __init__(self):
        """Initialize database connection parameters from environment variables."""
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "nl2sql_db")
        self.user = os.getenv("DB_USER", "nl2sql_user")
        self.password = os.getenv("DB_PASSWORD", "nl2sql_password")
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logging.info(f"Connected to PostgreSQL database: {self.database}")
        except Exception as e:
            logging.error(f"Error connecting to PostgreSQL: {e}")
            raise
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor."""
        if self.conn is None or self.conn.closed:
            self._connect()
            
        cursor = None
        try:
            cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Database operation failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def create_or_update_session(self, session_id: str, metadata: Dict = None) -> str:
        """
        Create a new session or update an existing one.
        
        Args:
            session_id: Unique identifier for the session
            metadata: Optional metadata about the session
            
        Returns:
            session_id: The session ID (same as input)
        """
        try:
            with self.get_cursor() as cur:
                # Check if session exists
                cur.execute(
                    "SELECT session_id FROM sessions WHERE session_id = %s",
                    (session_id,)
                )
                
                if cur.fetchone():
                    # Update existing session
                    cur.execute(
                        "UPDATE sessions SET last_interaction = %s WHERE session_id = %s",
                        (datetime.datetime.now(), session_id)
                    )
                else:
                    # Create new session
                    cur.execute(
                        "INSERT INTO sessions (session_id, metadata) VALUES (%s, %s)",
                        (session_id, psycopg2.extras.Json(metadata) if metadata else None)
                    )
                    
            logging.info(f"Created or updated session: {session_id}")
            return session_id
        except Exception as e:
            logging.error(f"Error creating/updating session: {e}")
            raise
    
    def store_message(self, session_id: str, message_type: str, content: str, 
                     query_type: Optional[str] = None, sql_query: Optional[str] = None) -> int:
        """
        Store a message in the conversation history.
        
        Args:
            session_id: The session ID
            message_type: 'user' or 'assistant'
            content: The message content
            query_type: Optional query type classification
            sql_query: Optional SQL query (for assistant responses)
            
        Returns:
            id: The message ID
        """
        try:
            # Ensure session exists or create it
            self.create_or_update_session(session_id)
            
            with self.get_cursor() as cur:
                cur.execute(
                    "INSERT INTO conversation_messages (session_id, message_type, content, query_type, sql_query) "
                    "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (session_id, message_type, content, query_type, sql_query)
                )
                message_id = cur.fetchone()[0]
                
            logging.info(f"Stored {message_type} message for session {session_id}")
            return message_id
        except Exception as e:
            logging.error(f"Error storing message: {e}")
            raise
    
    def store_sql_query(self, session_id: str, natural_language_query: str, 
                       sql_query: str, complexity: str = "SIMPLE") -> str:
        """
        Store a generated SQL query.
        
        Args:
            session_id: The session ID
            natural_language_query: Original natural language query
            sql_query: Generated SQL query
            complexity: Query complexity ('SIMPLE' or 'COMPLEX')
            
        Returns:
            query_hash: MD5 hash of the natural language query
        """
        try:
            # Ensure session exists or create it
            self.create_or_update_session(session_id)
            
            # Generate hash for the query
            query_hash = hashlib.md5(natural_language_query.encode()).hexdigest()
            
            with self.get_cursor() as cur:
                cur.execute(
                    "INSERT INTO sql_queries (session_id, query_hash, natural_language_query, sql_query, complexity) "
                    "VALUES (%s, %s, %s, %s, %s) "
                    "ON CONFLICT (query_hash) DO UPDATE "
                    "SET sql_query = EXCLUDED.sql_query, "
                    "timestamp = CURRENT_TIMESTAMP, "
                    "complexity = EXCLUDED.complexity",
                    (session_id, query_hash, natural_language_query, sql_query, complexity)
                )
                
            logging.info(f"Stored SQL query with hash {query_hash}")
            return query_hash
        except Exception as e:
            logging.error(f"Error storing SQL query: {e}")
            raise
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Retrieve conversation history for a specific session.
        
        Args:
            session_id: The session ID
            
        Returns:
            List of conversation messages
        """
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    "SELECT id, message_type, content, query_type, sql_query, timestamp "
                    "FROM conversation_messages "
                    "WHERE session_id = %s "
                    "ORDER BY timestamp",
                    (session_id,)
                )
                
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logging.error(f"Error retrieving conversation history: {e}")
            return []
    
    def get_sql_query_by_hash(self, query_hash: str) -> Optional[Dict]:
        """
        Retrieve a SQL query by its hash.
        
        Args:
            query_hash: MD5 hash of the natural language query
            
        Returns:
            SQL query entry or None if not found
        """
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    "SELECT * FROM sql_queries WHERE query_hash = %s",
                    (query_hash,)
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logging.error(f"Error retrieving SQL query by hash: {e}")
            return None
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve information about a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session info or None if not found
        """
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    "SELECT * FROM sessions WHERE session_id = %s",
                    (session_id,)
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logging.error(f"Error retrieving session info: {e}")
            return None
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve recent sessions ordered by last interaction.
        
        Args:
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of recent sessions
        """
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    "SELECT session_id, created_at, last_interaction, metadata "
                    "FROM sessions "
                    "ORDER BY last_interaction DESC "
                    "LIMIT %s",
                    (limit,)
                )
                
                return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logging.error(f"Error retrieving recent sessions: {e}")
            return []
            
    def close(self):
        """Close the database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logging.info("Database connection closed")

# Create a singleton instance
db_manager = DatabaseManager()