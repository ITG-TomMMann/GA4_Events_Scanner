import pytest
from fastapi.testclient import TestClient
from source.main import app
from unittest.mock import patch
import json

client = TestClient(app)

@patch('source.query_agent.generate_sql')
@patch('source.rag.retrieval.retrieve_examples')
@patch('source.schema_agent.get_schema')
def test_handle_query(mock_get_schema, mock_retrieve_examples, mock_generate_sql):
    mock_get_schema.return_value = {"users": {"columns": ["id", "name"]}}
    mock_retrieve_examples.return_value = []
    mock_generate_sql.return_value = "SELECT * FROM users;"

    response = client.post(
        "/query",
        json={"query": "Get all users", "session_id": "test_session"}
    )
    assert response.status_code == 200
    assert response.json()["sql"] == "SELECT * FROM users;"

@patch('source.query_agent.generate_sql')
@patch('source.rag.retrieval.retrieve_examples')
@patch('source.schema_agent.get_schema')
def test_handle_followup(mock_get_schema, mock_retrieve_examples, mock_generate_sql):
    mock_get_schema.return_value = {"users": {"columns": ["id", "name"]}}
    mock_retrieve_examples.return_value = []
    mock_generate_sql.return_value = "SELECT name FROM users;"

    response = client.post(
        "/followup",
        json={"follow_up_query": "Only retrieve names", "session_id": "test_session"}
    )
    assert response.status_code == 200
    assert response.json()["sql"] == "SELECT name FROM users;"
