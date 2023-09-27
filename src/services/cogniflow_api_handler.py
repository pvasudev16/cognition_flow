from flask_restful import Api, Resource, reqparse
import  services.cogniflow_core as cfc
from flask import session
from main import *
import json
import requests
import dotenv

class InitializationHandler(Resource):
  # Initialization should:
  # - Gather and store the four parameters
  #   (NUM_SENTENCES, PATH_TO_FILE, MODEL_HUB, MODEL_NAME) as session
  #   variables
  # - Get the raw text and store it as a session variable RAW_TEXT
  # - Instantiate the LLM model and set it to a session variable LLM
  # - Instantiate the embeddings and set it to a session variable
  #   EMBEDDINGS
  # - Chunk the text
  # - Create the vector database and set it to a session variable
  #   VECTOR_DB
  # - Create a ConversationBufferMemory and set it to a session variable
  #   MEMORY
  # - Define the assistant's persona and set it to a session variable
  #   PERSONA
  def __init__(self):
    pass

  def get(self):
    pass

  def post(self):
    if not session.get("INITIALIZED"):
      parser = reqparse.RequestParser()
      parser.add_argument('NUM_SENTENCES', type=int, location='form')
      parser.add_argument('PATH_TO_FILE', type=str, location='form')
      parser.add_argument('MODEL_HUB', type=str, location='form')
      parser.add_argument('MODEL_NAME', type=str, location='form')
      args = parser.parse_args()

      # Gather and store the four parameters NUM_SENTENCES, PATH_TO_FILE,
      # MODEL_HUB, MODEL_NAME
      NUM_SENTENCES = args['NUM_SENTENCES']
      PATH_TO_FILE = args['PATH_TO_FILE']
      MODEL_HUB = args['MODEL_HUB']
      MODEL_NAME = args['MODEL_NAME']
      session["NUM_SENTENCES"] = NUM_SENTENCES
      session["PATH_TO_FILE"] = PATH_TO_FILE
      session["MODEL_HUB"] = MODEL_HUB
      session["MODEL_NAME"] = MODEL_NAME

      # Get the raw text
      raw_text = cfc.get_raw_text(PATH_TO_FILE)

      session["RAW_TEXT"] = raw_text

      # Get the LLM
      # session["LLM"] = cfc.get_llm(MODEL_HUB, MODEL_NAME)
      # Get the embeddings
      embeddings = cfc.get_embeddings(MODEL_HUB, MODEL_NAME)
      # session["EMBEDDINGS"] = embeddings

      # Chunk the text; default chunk size and overlap args used
      chunked_text = cfc.split_and_chunk_text(raw_text)

      # Create a vector database
      vector_db = cfc.get_vector_db(chunked_text, embeddings)
      # session["VECTOR_DB"] = vector_db

      # Get memory
      # session["MEMORY"] = cfc.get_memory()

      # Get persona
      session["PERSONA"] = cfc.get_persona()

      session["INITIALIZED"] = True
      print("Got to the end!")

    return session["INITIALIZED"]


class CognitionFlowApiHandler(Resource):
  def __init__(self):
    # Langchain's conversatio buffer memory
    self.memory = None

    # Status can be "initialization", "preproessing",
    # "welcome_converation", etc.
    self.status = None
    
  def get(self): # get(self, message_id=5), use get to get the 6th message in the history
    # get is more to look at the history or a db that exists and get
    # something from it
    return {
      'resultStatus': 'SUCCESS',
      'message': "Cognition Flow Api Handler"
      }

  def post(self): # post(self, response_text)
    # post means send the user input to chatbot AND get the chatbot's
    # response
    # include a conversation status key in the post input/output to
    # know where we are in the conversation.
    parser = reqparse.RequestParser()
    parser.add_argument('NUM_SENTENCES', type=int, location='form')
    parser.add_argument('PATH_TO_FILE', type=str, location='form')
    parser.add_argument('MODEL_HUB', type=str, location='form')
    parser.add_argument('MODEL_NAME', type=str, location='form')
    args = parser.parse_args()

    NUM_SENTENCES = args['NUM_SENTENCES']
    PATH_TO_FILE = args['PATH_TO_FILE']
    MODEL_HUB = args['MODEL_HUB']
    MODEL_NAME = args['MODEL_NAME']

    data = session.get("RAW_TEXT")[0:100]
    print(data)
    final_ret = {
      "status": "Success",
      "summary": data,
    }

    return final_ret


