from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env.local")

openai_model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

streaming_model = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-1.5-flash",
    temperature=0,
    streaming=True,
)

non_streaming_model = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-1.5-flash",
    temperature=0,
    streaming=False,
)
