import sys
sys.path.insert(1, "./src")
from flask import Flask, request
from flask_cors import CORS #comment this on deployment

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

import services.cogniflow_core as cfc

# Do I need these here?
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

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
    preprocessed = db.Column(db.Boolean)
    raw_text = db.Column(db.Text)
    vector_db = db.Column(db.LargeBinary)

    # Status
    status = db.Column(db.String(50))

    def __repr__(self):
        return f'<path_to_file[0:25]: {self.path_to_file[0:25]}'


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
            status="welcome"
        )
        db.session.add(config)
        db.session.commit()
        message = (
            "NUM_SENTENCES="
            + str(Configuration.query.get(config.id).num_sentences)
            + ", "
            + "PATH_TO_FILE="
            + Configuration.query.get(config.id).path_to_file[0:10]
            + ", "
            + "MODEL_HUB="
            + Configuration.query.get(config.id).model_hub
            + ", "
            + "MODEL_NAME="
            + Configuration.query.get(config.id).model_name
        )
        # To get the id of the Configuration you just committed, see
        # Miguel Grinberg's post at
        # https://www.reddit.com/r/flask/comments/3mhgt1/how_do_i_grab_the_id_of_an_object_after_ive/
        return {
            "initialized" : message,
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
            db.session.add(config)
            db.session.commit()
        # Program outline:
        if config.status == "Welcome":
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
                human_input=""
            )

            # Update chat history and status
            config.memory_buffer_as_string = memory.buffer_as_str
            config.status = "Don't know yet!"
            db.session.add(config)
            db.session.commit()

            return {"summary" : welcome.strip()}
        num_sentences = config.num_sentences
        raw_text = config.raw_text
        preprocessed = config.preprocessed
        message = (
            "Human message is: "
            + HUMAN_MESSAGE
            + ",\n"
            + "ID="
            + ID
            + ",\n"
            + "NUM_SENTENCES="
            + str(num_sentences)
            + ",\n"
            + "raw_text="
            + raw_text[400:500]
            + ",\n"
            + "preprocssed="
            + str(preprocessed) 
        )
        return {"summary" : message}

# if __name__ == "__main__":
#     db.create_all()
#     app.run()