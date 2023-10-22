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
    memory_buffer_string = db.Column(db.Text) # Memory buffer string
                                              # to (re-)construct 
                                              # memory
    intro_ready_to_go = db.Column(db.Boolean) # Whether or not to
                                              # continue the
                                              # conversation loop in
                                              # the intro
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
            status="welcome",
            sentences=None,
            number_of_sentences_in_text=None,
            cursor=0,
            pre_summary_ready_to_go=False
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
                    config.status = "what's next"
            
            config.memory_buffer_string = memory.buffer_as_str
            db.session.commit()
            return {"summary" : check_if_ready}

        if config.status == "what's next":
            return {"summary" : "what's next?"}

        
        return {"summary" : "Garbage"}

# if __name__ == "__main__":
#     db.create_all()
#     app.run()