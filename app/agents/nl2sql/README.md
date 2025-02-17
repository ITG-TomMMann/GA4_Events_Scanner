# Advanced Text-to-SQL System

The Advanced Text-to-SQL system converts natural language queries into executable SQL statements using an AI assistant powered by LangChain. It features an interactive FastAPI-based UI, optimized table selection, sophisticated prompt engineering, conversation memory for follow-up queries, and dynamic retrieval of few-shot examples.

## Features

- **Interactive UI:** FastAPI-based interface for submitting queries and viewing results.
- **Optimized Table Selection:** Dynamically selects relevant tables based on query context using FAISS.
- **Sophisticated Prompt Engineering:** Constructs dynamic prompts incorporating schema and few-shot examples.
- **Conversation Memory:** Maintains context across multiple interactions for follow-up queries.
- **Dynamic Few-Shot Retrieval:** Retrieves contextually relevant examples to enhance SQL generation accuracy.
- **Logging & Monitoring:** Comprehensive logging for debugging and monitoring.
- **Unit & Integration Testing:** Ensures reliability and correctness of components.
- **Containerization:** Dockerized application for easy deployment.

## Architecture

```
nl2sql/
├── config/
│   └── config.yaml
├── examples/
│   ├── examples.json
│   └── query_prompt_template.txt
├── source/
│   ├── rag/
│   │   ├── retrieval.py
│   │   ├── vector_store.py
│   │   └── __init__.py
│   ├── utils/
│   │   ├── embedding_utils.py
│   │   ├── logger.py
│   │   ├── prompt_builder.py
│   │   ├── schema_inference.py
│   │   └── table_selector.py
│   ├── memory_manager.py
│   ├── main.py
│   ├── query_agent.py
│   └── schema_agent.py
├── tests/
│   ├── __init__.py
│   ├── test_query_agent.py
│   ├── test_retrieval.py
│   ├── test_schema_agent.py
│   └── test_nl2sql.py
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## Installation

### Prerequisites

- Python 3.9+
- Docker & Docker Compose

### Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/your-repo/nl2sql.git
    cd nl2sql
    ```

2. **Create and Activate Virtual Environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Unix/macOS
    # or
    .\venv\Scripts\activate     # On Windows
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables:**

    Create a `.env` file in the root directory:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

5. **Configure `config.yaml`:**

    Update `config/config.yaml` with your database credentials and other settings.

## Usage

### Running Locally

1. **Start FastAPI Server:**

    ```bash
    uvicorn source.main:app --reload
    ```

2. **Access the UI:**

    Open your browser and navigate to `http://localhost:8000/docs` to access the interactive API documentation.

### Docker Deployment

1. **Build the Docker Image:**

    ```bash
    docker build -t nl2sql_app .
    ```

2. **Run the Docker Container:**

    ```bash
    docker run --env-file .env -p 8000:8000 nl2sql_app
    ```

3. **Using Docker Compose:**

    Ensure `docker-compose.yml` is configured with necessary environment variables.

    ```bash
    docker-compose up --build
    ```

## Deployment on Cloud Platforms

- **Google Cloud Run:** [Guide](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)
- **AWS ECS:** [Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- **Heroku:** [Guide](https://devcenter.heroku.com/categories/deploying-with-docker)

## Testing

1. **Run Unit Tests:**

    ```bash
    pytest
    ```

## Contributing

Contributions are welcome! Please open issues and submit pull requests for enhancements and bug fixes.

## License

[MIT License](LICENSE)
