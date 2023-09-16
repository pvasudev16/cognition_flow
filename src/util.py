from typing import *
import os
import dotenv
from langchain.llms import HuggingFaceHub, OpenAI
from typing import *
import stanza


# Import input processing packages
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
from urllib.parse import urlparse
from os.path import exists

# Import packages for chunking text and creating embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import (
    OpenAIEmbeddings,
    HuggingFaceHubEmbeddings
)

def check_for_dot_env_file():
  if not os.path.exists(".env"):
      raise Exception(
          "You must provide a .env file in the root cogni_flow "
          + "directory that contains OPEN_API_KEY and/or "
          + "HUGGINGFACEHUB_API_TOKEN values."
      )

class LLMSpecification:
    def __init__(self, model_hub, model_name):
      self.model_hub = model_hub
      self.model_name = model_name
      
      check_for_dot_env_file()

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


def print_sentences_and_tokens(document : stanza.Document) -> None:
      """
      Utility function for debugging.
      This function prints out the token id and the text associated
      with each token id for each sentence int he stanza document
      """
      for i, sentence in enumerate(document.sentences):
        print(f'====== Sentence {i+1} tokens =======')
        print(
            *[
                f'id: {token.id}\ttext: {token.text}'
                for token in sentence.tokens
              ],
            sep='\n'
        )

def print_sentences(document : stanza.Document) -> None:
    """
    Utility function to print out the sentences in a stanza document
    """
    for s in document.sentences:
        print(s.text + " ")

def get_next_sentences(
    document : stanza.Document,
    starting_position : int,
    number_of_sentences : int
):
    sentences = ""
    for j in range(number_of_sentences):
        if starting_position + j >= len(document.sentences):
            break
        sentences += document.sentences[starting_position + j].text
        sentences += " "
    return sentences

# Find out if a file is local or not
# https://stackoverflow.com/questions/68626097/pythonic-way-to-identify-a-local-file-or-a-url
def is_local(url):
    url_parsed = urlparse(url)
    if url_parsed.scheme in ('file', ''): # Possibly a local file
        return exists(url_parsed.path)
    return False

# Find out if a file is a pdf or not
def is_pdf(filename):
    split_filename = filename.split(".")
    if split_filename[-1] == "pdf":
        return True
    else:
        return False

# Scraping functions. Taken verbatim from
# https://stackoverflow.com/questions/1936466/how-to-scrape-only-visible-webpage-text-with-beautifulsoup
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    texts = soup.findAll(string=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def get_start_and_end_points(raw_text):
    """
    Given the scraped text from a website, ask the user for help in
    identifying the relevant text (e.g. article). This function will
    ask the user to input the first and last four words of the relevant
    text, and note their positions. It will then return the actual
    text to subdivide into sentences, summarize, and display.
    """

    first_four_words = input(
        "Thanks for giving me a URL that we can read together. "
        + "To read a URL, I need a bit of help from you. Can you "
        + "tell me what the first four words of the article are? "
        + "Please write them exactly here.\n"""
    )
    starting_pos = raw_text.find(first_four_words)
    while starting_pos == -1:
        first_four_words = input(
            "Oops, I couldn't find that in the article! Please "
            + "input the first four words of the article exactly!\n"
        )
        starting_pos = raw_text.find(first_four_words)
    
    last_four_words = input(
        "Thanks! And I need one last thing from you. Can you "
        + "provide me with the last four words of the article?\n"
    )
    ending_pos = raw_text.find(last_four_words)
    while ending_pos == -1:
        last_four_words = input(
            "Oops, I couldn't find that in the article! Please "
            + "input the last four words of the article exactly!\n"
        )
        ending_pos = raw_text.find(last_four_words)
    text_to_return = raw_text[
        starting_pos:(ending_pos + len(last_four_words))
    ]
    return text_to_return

class LLMEmbeddings:
    def __init__(self, model_hub, model_name):
      self.model_hub = model_hub
      self.model_name = model_name
      
      check_for_dot_env_file()

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
          self.embeddings = OpenAIEmbeddings(
              openai_api_key=environment_values["OPEN_AI_KEY"]
          )

      elif model_hub == "HuggingFaceHub":
          try:
              assert environment_values["HUGGINGFACEHUB_API_TOKEN"]
          except:
              print(
                "You must supply your HuggingFaceHub API key in the "
                + ".env file as:\nHUGGINFACEHUB_API_TOKEN=hf_[your key]"
              )
          self.embeddings = HuggingFaceHubEmbeddings(
              huggingfacehub_api_token=environment_values["HUGGINGFACEHUB_API_TOKEN"],
          )

      else:
          raise Exception("Model hub must be OpenAI or HuggingFaceHub")
      
    def get_embeddings(self):
        return self.embeddings

    def get_model_name(self):
        return self.model_name
    
    def get_model_hub(self):
        return self.model_hub