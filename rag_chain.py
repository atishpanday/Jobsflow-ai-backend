from langchain.prompts import ChatPromptTemplate
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from pinecone_client import get_pinecone_client, get_vector_store

from llm import streaming_model, non_streaming_model

contextualize_q_system_prompt = """
Given a chat history and the latest user question
which might reference context in the chat history,
formulate a standalone question which can be understood
without the chat history. Do NOT answer the question, just
reformulate it if needed and otherwise return it as is."""

qa_system_prompt = """
You are an assistant for question-answering tasks. Use
the following pieces of retrieved context to answer the
question. If you don't know the answer, just say that you
don't know. Use three sentences maximum and keep the answer
concise.
\n\n
{context}"""


def call_chain(question, chat_history):
    sanitized_question = question.strip().replace("\n", " ")

    pc = get_pinecone_client()
    vector_store = get_vector_store(pc)
    retriever = vector_store.as_retriever()

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            "\n{chat_history}\n",
            ("human", "{input}"),
        ]
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            "\n{chat_history}\n",
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm=non_streaming_model,
        retriever=retriever,
        prompt=contextualize_q_prompt,
    )

    question_answer_chain = create_stuff_documents_chain(
        llm=streaming_model, prompt=qa_prompt
    )

    rag_chain = create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=question_answer_chain,
    )

    for chunk in rag_chain.stream(
        {
            "input": sanitized_question,
            "chat_history": chat_history,
        }
    ):
        if answer_chunk := chunk.get("answer"):
            yield answer_chunk
