import gradio
from fastapi import FastAPI
from search_ask_chat import search_for_answer


upload_component = gradio.File(label="Upload your context")
question_component = gradio.Textbox(value="How can I build a city?", lines=10, label="Your question")
answer_component = gradio.Text(label="Answer")

ui = gradio.Interface(fn=search_for_answer,
                      inputs=[upload_component, question_component],
                      outputs=answer_component,
                      title="Answer Machine")
# ui.queue().launch()

# The FastAPI usage is a workaround for deployment purposes.
app = FastAPI()
app = gradio.mount_gradio_app(app, ui, path='/')
