
import os
from dotenv import load_dotenv
from openai import OpenAI


ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")
if not OPENAI_BASE_URL:
    raise ValueError("OPENAI_BASE_URL not found in .env file")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL not found in .env file")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

completion = client.chat.completions.create(
  model=OPENAI_MODEL,
  messages=[
    { "role": "system", 
      "content": "You are a helpful AI assistant." },
    { "role": "user", 
      "content": "Explain  what is Tomato late blight and how to prevent it." }
  ],
  temperature=0.7
)

print(completion.choices[0].message.content)