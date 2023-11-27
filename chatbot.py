import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFDirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import docx2txt
from PyPDF2 import PdfReader
from langchain.prompts.prompt import PromptTemplate
import os
import streamlit as st

class Chatbot:
    def __init__(self, openai_api_key):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=100)
        self.underlying_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)

        qa_template = """       
You are an invaluable assistant entrusted with crafting personalized cover letters. Armed with the user's resume and the specifics of the job description,
your mission is to meticulously tailor the cover letter to highlight precisely how the candidate's qualifications align with the job requirements. 
Additionally, if provided, incorporate any extra insights about the company to infuse the cover letter with specific details, such as projects, values, or achievements.
The goal is to create a compelling narrative that not only demonstrates a perfect fit for the job but also showcases a deep understanding of the unique aspects of the hiring company.

        context: {context}
        =========
        question: {question}
        ======
        """

        self.QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["context","question" ])   

    
    def load_document(self, file):
        text=""
        if file.name.endswith(".pdf"):
            pdf = PdfReader(file)
            for page in pdf.pages:
                text += page.extract_text()
        elif file.name.endswith(".docx"):
            text = docx2txt.process(file)
            text = self.strip_consecutive_newlines(text)

        return text
    

    @st.cache_resource(show_spinner="creating a vectorstore...")
    def vectorize(_self, texts):
    
        chunks = _self.splitter.split_text(texts)
        vectorstore = Chroma.from_texts(chunks, _self.underlying_embeddings)

        return vectorstore
    
    def build_chain(_self, vectorstore, top_k):
        chain = RetrievalQA.from_chain_type(llm = _self.llm, 
                                            retriever = vectorstore.as_retriever(search_kwargs={"k": top_k}),
                                            combine_docs_chain_kwargs={'prompt': _self.QA_PROMPT},
                                            return_source_documents=True)
        return chain