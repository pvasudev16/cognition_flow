import sys
from typing import *
import stanza
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from src.util import *


def main():
    """
    Read in a text and display a summary and the actual text in
    segments of number_of_sentences sentences.

    Command line arguments should be:
    1) Path to a text file or URL, called path_to_text
        (e.g. ./elephants.txt,
              ./elon_musk.txt,
              https://www.theguardian.com/football/2023/aug/26/brentford-crystal-palace-premier-league-match-report
        ). If it's a URL, the program will scrape the text but then
        ask the user to identify the first/last four words of the
        text. This will prevent CogniFlow from displaying all the other
        useless stuff on websites.
    2) Number of sentences to summarise at at time, called 
       number_of_sentences (e.g. 5)
    3) Model hub to use. Currently only "OpenAI" or "HuggingFaceHub"
       are supported.
    4) A model name to use. Use "text-davinci-003" for OpenAI and
       whatever model you want from HuggingFaceHub
       (e.g. "google/flan-t5-xxl")
    """

    args = sys.argv[1:]

    if len(args) != 4:
        raise Exception(
            "Please provide exactly four command line arguments:\n"
            + "1) The path to the file or URL,\n"
            + "2) The number of sentences to summarise at a time,\n"
            + "3) A model hub. Currently only OpenAI or HuggingFaceHub "
            +     "are supported.\n"
            + "4) A model name to use, e.g. text-davinci-003 for an\n"
            + "   OpenAI model hub or google/flan-t5-xxl for a\n"
            + "   HuggingFaceHub model hub."
        )
    if len(args) == 4:
        PATH_TO_FILE = args[0]
        NUM_SENTENCES = int(args[1])
        MODEL_HUB = args[2]
        MODEL_NAME = args[3]

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

    print(welcome.strip())

    # INTRODUCTORY CONVERSATION
    ## This is the converation after the bot has welcomed the user
    ## to CogniFlow. This conversation goes on until the user tells
    ## CogniFlow that they are ready to go.

    intro_conversation_prompt = PromptTemplate(
        input_variables=[
            "persona",
            "chat_history",
            "human_input"
        ],
        template= (
            """
            {persona}
            
            Tell the human that when they are ready to start they
            can tell you. If the human indicates that they are ready
            to start output the phrase "Let's go" exactly. Continue
            the conversation with the human until they tell you they
            are ready to go.
            
            {chat_history}
            
            Human: {human_input}
            YOUR RESPONSE:"""
        )
    )

    intro_conversation_chain = LLMChain(
        llm=llm,
        prompt=intro_conversation_prompt,
        verbose=False,
        memory=memory
    )

    ready_to_go = False
    while not ready_to_go:
        user_input = input("Human: ")
        bot_output =  intro_conversation_chain.predict(
            human_input=user_input,
            persona=persona
        )
        if "Let's go" in bot_output:
            ready_to_go = True
            break
        print("Chatbot: " + bot_output.strip())
    

    # DOCUMENT PRE-PROCESSING
    #
    # Start by obtaining the main text f we are reading a remote source.
    # Not ideal, but ask the user for some help in finding the start
    # and end of the text
    if not local:
        raw_text = get_start_and_end_points(raw_text)
    
    # Use stanza to tokenize the document and find all the sentences.
    # Refer to the output of the tokenizer as the "document"
    tokenizer = stanza.Pipeline(
        lang='en',
        processors='tokenize',
        verbose=False
    )
    document = tokenizer(raw_text)

    # Get the sentences and the number of setnences in the document
    sentences = document.sentences
    number_of_sentences_in_document = len(sentences)

    # Store the NUM_SENTENCES we get sequentially
    summaries = []

    # Cursor to track what sentence we're at in the text. Start
    # at the beginning
    c = 0

    # INSTRUCTIONS
    ## Here CogniFlow tells the user how to use CogniFlow. CogniFlow
    ## will tell the user what it'll do and how the user can interact
    ## with it. It'll ask the user if they are ready.

    # Here, human_input is a dummy variable.
    instruction_prompt = PromptTemplate(
        input_variables=[
            "human_input",
            "number_of_sentences",
            "persona",
            "chat_history"
        ],
        template=(
            """
            {persona}

            Here is the chat history so far:
            
            {chat_history}
            
            Start by telling the user what you will do.
            Tell the user you'll display a summary of
            {number_of_sentences} sentences, followed by the actual text
            itself. Tell the user they will be able to discuss each
            summary with you. Tell the user they will be able to ask you
            to keep going or to stop
            
            {human_input}

            YOUR RESPONSE:
            """
        )
    )
    instruction_chain = LLMChain(
        llm=llm,
        prompt=instruction_prompt,
        memory=memory,
        verbose=False
    )
    instruction_output = instruction_chain.predict(
        human_input="",
        persona=persona,
        number_of_sentences=NUM_SENTENCES,
    )
    print("Chatbot: " + instruction_output.strip())

    human_input = input("Human: ")

    check_if_ready_prompt = PromptTemplate(
        input_variables=[
            "human_input",
            "chat_history",
            "persona"
        ],
        template=(
            """
            {persona}

            Here is the chat history so far:
            {chat_history}

            If "{human_input}" indicates that they are ready, output
            "Let's go" exactly. Follow this instruction exactly.
            If not, tell the human it's ok and ask if they have any
            other questions.

            YOUR RESPONSE:
            """
        )
    )
    check_if_ready_chain = LLMChain(
        llm=llm,
        prompt=check_if_ready_prompt,
        memory=memory,
        verbose=False
    )
    check_if_ready = check_if_ready_chain.predict(
        persona=persona,
        human_input=human_input,
    )

    ready_to_go = False

    if "Let's go" in check_if_ready:
        ready_to_go = True


    while not ready_to_go:
        print("Chatbot: " + check_if_ready.strip())
        human_input = input("Human: ")
        check_if_ready = check_if_ready_chain.predict(
            persona=persona,
            human_input=human_input,
        )
        if "Let's go" in check_if_ready:
            ready_to_go = True
            break
        print("Chatbot: " + check_if_ready.strip())
    

    print(memory.load_memory_variables({}))

    # SUMMARIZATION (PREPARATION)
    ## Prepare the prompts and chains we'll need to do
    ## the summarization.

    # human_input is a dummy input
    summary_prompt = PromptTemplate(
        input_variables=[
            "human_input",
            "text_to_summarize",
            "persona",
            "chat_history",
        ],
        template=(
            """
            {persona}
            Here is the chat history so far:
        
            {chat_history}

            Now please summarize the following text in 10 words:

            {text_to_summarize}
        
            {human_input}

            YOUR RESPONSE:
            """
        )
    )
    summary_chain = LLMChain(
        llm=llm,
        prompt=summary_prompt,
        memory=memory,
        verbose=False
    )

    # Make a prompt that will be used to discuss each of the summaries.
    # It needs a human_input as a prompt for the chat. Also pass in
    # the documents in case it needs to answer a question.
    discussion_prompt = PromptTemplate(
        input_variables=[
            "human_input",
            "persona",
            "most_recent_summary",
            "summaries",
            "chat_history",
            "documents"
        ],
        template=(
            """
            {persona}
            
            Here is the chat history so far:

            {chat_history}
            
            Here is the most recent summary:

            {most_recent_summary}

            and here is a summary of the text so far:

            {summaries}

            Help the human by answering any questions they may have. For
            example, if they ask you to define a word, define it for
            them. If they ask you questions about the summary, answer
            them.

            If the human indicates that they want to continue onto
            the next set of sentences then output only "Let's keep
            going" exactly. If the human indicates they are ready to
            quit, output the phrase "Let's stop" exactly.

            Here are the most relevant parts of the text to answer
            the user's query:
            {documents}

            Human: {human_input}
            YOUR RESPONSE:
            """
        )
    )
    discussion_chain = LLMChain(
        llm=llm,
        prompt=discussion_prompt,
        memory=memory,
        verbose=False,
    )

    # SUMMARIZATION CONVERSATION LOOP
    ## Now we'll do the NUM_SENTENCES by NUM_SENTENCES summarization.

    # Flag indicating whether the user is ready to keep going or not
    # By default, assume they'll do one interation.
    keep_going = True

    while(keep_going):
        next_sentences = get_next_sentences(document, c, NUM_SENTENCES)
        summary = summary_chain.predict(
            text_to_summarize=next_sentences,
            persona=persona,
            human_input=""
        )
        print(
            "The summary of sentences "
            + str(c)
            + " to "
            + str(c + NUM_SENTENCES)
            + " is:"
        )

        print(summary.strip() + "\n")
        print("The actual text is:")
        print(next_sentences + "\n")

        # Advance the cursor by NUM_SENTENCES
        c += NUM_SENTENCES

        # If we've exceeded the total number of setences, break
        if c >= number_of_sentences_in_document:
            keep_going = False
        
        summaries.append(summary)

        continue_conversation = True

        while(continue_conversation):
            user_input = input("Human: ")
            discussion_output = discussion_chain.predict(
                human_input=user_input,
                persona=persona,
                most_recent_summary=summary,
                summaries=" ".join(summaries),
                documents=retriever.get_relevant_documents(user_input)
            )
            print("Chatbot: " + discussion_output)
            if "Let's keep going" in discussion_output:
                continue_conversation=False
            if "Let's stop" in discussion_output:
                continue_conversation=False
                keep_going=False

        print("\n\n")

    # ENDING
    ## Make a prompt that will thank the user for using CogniFlow
    
    # Human input will be a dummy prompt.
    end_prompt = PromptTemplate(
        input_variables=[
            "human_input",
            "chat_history"
        ],
        template=(
            """This is the chat history so far:
            {chat_history}

            Tell the user that they made it to the end of the text
            and that they did good work. Thank the user and make sure
            to use "CogniFlow" in your thanks.
            
            {human_input}
            
            YOUR RESPONSE:"""
        )
    )
    end_chain = LLMChain(
        llm=llm,
        prompt=end_prompt,
        memory=memory,
        verbose=False
    )
    end_output = end_chain.predict(human_input="")
    print("Chatbot: " + end_output.strip())


if __name__ == "__main__":
    main()