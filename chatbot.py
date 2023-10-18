import gradio.components
import openai
import os


openai.api_key = os.environ["OPENAI_API_KEY"]


def chat_bot(prompt):

    message = {"role": "user", "content": prompt}

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[message])

    answer = response.choices[0].message.content

    return answer


iface = gradio.Interface(fn=chat_bot,
                         inputs=gradio.Textbox(value="How do I have my coffee?", lines=10, label="Prompt"),
                         outputs=gradio.Text(label="Answer"),
                         title="AI Chatbot with Custom Data")

iface.launch(share=True)