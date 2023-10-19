# Answer Machine

## Operations

### Configuration
Configure following environment variables in an ```.env``` file in the project root.

| Variable            | Description                                                                                              |
|---------------------|----------------------------------------------------------------------------------------------------------|
| WEAVIATE_URL        | Base URL to Weaviate vector database                                                                     |
| WEAVIATE_VECTORIZER | A Weaviate vectorizer (see https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules) |
| OPENAI_API_KEY      | OpenAI API Key to access ChatGPT                                                                         |

### Deployment
```shell
docker compose up -d && docker compose logs -f weaviate
docker compose down
```
**Test app instance**
```shell
open http://localhost:10000
```

## Development

**Create Python environment**
```shell
python3 -m venv venv
source venv/bin/activate
deactivate
```
