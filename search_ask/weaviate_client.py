from dotenv import load_dotenv
import os
import weaviate

load_dotenv()
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_vectorizer = os.environ["WEAVIATE_VECTORIZER"]

client = weaviate.Client(
    url=weaviate_url
)


def is_class_exists(class_name: str):
    return client.schema.exists(class_name=class_name)


def create_class(class_name: str):
    """
    Simply create a new schema by given class name and vectorizer.
    """
    clazz = {
        "class": class_name,
        "vectorizer": weaviate_vectorizer
    }
    client.schema.create_class(clazz)


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


def search_similar_texts(class_name: str, question: str, limit=10):
    """
    Search similar texts to the question. The nearest documents
    according the vectors in descending order are returned.
    """
    response = (
        client.query
        .get(class_name, ["no", "text"])
        .with_near_text({"concepts": [question]})
        .with_limit(limit)
        .do())
    return response
