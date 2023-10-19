import sys
sys.path.insert(1, "./src")
from flask import Flask, request, redirect
from flask_cors import CORS #comment this on deployment

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

import services.cogniflow_core as cfc

# Do I need these here?
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import stanza

# Following SQLAlchemy tutorial at https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__) #, static_url_path='', static_folder='frontend/build')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///'
    + os.path.join(basedir, 'database.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Initialization
    num_sentences = db.Column(db.Integer)
    path_to_file = db.Column(db.String(4096))
    model_hub = db.Column(db.String(100))
    model_name = db.Column(db.String(100))

    # CogniFlow stuff
    preprocessed = db.Column(db.Boolean) # Has CF created a vector
                                         # database for the text?
    raw_text = db.Column(db.Text)
    vector_db = db.Column(db.LargeBinary)
    memory_buffer_string = db.Column(db.String(10000)) # Memory buffer string
                                              # to (re-)construct 
                                              # memory
    intro_ready_to_go = db.Column(db.Boolean) # Whether or not to
                                              # continue the
                                              # conversation loop in
                                              # the intro

    # Status
    status = db.Column(db.String(50))

    def __repr__(self):
        return f'memory_buffer: {self.memory_buffer_string}'


app.secret_key = "dflajdflajdflasjdfljasldfjalsd"
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
            status="welcome"
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

            # Probably can kill cfc.get_memory()
            # Use cfc.get_memory_from_buffer_string(config.memory_buffer_string, ai_prefix, human_prefix)
            config.preprocessed = True
            # db.session.add(config)
            db.session.commit()
        
        # Program outline:
        # 1) Welcome
        # 2) Introductory conversation
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
            print("introductory convo")
            # INTRODUCTORY CONVERSATION
            ## This is the converation after the bot has welcomed the
            ## user to CogniFlow. This conversation goes on until the
            ## user tells CogniFlow that they are ready to go.

            # Reconstruct the chat memory
            memory_buffer_as_string = config.memory_buffer_string
            print(repr(memory_buffer_as_string))
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
            print("document_preprocssing convo")
            # DOCUMENT PROCESSING
            #
            # Start by obtaining the main text if we are reading a
            # remote source. Not ideal, but ask the user for some help
            # in finding the start and end of the text
            # if not cfc.is_local(config.path_to_file):
                # raw_text = cfc.get_start_and_end_points(raw_text)
            
            # Use stanza to tokenize the document and find all the sentences.
            # Refer to the output of the tokenizer as the "document"
            # tokenizer = stanza.Pipeline(
            #     lang='en',
            #     processors='tokenize',
            #     verbose=False
            # )
            # document = tokenizer(raw_text)

            # Get the sentences and the number of setnences in the document
            # sentences = document.sentences
            # number_of_sentences_in_document = len(sentences)

            # Store the NUM_SENTENCES we get sequentially
            # summaries = []

            # Cursor to track what sentence we're at in the text. Start
            # at the beginning
            # c = 0
            # db.session.add(config)
            # db.session.commit()
            return {"summary" : "document_processing"}
        return {"summary" : "Garbage"}

# if __name__ == "__main__":
#     db.create_all()
#     app.run()