from typing import *
import dotenv
from langchain.llms import HuggingFaceHub, OpenAI


class LLMSpecification:
    def __init__(self, model_hub, model_name):
      self.model_hub = model_hub
      self.model_name = model_name
      
      # Place holder: throw an error if there is no .env file

      dotenv.load_dotenv()
      environment_values = dotenv.dotenv_values()

      if model_hub == "OpenAI":
          try:
              assert environment_values["OPEN_AI_KEY"]
          except:
              print(
                "You must supply your OpenAI API key in the .env file "
                + "as:\nOPEN_AI_KEY=sk_[your key]"
              )
          self.llm = OpenAI(
              model=model_name,
              openai_api_key=environment_values["OPEN_AI_KEY"],
              temperature=0.9,
              client="",
          )

      elif model_hub == "HuggingFaceHub":
          try:
              assert environment_values["HUGGINGFACEHUB_API_TOKEN"]
          except:
              print(
                "You must supply your HuggingFaceHub API key in the "
                + ".env file as:\nHUGGINFACEHUB_API_TOKEN=hf_[your key]"
              )
          self.llm = HuggingFaceHub(
              huggingfacehub_api_token=environment_values["HUGGINGFACEHUB_API_TOKEN"],
              repo_id=model_name,
              client=None,
          )

      else:
          raise Exception("Model hub must be OpenAI or HuggingFaceHub")
      
    def get_llm(self):
        return self.llm

    def get_model_name(self):
        return self.model_name
    
    def get_model_hub(self):
        return self.model_hub

