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
