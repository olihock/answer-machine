
## Deployment

### Environment Variables
| Variable       | Description                          |
|----------------|--------------------------------------|
| WEAVIATE_URL   | Base URL to Weaviate vector database |
| OPENAI_API_KEY | OpenAI API Key to access ChatGPT     |


## Development

### Project Dependencies
```shell
python3 -m pip install gradio
python3 -m pip install openai
python3 -m pip install os
python3 -m pip install dotenv
python3 -m pip install sklearn
python3 -m pip install weaviate-client
```

### Python Environments
```shell
python3 -m venv localenv
source localenv/bin/activate
deactivate
```

### Vector Database
```shell
cd weaviate
docker compose up -d && docker compose logs -f weaviate
docker start docker-weaviate-1
```