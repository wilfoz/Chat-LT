from pathlib import Path

import streamlit as st
from langchain.chains.conversational_retrieval.base import \
    ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from configs import get_config

st.secrets['openai']['OPENAI_API_KEY']

FILE_FOLDER = Path(__file__).parent / 'arquivos'


class Chat:
    def __init__(self, user_id, database):
        self.user_id = user_id
        self.chat_chain = None
        self.memory = None
        self.database = database

    def import_documents(self):
        documentos = []
        for arquivo in FILE_FOLDER.glob('*.pdf'):
            loader = PyPDFLoader(str(arquivo))
            documentos_arquivo = loader.load()
            documentos.extend(documentos_arquivo)
        return documentos

    def split_documents(self, documentos):
        recur_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2500,
            chunk_overlap=300,
            separators=["/n\n", "\n", ".", " ", ""]
        )
        documentos = recur_splitter.split_documents(documentos)

        for i, doc in enumerate(documentos):
            doc.metadata['source'] = doc.metadata['source'].split('/')[-1]
            doc.metadata['doc_id'] = i
        return documentos

    def create_vector_store(self, documentos):
        embedding_model = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(
            documents=documentos,
            embedding=embedding_model
        )
        return vector_store

    def initialize_chain(self):
        documentos = self.import_documents()
        documentos = self.split_documents(documentos)
        vector_store = self.create_vector_store(documentos)

        chat = ChatOpenAI(model=get_config('model_name'))
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key='chat_history',
            output_key='answer'
        )
        
        retriever = vector_store.as_retriever(
            search_type=get_config('retrieval_search_type'),
            search_kwargs=get_config('retrieval_kwargs')
        )
        prompt = PromptTemplate.from_template(get_config('prompt'))
        self.chat_chain = ConversationalRetrievalChain.from_llm(
            llm=chat,
            memory=self.memory,
            retriever=retriever,
            return_source_documents=True,
            verbose=True,
            combine_docs_chain_kwargs={'prompt': prompt},
        )
        st.session_state['chain'] = self.chat_chain

    def add_to_memory(self, user_id: str):
        conversation_history = self.database.get_conversation_history(user_id)
        resp = conversation_history if conversation_history else []
        messages_and_responses = [(item['message'], item['response']) for item in resp]

        for message, response in messages_and_responses:
            self.memory.chat_memory.add_user_message(message)
            self.memory.chat_memory.add_ai_message(response)

    def clear_history(self):
        self.database.clear_conversation_history(self.user_id)
        self.memory.clear()
