import openai
import os
import tiktoken

openai.api_key = os.environ["OPENAI_API_KEY"]
GPT_MODEL = "gpt-3.5-turbo"


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """
    Calculate and return the number of tokens in a text.
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def engineer_prompt(question, similarities, token_budget=(4096-512)):
    introduction = ("Use the below pages to answer the subsequent question. "
                    "If the answer cannot be found in the pages, write \"I could not find an appropriate answer.\".")
    prompt = introduction
    for page in similarities['data']['Get']['Programming']:
        page_text = page['text']
        next_page_section = f'\n\nPage section: """\n{page_text}\n"""'
        if num_tokens(prompt + next_page_section + question) < token_budget:
            prompt += next_page_section
        else:
            break
    return prompt + "\n\nQuestion: " + question


def answer_question(prompt: str):
    messages = [
        {"role": "system", "content": "You answer questions to the user."},
        {"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(model=GPT_MODEL, messages=messages, temperature=0.25)
    answer = response.choices[0].message.content

    return answer
