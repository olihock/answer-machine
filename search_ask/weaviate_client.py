import os
import logging
import weaviate

from dotenv import load_dotenv

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
        "class": class_name.lower(),
        "vectorizer": weaviate_vectorizer
    }
    client.schema.create_class(clazz)


def feed_vector_database(text_list, schema_name, user_id, file_id, filename, batch_size=10):
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
                "user_id": str(user_id),
                "file_id": file_id,
                "filename": filename,
                "chunk_no": f"{i} of {len(text_list)}",
                "text": text
            }
            batch.add_data_object(properties, schema_name)
            logging.debug("Indexed page " + str(i) + " of " + str(len(text_list)))


def search_similar_texts(class_name: str, question: str):
    """
    Search similar texts to the question. The nearest documents
    according the vectors in descending order are returned.
    """
    response = (
        client.query
        .get(class_name, ["user_id", "file_id", "filename", "chunk_no", "text"])
        .with_near_text({"concepts": [question]})
        .do())
    return response
