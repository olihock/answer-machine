import os
import openai
from sklearn.metrics.pairwise import cosine_similarity

openai.api_key = os.environ["OPENAI_API_KEY"]

coffee_types = [
    "Black: Coffee is served without any additions like milk, cream, or sugar. It provides the most authentic taste "
    "of the coffee bean.",
    "With milk or cream: Adding milk or cream to coffee can provide a creamy and smoother taste. The amount can be "
    "adjusted according to your preference, from a splash to a larger amount.",
    "With sugar or sweetener: If you prefer a sweeter taste, you can add sugar or any preferred sweetener to your "
    "coffee. Adjust the amount based on your desired level of sweetness.",
    "Espresso: Espresso is a concentrated form of coffee made by forcing hot water under pressure through finely "
    "ground coffee beans. It is a strong and bold method of enjoying coffee.",
    "Latte: A latte consists of espresso mixed with steamed milk and topped with a small amount of foam. It can be "
    "customized with different flavors or additional toppings like chocolate or caramel syrup.",
    "Cappuccino: Cappuccino is similar to latte but with equal parts of espresso, steamed milk, and foam. It has a "
    "balanced flavor and is often topped with cocoa or cinnamon.",
    "Iced coffee: Coffee served over ice, often with milk, cream, or sweeteners added. It is a refreshing option, "
    "especially during hot weather."
]

# Create a list of embeddings (also vectors re. indexes) from custom data given prior to the text generation.
coffee_type_embeddings = []
for coffee_type in coffee_types:
    openai_response = openai.Embedding.create(engine="text-embedding-ada-002", input=coffee_type)
    coffee_type_embeddings.append(openai_response['data'][0]['embedding'])

# Generate the embedding for the user question.
user_question = "Recommend a coffee if I prefer a balanced flavour?"
embedded_user_question = (
    openai.Embedding.create(engine="text-embedding-ada-002", input=user_question))['data'][0]['embedding']

# Find the most similar embedding in the coffee types.
similarities = cosine_similarity([embedded_user_question], coffee_type_embeddings)
array_index_of_most_similar_coffee_type = similarities.argmax()
prompt_context = coffee_types[array_index_of_most_similar_coffee_type]

# Merge the user question and context (which is the most similar coffee type) and forward all to OpenAI.
prompt = (
        user_question +
        " Use the below coffee hint to answer the subsequent question. If the answer cannot be found in the articles, "
        "write 'I cannot recommend a coffee to you." +
        prompt_context)
message = {"role": "user", "content": prompt}
prompt_response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[message])
answer = prompt_response.choices[0].message.content
print(answer)
