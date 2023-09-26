import sys
from typing import *
import stanza
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from src.util import *

def preprocessing(
    NUM_SENTENCES,
    PATH_TO_FILE,
    MODEL_HUB,
    MODEL_NAME
):
    # INPUT PARSING
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
    
    # EMBEDDINGS, SEMANTIC MEANING, AND VECTOR DATABASE RETRIEVAL
    # Let's get the LLM to read the document and get the "semantic
    # meaning" of the text so the user can ask questions during the
    # reading.

    # Get the LLM and embeddings based on the user inputs.
    llm = LLMSpecification(MODEL_HUB, MODEL_NAME).get_llm()
    embeddings = LLMEmbeddings(MODEL_HUB, MODEL_NAME).get_embeddings()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20
    )
    # We need to convert the text into a LangChain document
    document = text_splitter.create_documents([raw_text])
    chunked_raw_text = text_splitter.split_documents(document)
    embedding_list = embeddings.embed_documents(
        [t.page_content for t in chunked_raw_text]
    )

    # Store our embedding list in a searchable vector database
    db = FAISS.from_documents(chunked_raw_text, embeddings)

    # Get a retriever which will retrieve the 10 closest results
    # to a query
    retriever = db.as_retriever(search_kwargs={"k" : 10})

    
    # MEMORY
    # Every prompt will need a "human_input" input, even if it's 
    # not actually the human inputting it. E.g. it might be
    # NUM_SENTENCES of the document we've parsed
    memory=ConversationBufferMemory(
        memory_key="chat_history",
        input_key="human_input"
    )

    # PERSONA
    ## Define our reader's persona
    persona = (
        """
        You are a kind and compassionate assistant. Your main
        role is to help people read. You use short sentences.
        You are having a conversation with a human. When you respond,
        you keep your answers to 10 - 15 words and you use simple
        vocabulary.
        """
    )

    # WELCOME
    ## Make a chat prompt for the reader to welcome the user to
    ## CogniFlow. Human input should just be empty. Here, human_input
    ## will be a dummy input, since the memory has it as the input_key.
    welcome_prompt = PromptTemplate(
        input_variables=[
            "persona",
            "chat_history",
            "human_input"
        ],
        template=(
            """
            {persona}

            Here is the chat history so far:
            
            {chat_history}

            Welcome the user to CogniFlow. Make sure to use the words
            "CogniFlow" in your welcome exactly. Tell the user they
            can ask you any questions. If they ask you what CogniFlow
            is, tell them that you are a reading assistant. You are
            starting this conversation.

            {human_input}

            YOUR RESPONSE:
            """
        )
    )

    welcome_chain = LLMChain(
        llm=llm,
        prompt=welcome_prompt,
        verbose=False,
        memory=memory
    )

    welcome = welcome_chain.predict(
        persona=persona,
        human_input=""
    )

    return welcome.strip()