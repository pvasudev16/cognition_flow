from flask_restful import Resource, reqparse
import services.cogniflow_core as cfc
from flask import session
import services.prompt_library as prompt_library

# TEMP; Axe these because these are in services.cogniflow_core
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class InitializationHandler(Resource):
    # Initialization should:
    # - Gather and store the four parameters
    #   (NUM_SENTENCES, PATH_TO_FILE, MODEL_HUB, MODEL_NAME) as session
    #   variables
    # - Define a session variable INITIALIZED
    def get(self):
        return {
            'resultStatus': 'SUCCESS',
            'message': "Initialization Handler"
        }

    def post(self):
        ## This isn't working. Need to get the session variable to work
        ## see https://stackoverflow.com/questions/77189435/how-to-make-session-dictionary-persist-between-two-endpoints-resources-in-flask

        # Do initialization only if not initialized; but not working.
        # if not session.get("INITIALIZED"):
        parser = reqparse.RequestParser()
        parser.add_argument('NUM_SENTENCES', type=int, location='form')
        parser.add_argument('PATH_TO_FILE', type=str, location='form')
        parser.add_argument('MODEL_HUB', type=str, location='form')
        parser.add_argument('MODEL_NAME', type=str, location='form')
        args = parser.parse_args()

        # Gather and store the four parameters NUM_SENTENCES, PATH_TO_FILE,
        # MODEL_HUB, MODEL_NAME
        print(session)
        NUM_SENTENCES = args['NUM_SENTENCES']
        PATH_TO_FILE = args['PATH_TO_FILE']
        MODEL_HUB = args['MODEL_HUB']
        MODEL_NAME = args['MODEL_NAME']
        session['NUM_SENTENCES'] = NUM_SENTENCES
        session['PATH_TO_FILE'] = PATH_TO_FILE
        session['MODEL_HUB'] = MODEL_HUB
        session['MODEL_NAME'] = MODEL_NAME
        session['INITIALIZED'] = "TRUE"
        session.modified=True
        print(session)
        return {"initialized" : str(session['INITIALIZED'])}


class CognitionFlowApiHandler(Resource):
    def __init__(self):
        # Has text loading, chunking, vector_db, etc. been done?
        self.preprocessed = False

        # Raw text, LLM, Embeddings, Chunked Text, Vector DB and Retriever,
        # and Memory.
        self.raw_text = None
        self.llm = None
        self.embeddings = None
        self.chunked_raw_text = None
        self.vector_db = None
        self.vector_db_retriever = None
        self.memory = None

        # Persona
        self.persona = None

        # Hold the post-processed sentences
        self.sentences = None

        # Conversation status: welcome, initial conversation, summary,
        # etc.
        self.conversation_status = "welcome"


    def get(self):
        return {
            'resultStatus': 'SUCCESS',
            'message': "Cognition Flow Api Handler"
        }

    def post(self):
        print(self.conversation_status)
        # Session not working for now so hard code in parameters
        NUM_SENTENCES = 3
        PATH_TO_FILE = "https://www.theguardian.com/football/2023/sep/30/tottenham-liverpool-premier-league-match-report"
        MODEL_HUB = "OpenAI"
        MODEL_NAME = "text-davinci-003"

        # Session stuff
        # print(session)
        # if not session.get('INITIALIZED'):
        #   return {"summary" : "session not initialized"}
        #
        # NUM_SENTENCES = session['NUM_SENTENCES'] 
        # PATH_TO_FILE = session['PATH_TO_FILE']
        # MODEL_HUB = session['MODEL_HUB']
        # MODEL_NAME = session['MODEL_NAME']
    
        if not self.preprocessed:
            self.raw_text = cfc.get_raw_text(PATH_TO_FILE)
            self.llm = cfc.get_llm(MODEL_HUB, MODEL_NAME)
            self.embeddings = cfc.get_embeddings(MODEL_HUB, MODEL_NAME)
            self.chunked_raw_text = cfc.split_and_chunk_text(self.raw_text)
            self.vector_db = cfc.get_vector_db(
                self.chunked_raw_text,
                self.embeddings
            )
            self.vector_db_retriever = cfc.get_vector_db_retriever(
                self.vector_db
            )
            self.memory = cfc.get_memory()
            self.persona = cfc.get_persona()
            self.preprocessed = True
    
        # Is this robust?
        if self.conversation_status == "welcome":
            welcome_prompt = prompt_library.WelcomePrompt().get_prompt()

            welcome_chain = LLMChain(
                llm=self.llm,
                prompt=welcome_prompt,
                verbose=False,
                memory=self.memory
            )

            welcome = welcome_chain.predict(
                persona=self.persona,
                human_input=""
            )

            self.conversation_status = "introductory_conversation"

            return {"summary" : welcome.strip()}

        elif self.conversation_status == "introductory_conversation":
            parser = reqparse.RequestParser()
            parser.add_argument('HUMAN_INPUT', type=int, location='form')
            args = parser.parse_args()
            text = args['HUMAN_INPUT']
            return {"summary" : text}

