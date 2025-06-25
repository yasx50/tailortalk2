from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  

api_key = os.getenv("API_KEY")


client = Groq(
    api_key=api_key,
)

def chat_ai(content):
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": content,
        }
    ],
    model="llama-3.3-70b-versatile",
)
    return chat_completion.choices[0].message.content
response = chat_ai("titanic kya hai 1 word answer")
print(response)