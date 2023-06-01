from flask_restful import Api, Resource, reqparse

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
    args = parser.parse_args()

    raw_content = args['postContent']
    ret_msg = raw_content

    # placeholder for the actual model
    final_ret = {"status": "Success", "summary": "Africans: large ears, concave backs; Asians: small ears, convex/level backs."}

    return final_ret