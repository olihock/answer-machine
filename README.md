# Answer Machine

## Application States
Documents have a status field that can have the following values:
- ```hochgeladen```: Document has been uploaded and is waiting to be processed.
- ```durchsuchbar```: Document has been processed and is ready to be queried.

## Operations

### Docker
From within a Docker container to Linux host: ```172.17.0.1```

### OpenID Connect Provider
Install and configure an OpenID Connect Provider (e.g. Keycloak is used here). 
1. Create a realm ```production```.
2. Configure an SMTP server for this realm (for user registration). 
3. Within this realm create a client ```answer-machine```.

### File Database
```shell
sudo apt-get install -y postgresql-client
psql -h localhost -p 5433 -d postgres -U postgres
CREATE DATABASE filedb;
CREATE USER data_import WITH PASSWORD 'data_import';
GRANT ALL PRIVILEGES ON DATABASE filedb TO data_import;
\c filedb
GRANT CREATE ON SCHEMA public TO data_import;
CREATE TABLE IF NOT EXISTS upload_file (
	id SERIAL NOT NULL, 
	user_id UUID NOT NULL, 
	category VARCHAR NOT NULL, 
	filename VARCHAR NOT NULL, 
	status VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)
GRANT ALL ON TABLE upload_file TO data_import;
GRANT USAGE, SELECT ON SEQUENCE upload_file_id_seq TO data_import;
\q
```




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
