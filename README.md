# Text-to-SQL System

The Text-to-SQL system converts natural language queries into executable SQL statements using an AI assistant. It incorporates few-shot prompting, schema inference, and a Retrieval-Augmented Generation (RAG) mechanism for iterative self-improvement.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate     # On Windows

pip install -r requirements.txt
```

## Usage

```bash
python source/main.py --query "Your natural language query here"
```

## Docker Deployment

### Building the Docker Image

```bash
docker build -t nl2sql_app .
```

### Running the Docker Container

```bash
docker run -e OPENAI_API_KEY=your_api_key nl2sql_app --query "Sample query"
```

### Using Docker Compose

Ensure you have `docker-compose.yml` configured.

```bash
docker-compose up --build
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for accessing the LLM.

## Deployment on Cloud Platforms

- **Google Cloud Run:** [Guide](https://cloud.google.com/run/docs/quickstarts/build-and-deploy)
- **AWS ECS:** [Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- **Heroku:** [Guide](https://devcenter.heroku.com/categories/deploying-with-docker)
