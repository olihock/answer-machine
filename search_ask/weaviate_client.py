import weaviate
import json

client = weaviate.Client(
    url="http://localhost:8080",
)


def create_class_in_schema(class_name):
    search_ask_class = {
        "class": class_name,
        "vectorizer": "none"
    }
    client.schema.create_class(search_ask_class)


def feed_vector_database(text_vector_pairs):
    text_vector_json = json.dumps(text_vector_pairs)

    client.batch.configure(batch_size=100)
    with client.batch as batch:
        for i, data in enumerate(text_vector_json):
            properties = {
                "text": data['Text']
            }
            batch.add_data_object(properties, "Text", vector=data["Vector"])
