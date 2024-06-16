from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

from embeddings import get_embeddings

load_dotenv(dotenv_path=".env.local")

pinecone_api_key = os.getenv("PINECONE_API_KEY")


def get_pinecone_client():
    pc = Pinecone(api_key=pinecone_api_key)
    return pc


def get_vector_store(pc: Pinecone):
    embeddings = get_embeddings()
    vector_store = PineconeVectorStore.from_existing_index(
        embedding=embeddings,
        index_name=os.getenv("PINECONE_INDEX"),
        namespace=os.getenv("PINECONE_NAMESPACE"),
        text_key="text",
    )
    return vector_store
