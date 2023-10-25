import os
import re
from search_ask.weaviate_client import search_similar_texts
from search_ask.user_chatbot import engineer_prompt, answer_question


def search_for_answer(category: str, question: str):
    """
    Search for an answer to a question in the Weaviate database, create a prompt for the user chatbot and search
    for the answer.
    """
    similarities = search_similar_texts(category, question)
    prompt = engineer_prompt(category, question, similarities)
    answer = answer_question(prompt)

    return answer


def build_filename(file):
    """
    Replace all special characters by an underscore as Weaviate class names allow
    regular characters only.
    """
    file_path = os.path.basename(file.name)
    class_name = re.sub("[^A-Za-z0-9]+", "_", file_path)
    return class_name.capitalize()
