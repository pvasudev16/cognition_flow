import sys
from typing import *
import stanza
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import dotenv
from langchain.llms import HuggingFaceHub, OpenAI
from src.models.llm_specification_model import LLMSpecification
from src.services.cogniflow_core import get_next_sentences

# For chatbot
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


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
       whatever model you want from HuggingFaceHub
       (e.g. "google/flan-t5-xxl")
    """
    # Place holder: error check if they provide more than/less than four
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

    # Define which LLM we want to use. Right now, limit it to OpenAI
    # or HuggingFaceHub.
    llm = LLMSpecification(MODEL_HUB, MODEL_NAME).get_llm()

    # PERSONA
    ## Define our reader's persona
    persona = (
        "You are a friendly assistant meant to help people with "
        + "reading. You are attentive to individual's needs and kind. "
        + "You are trying to help people who may have difficulty "
        + "reading. "
    )

    # WELCOME
    ## Make a chat prompt for the reader to welcome the user to
    ## CogniFlow
    
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        persona
    )
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template
    )
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            system_message_prompt,
            human_message_prompt
        ]
    )

    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
    )
    welcome_message = chain.run(
        "Welcome the user to this app called \"CogniFlow\" and tell "
        + "them that they have already supplied a text file so we're "
        + "good to go. Make sure to explicitly welcome them to "
        + "\"CogniFlow\""
    )

    print(welcome_message + "\n")
    # print( "Welcome to CogniFlow!\n"
    #       + "I am your friendly reader assistant.\n"
    #       + "Since you're running me from the command line, you've\n"
    #       + "already supplied me with a text file and the number of\n"
    #       + "sentences you want to parse at a time.\n\n"
    #       + "I'm going to print a summary of the number of sentences\n"
    #       + "you supplied followed by the original text for you to "
    #       + "read.\n\n"
    #       + "As we go through the text, I'm going to ask you if you\n"
    #       + "want to continue. For now, just say anything to keep "
    #       + "going\nand write 'q' to quit.\n\n"
    #       + "Have fun!\n\nWhen you're ready to go, press any key."
    # )

    # PRELIMINARY DISCUSSION
    ## Have the assistant converse with the user. If the user tells
    ## them they're ready to go, then begin.
    conversation_prompt = (
        "Ask the user about themselves and about their needs. "
        + "Tell the user that if they are ready to start to let "
        + "you know. If the user does let you know they are ready to start "
        + "then make sure to use the words \"Let's begin\" "
        + "at the end of your response."
    )
    chain = LLMChain(
        llm=llm,
        prompt=chat_prompt
    )
    output = chain.run(conversation_prompt)
    print(output)
    ready_to_go = False
    while(not ready_to_go):
        user_input = input("User: ")
        print(user_input)
        output = chain.run(user_input)
        print(output)
        if "Let's begin" in output:
            ready_to_go = True
    print("\n\n")
    
    
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

    # Sequentially get the next NUM_SENTENCES.
    summaries = []

    # Flag whether to keep going or not
    keep_going = True

    # Cursor to track what sentence we're at in the text. Start
    # at the beginning
    c = 0

    # Specify which chain we want to use
    chain = LLMChain(llm=llm, prompt=prompt)

    while(keep_going):
        next_sentences = get_next_sentences(document, c, NUM_SENTENCES)
        summary = chain.run(next_sentences)
        print(
            "The summary of sentences "
            + str(c)
            + " to "
            + str(c + NUM_SENTENCES)
            + " is:"
        )

        print(summary + "\n")
        print("The actual text is:")
        print(next_sentences + "\n")

        # Advance the cursor by NUM_SENTENCES
        c += NUM_SENTENCES

        # If we've exceeded the total number of setences, break
        if c >= number_of_sentences_in_document:
            break

        keep_going_string = input("Keep going? ")
        if keep_going_string == "q":
            keep_going = False
        print("\n\n")


    # Below is just the for-loop implementation without asking for
    # user input.
    if False:
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