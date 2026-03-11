import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate   
from langchain_community.document_loaders import WebBaseLoader

ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(ENV_PATH)

OPENAI_API_kEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

if not OPENAI_API_kEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
if not OPENAI_BASE_URL:
    raise ValueError("OPENAI_BASE_URL is not set in the environment variables.")
if not OPENAI_MODEL:
    raise ValueError("OPENAI_MODEL is not set in the environment variables.")

client = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_kEY,
    base_url=OPENAI_BASE_URL,
    temperature=0.7,
)


# prompt_template = PromptTemplate(
#     input_variables=["topic"],
#     template="Explain what is {topic} and how to prevent it? with less than 100 characters."
# )
# # response = client.invoke(prompt_template.format(topic="Tomato late blight"))
# # print(response.content)

# chat_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are an expert agricultural advisor. Be concise and accurate."),
#         ("human", "Explain what is {topic} and how to prevent it? Limit it to {num_words} words."),
#     ]
# )
# messages = chat_prompt.invoke({"topic": "Tomato late blight", "num_words": 100})
# response = client.invoke(messages)
# print(response.content)

##Context
# context="""Tomato Late Blight is caused by Phytiphthora infestans, a fungus-like organism. It thrives in wet conditions and can devastate tomato crops. To prevent it, ensure good air circulation, avoid overhead watering, and apply fungicides as needed."""
# rag_prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are an expert agricultural advisor. Be concise and accurate."),
#         ("human", """Context:{context}
#          "Question":{question}
#          Answer:"""
# )]
# )
# messages=rag_prompt.invoke({"context": context, "question": "How to treat tomato disease?",})
# response = client.invoke(messages)
# print(response.content)

## ---Web Loader Example---
WIKI_URL = "https://en.wikipedia.org/wiki/Phytophthora_infestans"
loader=WebBaseLoader(WIKI_URL)
docs = loader.load()
web_context = docs[0].page_content[:6000]

rag_prompt_web=ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert agricultural advisor. Answer using ONLY the provided context."),
        ("human", """Context:{context}
         "Question":{question}
         Answer:""",
    )]
)
messages_web=rag_prompt_web.invoke({
    "source": WIKI_URL,
    "context": web_context,
    "question": "What is Phytophthora infestans and how can farmers manage late blight?"
})
response_web = client.invoke(messages_web)
print(response_web.content)




# # First prompt
# response = client.invoke(
#     [
#         {"role":"system","content":"You are a helpful assistant for farmers."},
#         {"role":"user","content":"Explain what is Tomato late blight and how to prevent it? with less than 100 characters."}
#     ]
# )
# print(response.content)

# # Second prompt
# prompt_input = "What is the best fertilizer for tomatoes?"
# response = client.invoke(prompt_input)
# print(response.content)

# # Third prompt
# prompt_input = "What is the best fertilizer for tomatoes?"
# response = client.invoke(prompt_input)
# print(response.content)