import sys
sys.path.insert(1, "./src")
from flask import Flask, request, redirect, Response, url_for
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

#### Terminology:
# - N: number of sentences to parse at a time. This is the number of
#      sentences CogniFlow will summarize and display at a time.
#### CogniFlow Outline
# 0) Initialization. The user will click on the "Initialize" button
#    to initiate the N (number of sentences to parse at a time), and the
#    URL. Assume we use OpenAI text-davinci-003
# 1) Preprocessing. Get the raw text from the text file or website.
#    If it's a website, the raw text will include all the metadata and
#    extraneous text to the actual text itself. Form the embeddings,
#    chunk the text, and form the vector database. Using the 
#    newspaper3k package, get the main text of the article. Break the
#    main text into human-parseable sentences (as opposed to just 500
#    character long chunks).
# 2) Text Summarization. This is where we will display the summary of
#    the N sentences followed by the N sentences themselves. In
#    between each of the N sentences, the user can converse with
#    CogniFlow about the displayed sentences. The user can tell
#    CogniFlow that they want to end early
# 3) Exit.

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

    # A JSON dump of the vector of the human-parseable sentences
    # in the text. This excludes any metadata/garbage in text
    # scraped from URLs.
    sentences = db.Column(db.Text)

    # The number of sentences in the text
    number_of_sentences_in_text = db.Column(db.Integer)

    # A cursor indicating how many sentences have been summarized
    # and displayed.
    cursor = db.Column(db.Integer)

    # A JSON dump of the conversation history, which will alternate
    # between what the chatbot says (including actual text of)
    # the article and what the human says.
    conversation_history = db.Column(db.Text)

    # A boolean flag indicating in the summarization whether
    # the user is ready to keep going.
    summarization_keep_going = db.Column(db.Boolean)

    # A JSON dump of the vector of summaries CogniFlow has made
    # so far
    summaries = db.Column(db.Text)

    # A boolean flag indicating after displaying the summaries if
    # to keep going in the conversation.
    summarization_continue_conversation = db.Column(db.Boolean)

    # Status
    status = db.Column(db.String(50))

    def __repr__(self):
        return f'memory_buffer: {self.memory_buffer_string}'

CORS(app, supports_credentials=True) #comment this on deployment

@app.route("/landing", methods=["POST"])
def landing_page():
    if request.method == "POST":
        return Response("Hello Theo")
    return Response("Hello")

@app.route("/append_to_conversation_history", methods=["POST"])
def append_to_conversation_history():
    HUMAN_MESSAGE = request.form['HUMAN_MESSAGE']
    ID = request.form['ID']
    config = Configuration.query.get(ID)
    if request.method == "POST":
        if not config.conversation_history:
            conversation_history = []
        else:
            conversation_history = json.loads(
                config.conversation_history
            )
        conversation_history.append(HUMAN_MESSAGE)
        config.conversation_history = json.dumps(conversation_history)
        db.session.commit()
    return(
        {
            "conversation" : config.conversation_history,
            "status" : "unknown",
            "summary" : "No summary"
        }
    )


@app.route("/initialization", methods=["POST"])
def initialize():
    #### 0) INITIALIZATION
    if request.method == 'POST':
        NUM_SENTENCES = int(request.form['NUM_SENTENCES'])
        PATH_TO_FILE = request.form['PATH_TO_FILE']
        config = Configuration(
            num_sentences=NUM_SENTENCES,
            path_to_file=PATH_TO_FILE,
            model_hub="OpenAI",
            model_name="text-davinci-003",
            preprocessed=False,
            raw_text=None,
            vector_db=None,
            memory_buffer_string=None,
            status="welcome",
            sentences=None,
            cursor=0,
            conversation_history=None,
            summarization_keep_going=True,
            summaries=None,
            summarization_continue_conversation=True
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

        if not config.conversation_history:
            conversation_history = []
        else:
            conversation_history = json.loads(
                config.conversation_history
            )        
        
        print(conversation_history)
        #### 1) PREPROCESSING
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

            # Get the human parseable sentences with Stanza
            tokenizer = stanza.Pipeline(
                lang='en',
                processors='tokenize',
                verbose=False
            )
            document = tokenizer(config.raw_text)
            sentences = [s.text for s in document.sentences]
            sentences_as_json = json.dumps(sentences)

            config.sentences = sentences_as_json
            config.number_of_sentences_in_text = len(sentences)
            config.cursor = 0
            config.status = "summarization"

            config.preprocessed = True
            db.session.commit()

        #### 2) SUMMARIZATION
        if config.status == "summarization":
            memory = cfc.get_memory_from_buffer_string(
                config.memory_buffer_string
            )
            llm = cfc.get_llm(config.model_hub, config.model_name)

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

            c = config.cursor
            sentences = json.loads(config.sentences)

            summaries = []
            if config.summaries:
                summaries = json.loads(config.summaries)

            if config.summarization_keep_going:
                next_sentences = cfc.get_next_sentences(
                    sentences,
                    c,
                    config.num_sentences
                )
                summary = summary_chain.predict(
                    text_to_summarize=next_sentences,
                    persona=cfc.get_persona(),
                    human_input=""
                )

                summary_string = (
                    "The summary of sentences "
                    + str(c)
                    + " to "
                    + str(c + config.num_sentences)
                    + " is:"
                    + summary.strip()
                    + "\nThe actual text is:\n\n"
                    + next_sentences
                    + "\n"
                )
                conversation_history.append(summary_string)

                # Advance the cursor by NUM_SENTENCES
                c += config.num_sentences

                # If we've exceeded the total number of setences, break
                if c >= config.number_of_sentences_in_text:
                    config.summarization_keep_going = False
                
                summaries.append(summary)
                config.summaries = json.dumps(summaries)
                config.cursor = c
                config.status = "summarization_discussion"
                config.summarization_continue_conversation = True
                config.memory_buffer_string = memory.buffer_as_str
                config.conversation_history = json.dumps(conversation_history)
                db.session.commit()
                return {
                    "summary" : summary_string,
                    "conversation" : config.conversation_history,
                    "status" : config.status
                }
            else:
                return {"summary" : "You've reached the end! Thanks for using CogniFlow!"}      
        
        if config.status == "summarization_discussion":
            memory = cfc.get_memory_from_buffer_string(
                config.memory_buffer_string
            )
            llm = cfc.get_llm(config.model_hub, config.model_name)
            vector_db = FAISS.deserialize_from_bytes(
                serialized=config.vector_db,
                embeddings=cfc.get_embeddings(
                    config.model_hub,
                    config.model_name
                )
            )
            vector_db_retriever = cfc.get_vector_db_retriever(vector_db)
            summaries = json.loads(config.summaries)


            # Make a prompt that will be used to discuss each of the
            # summaries. It needs a human_input as a prompt for the
            # chat. Also pass in the documents in case it needs to
            # answer a question.
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

            if config.summarization_continue_conversation:
                discussion_output = discussion_chain.predict(
                    human_input=HUMAN_MESSAGE,
                    persona=cfc.get_persona(),
                    most_recent_summary=summaries[-1],
                    summaries=" ".join(summaries),
                    documents=(
                        vector_db_retriever.get_relevant_documents(
                            HUMAN_MESSAGE
                        )
                    )
                )
                conversation_history.append(discussion_output)
                if "Let's keep going" in discussion_output:
                    config.summarization_continue_conversation=False
                    config.status = "summarization"
                    config.memory_buffer_string = memory.buffer_as_str
                    db.session.commit()
                    return redirect("/", code=307)
                if "Let's stop" in discussion_output:
                    config.summarization_continue_conversation=False
                    config.summarization_keep_going=False
                    config.status = "exit"
                config.memory_buffer_string = memory.buffer_as_str
                config.conversation_history = json.dumps(
                    conversation_history
                )
                db.session.commit()
                return {
                    "summary" : discussion_output,
                    "conversation" : config.conversation_history,
                    "status" : ID
                } #config.converation_history}
            else:
                raise Exception(
                    "SUMMARIZATION DISCUSSION: should never go here"
                )

        #### 3) EXIT
        if config.status == "exit":
            return {"summary" : "Goodbye"}
        
        raise Exception(
            "[NONE]: Should never go here, no status was set!"
        )

# if __name__ == "__main__":
#     db.create_all()
#     app.run()