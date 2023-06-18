import sys
from typing import *
import stanza
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import dotenv
from langchain.llms import HuggingFaceHub, OpenAI
from models.llm_specification_model import LLMSpecification
from src.services.cogniflow_core import get_next_sentences


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

def main():
    """
    Read in a text and display a summary and the actual text in
    segments of number_of_sentences sentences.

    Command line arguments should be:
    1) Path to a text file, called path_to_text (e.g. ./elephants.txt)
    2) Number of sentences to summarise at at time, called 
       number_of_setneces (e.g. 5)
    3) Model hub to use. Currently only "OpenAI" or "HuggingFaceHub"
       are supported.
    4) A model name to use. Use "text-davinci-003" for OpenAI and
       whatever model you want from HuggingFaceHub (e.g. "gpt2")
    """

    # Place holder: error check if they provide more than/less than two 
    # command line arguments
    
    args = sys.argv[1:]
    if len(args) == 4:
        PATH_TO_FILE = args[0]
        NUM_SENTENCES = int(args[1])
        MODEL_HUB = args[2]
        MODEL_NAME = args[3]
    

    # Place holder: error check if we can't find the file

    # Read in all the text, and get it into a single string, which
    # we'll call the document
    file_to_read = open(PATH_TO_FILE, "r")
    lines = []
    while True:
        line = file_to_read.readline()
        lines.append(line)
        if not line:
            break
    raw_text = "".join(lines)
    
    # Use stanza to tokenize the document and find all the sentences.
    # Refer to the output of the tokenizer as the "document"
    tokenizer = stanza.Pipeline(
        lang='en',
        processors='tokenize',
        verbose=False
    )
    document = tokenizer(raw_text)

    # Get the sentences and the number of setnences in the document
    sentences = document.sentences
    number_of_sentences_in_document = len(sentences)

    # Use the same prompt template to summarize each of the
    # NUM_SENTENCES. For some reason, langchain doesn't like if you
    # split the template string over multiple lines
    prompt = PromptTemplate(
      input_variables=["text_to_summarize"],
      template="Can you please summarize the following text in 10 words: {text_to_summarize}?",
    )

    # Define which LLM we want to use. Right now, limit it to OpenAI
    # or HuggingFaceHub.
    llm = LLMSpecification(MODEL_HUB, MODEL_NAME).get_llm()

    # Sequentially get the next NUM_SENTENCES.
    summaries = []
    for i in range(
        0,
        number_of_sentences_in_document,
        NUM_SENTENCES
    ):
        next_sentences = get_next_sentences(document, i, NUM_SENTENCES)
        chain = LLMChain(llm=llm, prompt=prompt)
        summaries.append(chain.run(next_sentences))
        print("LLM's summary:\n" + summaries[-1])
        print("\n")
        print("The actual text:\n" + next_sentences)
        print("\n\n\n\n")
    

if __name__ == "__main__":
    main()




# hub_llm = HuggingFaceHub(repo_id="https://huggingface.co/gpt2")

