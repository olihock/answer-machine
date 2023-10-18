import gradio.components
from search_ask.custom_data_reader import slice_to_pages
from search_ask.weaviate_client import create_class, feed_vector_database, search_similar_texts
from search_ask.user_chatbot import engineer_prompt, answer_question


def search_for_answer(class_name: str, file, question: str):
    create_class(class_name)

    pages = slice_to_pages(file)
    feed_vector_database(pages, class_name)

    similarities = search_similar_texts(class_name, question)
    prompt = engineer_prompt(class_name, question, similarities)
    answer = answer_question(prompt)

    return answer


upload_component = gradio.File(label="Upload your context")
context_component = gradio.Textbox(value="Miscellaneous", label="Classify your context")
question_component = gradio.Textbox(value="How can I build a city?", lines=10, label="Your question")
answer_component = gradio.Text(label="Answer")

iface = gradio.Interface(fn=search_for_answer,
                         inputs=[context_component, upload_component, question_component],
                         outputs=answer_component,
                         title="Answer Machine")

iface.launch(share=True)
