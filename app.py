import sys
sys.path.insert(1, "./src")
from flask import Flask, request, redirect
from flask_cors import CORS #comment this on deployment

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

import services.cogniflow_core as cfc
from src.util import * # I'd like to get rid of this

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import stanza
import json

# Following SQLAlchemy tutorial at https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__) #, static_url_path='', static_folder='frontend/build')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///'
    + os.path.join(basedir, 'database.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#### CogniFlow Outline
# Terminology:
# - N: number of sentences to parse at a time. This is the number of
#      sentences CogniFlow will summarize and display at a time.
# 0) Initialization. The user will click on the "Initialize" button
#    to initiate the N (number of sentences to parse at a time), the
#    path to the text file or URL, the model hub (OpenAI by default)
#    and the model name (text-davinci-003 by default)
# 1) Preprocessing. Get the raw text from the text file or website.
#    If it's a website, the raw text will include all the metadata and
#    extraneous text to the actual text itself. Form the embeddings,
#    chunk the text, and form the vector database.
# 2) Welcome. Assume no user input, and CogniFlow will welcome the user.
#    This welcome leads to an initial conversation where the user can
#    ask CogniFlow more questions.
# 3) Introductory Conversation. Conversation loop where
#    the user can ask CogniFlow any questions. Questions can be
#    irrelevant (e.g. "Who is Haruki Murakami?") or relevant
#    ("What do you do?"). Once the user indicates they are ready,
#    CogniFlow will proceed to the document preprocessing
# 4) Document Processing. Similar to preprocessing but different.
#    While preprocessing chunks and vectorizes the database, here
#    we break the text into human-parseable sentences (as opposed to
#    just 500 character long chunks).
#    4a) TO-DO: If the user provided a URL, we need to ask the user
#        for some help in identifying the start/end of the text.
#        Ask the user to identify the first and last four words
#        of the text itself.
# 5) Instructions. Assume no user input. CogniFlow will tell the user
#    that CogniFlow will display a summary of the N sentences followed
#    by the N sentences themselves. These instructions lead to the
#    pre-summary conversation.
# 6) Pre-summary Conversation. Conversation loop where the user can ask
#    CogniFlow more questions. Once the user indicates they are ready to
#    go, CogniFlow will proceed to the text summarization.
# 7) Text Summarization. This is where we will display the summary of
#    the N sentences followed by the N sentences themselves. In
#    between each of the N sentences, the user can converse with
#    CogniFlow about the displayed sentences. The user can tell
#    CogniFlow that they want to end early
# 8) Exit.


# For each CogniFlow session, we will have one Configuration record,
# which tracks the input parameters and the state of the conversation
class Configuration(db.Model):
    #### Primary integer key
    id = db.Column(db.Integer, primary_key=True)

    #### Input paramers:
    ####
    # Number of sentences to parse at a time
    num_sentences = db.Column(db.Integer)

    # Local path to text file or URL to web page
    path_to_file = db.Column(db.String(4096))

    # Model hub to use (by deafult, OpeanAI)
    model_hub = db.Column(db.String(100))

    # Model to use (by default, text-davinci-003) 
    model_name = db.Column(db.String(100))

    #### CogniFlow State Variables
    ####
    # A boolean flag indicating if CogniFlow has read in the
    # number of sentences to parse, the path to file/URL,
    # the model hub, and the model
    preprocessed = db.Column(db.Boolean)

    # The raw text read in from the URL or the text file. If 
    # path_to_file is a URL, this variable will not only hold the
    # actual text but also all the metadata
    raw_text = db.Column(db.Text)

    # The vector database. Get the embeddings (using the same
    # model_hub and model_name), chunk the text, and form a
    # FAISS vector database, holding the semantic meaning of the text
    vector_db = db.Column(db.LargeBinary)

    # The memory buffer as a string. To decode the memory into a
    # LangChain ConversationBufferMemory object, use
    # cfc.get_memory_buffer_from_string(). To encode a
    # ConversationBufferMemory object into a string, we just do
    # memory.buffer_as_str
    memory_buffer_string = db.Column(db.Text)

    # A boolean flag indicating whether the user is ready to go
    # during the introductory conversation
    intro_ready_to_go = db.Column(db.Boolean)

    sentences = db.Column(db.Text) # Vector of sentences, stored as
                                   # JSON, of the text.
    number_of_sentences_in_text = db.Column(db.Integer)
    cursor = db.Column(db.Integer) # Cursor telling us how many
                                   # sentences has the user read 
                                   # already through
    pre_summary_ready_to_go = db.Column(db.Boolean) # Whether or not
                                                    # the user is ready
                                                    # to go in the
                                                    # conversation 
                                                    # before the
                                                    # summaries
    summarization_keep_going = db.Column(db.Boolean)

    # Status
    status = db.Column(db.String(50))

    def __repr__(self):
        return f'memory_buffer: {self.memory_buffer_string}'

CORS(app, supports_credentials=True) #comment this on deployment

@app.route("/initialization", methods=["POST"])
def initialize():
    if request.method == 'POST':
        NUM_SENTENCES = int(request.form['NUM_SENTENCES'])
        PATH_TO_FILE = request.form['PATH_TO_FILE']
        MODEL_HUB = request.form['MODEL_HUB']
        MODEL_NAME = request.form['MODEL_NAME']
        config = Configuration(
            num_sentences=NUM_SENTENCES,
            path_to_file=PATH_TO_FILE,
            model_hub=MODEL_HUB,
            model_name=MODEL_NAME,
            preprocessed=False,
            raw_text=None,
            vector_db=None,
            memory_buffer_string=None,
            intro_ready_to_go=False,
            status="welcome",
            sentences=None,
            number_of_sentences_in_text=None,
            cursor=0,
            pre_summary_ready_to_go=False,
            summarization_keep_going = True
        )
        db.session.add(config)
        db.session.commit()
        # To get the id of the Configuration you just committed, see
        # Miguel Grinberg's post at
        # https://www.reddit.com/r/flask/comments/3mhgt1/how_do_i_grab_the_id_of_an_object_after_ive/
        return {
            "initialized" : "initialized",
            "id" : config.id
        }

@app.route("/", methods=["POST"])
def cogniflow_io():
    if request.method == "POST":
        HUMAN_MESSAGE = request.form['HUMAN_MESSAGE']
        ID = request.form['ID']

        # Get the relevant record
        config = Configuration.query.get(ID)

        # Has pre-processing been done?
        preprocessed = config.preprocessed
        if not preprocessed:
            PATH_TO_FILE = config.path_to_file
            MODEL_HUB = config.model_hub
            MODEL_NAME = config.model_name

            # Store raw text
            raw_text = cfc.get_raw_text(PATH_TO_FILE)
            config.raw_text = raw_text
            config.preprocessed = True

            # Get embeddings to make vector database and store it
            embeddings = cfc.get_embeddings(MODEL_HUB, MODEL_NAME)
            chunked_raw_text = cfc.split_and_chunk_text(raw_text)
            vector_db = cfc.get_vector_db(
                chunked_raw_text,
                embeddings
            )
            config.vector_db = vector_db.serialize_to_bytes()
            # To deserialize, use deserialize_from_bytes()
            # vector_db_retriever = cfc.get_vector_db_retriever(
            #     vector_db
            # )
            config.preprocessed = True
            db.session.commit()
        
        # Program outline:
        # 1) Welcome
        # 2) Introductory conversation
        # 3) Document pre-processing
        # 4) Instructions
        # 5) Pre-conversation summary
        if config.status == "welcome":
            # WELCOME
            ## Make a chat prompt for the reader to welcome the user to
            ## CogniFlow. Human input should just be empty. Here,
            ## human_input will be a dummy input, since the memory has
            ## it as the input_key.

            # Nothing in chat history yet, so get an empty memory
            memory = cfc.get_memory()

            llm = cfc.get_llm(config.model_hub, config.model_name)
            persona = cfc.get_persona()

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
                human_input="" # Note the dummy input
            )

            # Update chat history and status
            config.memory_buffer_string = memory.buffer_as_str
            config.status = "introductory"

            db.session.commit()
            return {"summary" : welcome.strip()}
        
        if config.status == "introductory":
            # INTRODUCTORY CONVERSATION
            ## This is the converation after the bot has welcomed the
            ## user to CogniFlow. This conversation goes on until the
            ## user tells CogniFlow that they are ready to go.

            # Reconstruct the chat memory
            memory_buffer_as_string = config.memory_buffer_string
            if memory_buffer_as_string:
                memory = cfc.get_memory_from_buffer_string(
                    config.memory_buffer_string
                )
            else:
                memory = cfc.get_memory()

            # Get LLM
            llm = cfc.get_llm(config.model_hub, config.model_name)

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
                    can tell you. Only if the human indicates that they are ready
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

            ready_to_go = config.intro_ready_to_go
            if not ready_to_go:
                bot_output =  intro_conversation_chain.predict(
                    human_input=HUMAN_MESSAGE,
                    persona=cfc.get_persona()
                )
                if "Let's go" in bot_output:
                    config.intro_ready_to_go = True
                    config.memory_buffer_string = memory.buffer_as_str
                    config.status = "document_processing"
                    db.session.commit()
                    # return {"summary" : bot_output}
                    # https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask
                    return redirect("/", code=307)  
            else:
                raise Exception(
                    "Once the user has said they're ready to go "
                    + "the introductory conversation should be over")
            # Update chat history and status
            config.memory_buffer_string = memory.buffer_as_str
            db.session.commit()
            return {"summary" : bot_output}
            
        if config.status == "document_processing":
            # DOCUMENT PROCESSING

            # TO-DO
            # Obtain the main text if we are reading a
            # remote source. Not ideal, but ask the user for some help
            # in finding the start and end of the text
            # if not cfc.is_local(config.path_to_file):
                # raw_text = cfc.get_start_and_end_points(raw_text)
            
            # Use stanza to tokenize the document and find all the
            # sentences. Refer to the output of the tokenizer as
            # the "document"
            tokenizer = stanza.Pipeline(
                lang='en',
                processors='tokenize',
                verbose=False
            )
            document = tokenizer(config.raw_text)

            # Get the sentences and the number of senences
            # in the document. Set the cursor to the start
            # of the document
            sentences = [s.text for s in document.sentences]
            sentences_as_json = json.dumps(sentences)

            config.sentences = sentences_as_json
            config.number_of_sentences_in_text = len(sentences)
            config.cursor = 0

            config.status = "instructions"
            db.session.commit()
            return redirect("/", code=307) # should fwd to instruction
        
        if config.status == "instructions":
            # INSTRUCTIONS
            ## Here CogniFlow tells the user how to use CogniFlow.
            ## CogniFlow will tell the user what it'll do and how the
            ## user can interact with it. It'll ask the user if they
            ## are ready.

            # Reconstruct the chat memory and get LLM
            memory_buffer_as_string = config.memory_buffer_string
            memory = cfc.get_memory_from_buffer_string(
                config.memory_buffer_string
            )
            llm = cfc.get_llm(config.model_hub, config.model_name)

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
                persona=cfc.get_persona(),
                number_of_sentences=config.num_sentences,
            )

            # Update chat history and status
            config.memory_buffer_string = memory.buffer_as_str
            config.status = "pre_summary_conversation"
            db.session.commit()
            return {"summary" : instruction_output}
        
        if config.status == "pre_summary_conversation":
            # PRE-SUMMARY CONVERSATION
            # This is a chance for the user to ask CogniFlow questions
            # and chat before starting the summarizations

            # Reconstruct the chat memory and get LLM
            memory_buffer_as_string = config.memory_buffer_string
            memory = cfc.get_memory_from_buffer_string(
                config.memory_buffer_string
            )
            llm = cfc.get_llm(config.model_hub, config.model_name)

            ready_to_go = config.pre_summary_ready_to_go

            if not ready_to_go:
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
                    persona=cfc.get_persona(),
                    human_input=HUMAN_MESSAGE,
                )

                if "Let's go" in check_if_ready:
                    config.pre_summary_ready_to_go = True
                    config.status = "summarization"
            
            config.memory_buffer_string = memory.buffer_as_str
            db.session.commit()
            return {"summary" : check_if_ready}

        if config.status == "summarization":
            # SUMMARIZATION: This is the part where we summarize
            # and display the test

            # Reconstruct the chat memory and get LLM
            memory_buffer_as_string = config.memory_buffer_string
            memory = cfc.get_memory_from_buffer_string(
                config.memory_buffer_string
            )
            llm = cfc.get_llm(config.model_hub, config.model_name)
            
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

            c = config.cursor

            # SUMMARIZATION CONVERSATION LOOP
            ## Now we'll do the NUM_SENTENCES by NUM_SENTENCES summarization.

            # Flag indicating whether the user is ready to keep going or not
            # By default, assume they'll do one interation.

            while(config.summarization_keep_going):
                next_sentences = get_next_sentences(document, c, config.num_sentences)
                summary = summary_chain.predict(
                    text_to_summarize=next_sentences,
                    persona=persona,
                    human_input=""
                )

                summary_string = (
                    "The summary of sentences "
                    + str(c)
                    + " to "
                    + str(c + config.num_sentences)
                    + " is:"
                    + summary.strip()
                    + "\nThe actual text is:"
                    + next_sentences
                    + "\n"
                )

                # Advance the cursor by NUM_SENTENCES
                c += config.num_sentences

                # If we've exceeded the total number of setences, break
                if c >= config.number_of_sentences_in_text:
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

            config.memory_buffer_string = memory.buffer_as_str
            db.session.commit()
            return {"summary" : "what's next?"}

        
        return {"summary" : "Garbage"}

# if __name__ == "__main__":
#     db.create_all()
#     app.run()