from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class WelcomePrompt:
    # WELCOME
    ## Make a chat prompt for the reader to welcome the user to
    ## CogniFlow. Human input should just be empty. Here, human_input
    ## will be a dummy input, since the memory has it as the input_key.
    def __init__(self):
        self.prompt = PromptTemplate(
            input_variables=[
              "persona",
              "chat_history",
              "human_input"
            ],
            template=(
                """
                {persona}

                Here is the chat history so far:
            
                {chat_history}

                Welcome the user to CogniFlow. Make sure to use the words
                "CogniFlow" in your welcome exactly. Tell the user they
                can ask you any questions. If they ask you what CogniFlow
                is, tell them that you are a reading assistant. You are
                starting this conversation.

                {human_input}

                YOUR RESPONSE:
                """
            )   
        )
    
    def get_prompt(self):
        return self.prompt