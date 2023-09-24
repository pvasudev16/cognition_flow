from flask_restful import Api, Resource, reqparse
from services.cogniflow_core import cogniflow_core
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
    parser.add_argument('postContent', type=str, location='form')
    parser.add_argument('numSentences', type=int, location='form')
    args = parser.parse_args()

    text = args['postContent']
    num_sentences = args['numSentences']


    data = self.query(
        {
            "inputs": text,
            "parameters": {"no_repeat_ngram_size": 3, "min_length": num_sentences, "max_length": 256, "encoder_no_repeat_ngram_size": 3},
        })

    
    # ret_msg = cogniflow_core(text, num_sentences, "HuggingFaceHub", "facebook/bart-large-cnn")

    print(data)
    final_ret = {"status": "Success", "summary": data[0]["summary_text"]}

    return final_ret


