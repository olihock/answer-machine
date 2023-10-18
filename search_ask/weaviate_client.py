from dotenv import load_dotenv
import os
import weaviate

load_dotenv()
weaviate_url = os.environ["WEAVIATE_URL"]

client = weaviate.Client(
    url=weaviate_url
)


def create_schema(class_name, vectorizer):
    """
    Simply create a new schema by given class name and vectorizer,
    if it does not exist yet.
    """
    schema = {
        "class": class_name,
        "vectorizer": vectorizer
    }
    client.schema.create_class(schema)


def feed_vector_database(text_list, schema_name, batch_size=100):
    """
    Take a list of texts and a schema name to feed the vector database in batch mode.
    The vector is created by the transformer that has been configured when running
    Weaviate. See ENABLE_MODULES in docker-compose.yml for example.
    """
    client.batch.configure(batch_size=batch_size)
    with client.batch as batch:
        i = 0
        for text in text_list:
            i = i + 1
            properties = {
                "no": i,
                "text": text
            }
            batch.add_data_object(properties, schema_name)


def search_similar_texts(question: str, limit=10):
    """
    Search similar texts to the question. The nearest documents
    according the vectors in descending order are returned.
    """
    response = (
        client.query
        .get("Programming", ["no", "text"])
        .with_near_text({"concepts": [question]})
        .with_limit(limit)
        .do())
    return response
