import sys
sys.path.insert(1, "./src")
from flask import Flask
from flask_restful import Api
from flask_cors import CORS #comment this on deployment
from services.cogniflow_api_handler import CognitionFlowApiHandler, InitializationHandler

app = Flask(__name__) #, static_url_path='', static_folder='frontend/build')
app.secret_key = "dflajdflajdflasjdfljasldfjalsd"
CORS(app, supports_credentials=True) #comment this on deployment

api = Api(app)
api.add_resource(CognitionFlowApiHandler, '/')
api.add_resource(InitializationHandler, '/initialization')