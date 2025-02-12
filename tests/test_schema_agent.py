import pytest
from src.schema_agent import get_schema
from unittest.mock import patch

@patch('src.schema_agent.fetch_schema_sql')
@patch('src.utils.schema_inference.infer_schema')
def test_get_schema(mock_infer, mock_fetch_sql):
    mock_fetch_sql.return_value = "CREATE TABLE users (id INT, name VARCHAR(100));"
    mock_infer.return_value = {"users": {"columns": ["id", "name"]}}
    schema = get_schema()
    assert schema == {"users": {"columns": ["id", "name"]}}
