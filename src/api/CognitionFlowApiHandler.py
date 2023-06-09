from flask_restful import Api, Resource, reqparse
from important_functions import *

class CognitionFlowApiHandler(Resource):
  def get(self):
    return {
      'resultStatus': 'SUCCESS',
      'message': "Cognition Flow Api Handler"
      }

  def post(self):
    print(self)
    parser = reqparse.RequestParser()
    parser.add_argument('postContent', type=str, location='form')
    parser.add_argument('numSentences', type=str, location='form')
    args = parser.parse_args()

    text = args['postContent']
    num_sentences = args['numSentences']
    ret_msg = cogniflow_core(text, num_sentences, "HuggingFaceHub", "google/flan-t5-xxl")

    # ret_msg = raw_content

    # if ret_msg:
    #   message = "Your Message Requested: {}".format(ret_msg)
    # else:
    #   message = "No Msg"
    
    # placeholder for the actual model
    final_ret = {"status": "Success", "summary": ret_msg}

    return final_ret