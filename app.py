import os
from search_ask.custom_data_reader import read_custom_data
from search_ask.weaviate_client import feed_vector_database, search_similar_texts
from search_ask.user_chatbot import engineer_prompt, answer_question

PROJECT_DIR = os.path.abspath(os.curdir)
data_location = os.path.join(PROJECT_DIR, "data")

# Read all custom data from the source.
custom_data = read_custom_data(data_location)

# Insert all chunked data into the vector database.
feed_vector_database(custom_data, "Programming")

# Find similarities of user question from the vector database.
question = "How Would You Build a City?"
similarities = search_similar_texts(question)
prompt = engineer_prompt(question, similarities)
answer = answer_question(prompt)
print(answer)
