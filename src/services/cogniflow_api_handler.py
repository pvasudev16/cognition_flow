from flask_restful import Api, Resource, reqparse
import  services.cogniflow_core as cogniflow_core
from main import *
import json
import requests
import dotenv

class CognitionFlowApiHandler(Resource):
  def query(self, payload):
    environment_values = dotenv.dotenv_values()
    token = environment_values["HUGGINGFACEHUB_API_TOKEN"]
    headers = {"Authorization": f"Bearer {token}"}
    API_URL = "https://api-inference.huggingface.co/models/pszemraj/led-base-book-summary"
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))
  
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

    print(NUM_SENTENCES)

    data = cogniflow_core.preprocessing(
      NUM_SENTENCES,
      PATH_TO_FILE,
      MODEL_HUB,
      MODEL_NAME
    )
    print(data)
    final_ret = {
      "status": "Success",
      "summary": data,
    }

    return final_ret


