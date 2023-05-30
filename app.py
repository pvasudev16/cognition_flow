from flask import Flask
from flask_restful import Api
from flask_cors import CORS #comment this on deployment
from api.CognitionFlowApiHandler import CognitionFlowApiHandler

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
CORS(app) #comment this on deployment
api = Api(app)

api.add_resource(CognitionFlowApiHandler, '/cognition_flow/')