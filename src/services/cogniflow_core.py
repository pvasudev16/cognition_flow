import sys
from typing import *
import stanza
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from src.util import *

# INPUT PARSING
def get_raw_text(PATH_TO_FILE):
    # Find out if this is a local file or not.
    local = is_local(PATH_TO_FILE)

    if local:
        # Read in all the text, and get it into a single string, which
        # we'll call the raw_text. Note that we assume local files
        # are only plain text files; no HTML.
        file_to_read = open(PATH_TO_FILE, "r")
        lines = []
        while True:
            line = file_to_read.readline()
            lines.append(line)
            if not line:
                break
        raw_text = "".join(lines)
    else:
        # If this is a URL, then we need to get it
        raw_text = text_from_html(PATH_TO_FILE)
    return raw_text

def get_llm(MODEL_HUB, MODEL_NAME):
    return LLMSpecification(MODEL_HUB, MODEL_NAME).get_llm()

def get_embeddings(MODEL_HUB, MODEL_NAME):
    return LLMEmbeddings(MODEL_HUB, MODEL_NAME).get_embeddings()

# EMBEDDINGS, SEMANTIC MEANING, AND VECTOR DATABASE RETRIEVAL
# Let's get the LLM to read the document and get the "semantic
# meaning" of the text so the user can ask questions during the
# reading.
def split_and_chunk_text(raw_text, chunk_size=500, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    # We need to convert the text into a LangChain document
    document = text_splitter.create_documents([raw_text])
    chunked_raw_text = text_splitter.split_documents(document)
    return chunked_raw_text

def get_vector_db(chunked_raw_text, embeddings):
    return FAISS.from_documents(chunked_raw_text, embeddings)

def serialize_vector_db(vector_db, folder_path, filename):
    vector_db.save_local(vector_db, folder_path, filename)

def get_vector_db_retriever(db, k=10):
    # k specifies to retrieve the k-closest queires
    return db.as_retriever(search_kwargs={"k" : k})

# MEMORY
# Every prompt will need a "human_input" input, even if it's 
# not actually the human inputting it. E.g. it might be
# NUM_SENTENCES of the document we've parsed
def get_memory():
    return ConversationBufferMemory(
        memory_key="chat_history",
        input_key="human_input"
    )

# PERSONA
## Define our reader's persona
def get_persona():
    return (
        """
        You are a kind and compassionate assistant. Your main
        role is to help people read. You use short sentences.
        You are having a conversation with a human. When you respond,
        you keep your answers to 10 - 15 words and you use simple
        vocabulary.
        """
    )