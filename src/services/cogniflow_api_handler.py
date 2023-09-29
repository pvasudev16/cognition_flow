from flask_restful import Resource, reqparse
import services.cogniflow_core as cfc
from flask import session

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
#    if not session.get("INITIALIZED"):
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
    self.preprocessed = False
    self.raw_text = None
    
  def get(self): # get(self, message_id=5), use get to get the 6th message in the history
    # get is more to look at the history or a db that exists and get
    # something from it
    return {
      'resultStatus': 'SUCCESS',
      'message': "Cognition Flow Api Handler"
      }

  def post(self): # post(self, response_text)
    print(session)
    if not session.get('INITIALIZED'):
      return {"summary" : "session not initialized"}

    if not self.preprocessed:
      self.raw_text = cfc.get_raw_text(session['PATH_TO_FILE'])
      self.preprocessed = True

    return {"summary" : self.raw_text[0:10]}


