import gradio.components
import os
import re
from search_ask.custom_data_reader import slice_to_pages
from search_ask.weaviate_client import create_class, feed_vector_database, search_similar_texts, is_class_exists
from search_ask.user_chatbot import engineer_prompt, answer_question


def search_for_answer(file, question: str):
    """
    This method does the magic. It creates a class name from the filename that has been uploaded.
    With this class name it checks on class existence and only indexes the texts in case it has
    not been done, yet. If we did, too many duplicates would be created and returned when searching
    similarities on the question.

    After that the prompt is engineered and fired off to ChatGPT via the API.

    Model and transformer are configured through environment variables as described in the README.md.
    """
    class_name = build_class_name(file)
    if not is_class_exists(class_name):
        create_class(class_name)
        pages = slice_to_pages(file)
        feed_vector_database(pages, class_name)

    similarities = search_similar_texts(class_name, question)
    prompt = engineer_prompt(class_name, question, similarities)
    answer = answer_question(prompt)

    return answer


def build_class_name(file):
    """
    Replace all special characters by an underscore as Weaviate class names allow
    regular characters only.
    """
    file_path = os.path.basename(file.name)
    class_name = re.sub("[^A-Za-z0-9]+", "_", file_path)
    return class_name.capitalize()


upload_component = gradio.File(label="Upload your context")
question_component = gradio.Textbox(value="How can I build a city?", lines=10, label="Your question")
answer_component = gradio.Text(label="Answer")

iface = gradio.Interface(fn=search_for_answer,
                         inputs=[upload_component, question_component],
                         outputs=answer_component,
                         title="Answer Machine")
# Queueing uses Websockets and avoids timeout when indexing large PDF files.
iface.queue()
iface.launch(share=True)
