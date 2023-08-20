import sys
from typing import *
import stanza
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import dotenv
from langchain.llms import HuggingFaceHub, OpenAI


from src.models.llm_specification_model import LLMSpecification
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

    # Define memory.
    # Every prompt will need a "human_input" input, even if it's 
    # not actually the human inputting it. E.g. it might be
    # NUM_SENTENCES of the document we've parsed
    memory=ConversationBufferMemory(
        memory_key="chat_history",
        input_key="human_input"
    )

    # PERSONA
    ## Define our reader's persona
    template = (
        """You are a kind and compassionate assistant. Your main role is
        to help people read. You are having a conversation with a human.
        Tell the human that when they are ready to start they can tell
        you. If the human indicates that they are ready to start
        output the phrase "Let's go" exactly. Continue the conversation
        with the human until they tell you they are ready to go.
        
        {chat_history}
        
        Human: {human_input}
        Chatbot:"""
    )

    # WELCOME
    ## Make a chat prompt for the reader to welcome the user to
    ## CogniFlow
    chat_prompt = PromptTemplate(
        input_variables=["chat_history", "human_input"],
        template=template
    )

    conversation_chain = LLMChain(
        llm=llm,
        prompt=chat_prompt,
        verbose=False,
        memory=memory
    )

    ready_to_go = False
    while not ready_to_go:
        user_input = input("Human: ")
        bot_output =  conversation_chain.predict(human_input=user_input)
        print("Chatbot: " + bot_output)
        if "Let's go" in bot_output:
            ready_to_go = True
    

    # DOCUMENT PRE-PROCESSING
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

    # DOCUMENT SUMMARIZATION
    # We have a conversation chat bot prompt template for the
    # conversation. Use a different prompt to do
    # the summaries of NUM_SENTENCES. After displaying the summary
    # and the actual text, the conversation bot will converse with
    # the user.

    intro_prompt = PromptTemplate(
        input_variables=[
            "human_input",
            "number_of_sentences",
            "chat_history"
        ],
        template=(
            """Here is the chat history so far:
            
            {chat_history}
            
            Start by telling the user what you will do.
            Tell the user you'll display a summary of
            {number_of_sentences} sentences, followed by the actual text
            itself. Tell the user they can discuss each summary with
            you. Tell the user they can indicate to keep going 
            or to stop. If the user indicates they want to
            keep going, output "Let's keep going" exactly. If the user
            indicates they want to stop, output "Let's stop" exactly".
            
            {human_input}"""
        )
    )

    # Note that this prompt does not accept any human_input. We are
    # just 
    summary_prompt = PromptTemplate(
        input_variables=[
            "human_input", # human_input is actually the text we
                           # want to summarize
            "chat_history",
        ],
        template=(
            """You are a kind and compassionate assistant. Your main
            role is to help people read. Here is the chat history
            so far:
        
            {chat_history}

            Now please summarize the following text in 10 words:
        
            {human_input}
            """
        )
    )

    # Make a prompt that will be used to discuss each of the summaries.
    # It needs a human_input as a prompt for the chat.
    discussion_prompt = PromptTemplate(
        input_variables=[
            "human_input",
            "most_recent_summary",
            "summaries",
            "chat_history"
        ],
        template=(
            """You are a kind and compassionate assistant. Your main role
            is to help people read. Here is the chat history so far:

            {chat_history}
            
            Here is the most recent summary:

            {most_recent_summary}

            and here is a summary of the text so far:

            {summaries}

            Help the user by answering any questions they may have. For
            example, if they ask you to define a word, define it for
            them. If the human indicates that they are ready to continue
            then output the phrase "Let's keep going" exactly. If the
            human indicates they are ready to quite, output the phrase
            "Let's stop" exactly.

            Human: {human_input}
            Chatbot:
            """
        )
    )

    # Make a prompt that will thank the user for using CogniFlow
    end_prompt = PromptTemplate(
        input_variables=[
            "human_input",
            "chat_history"
        ],
        template=(
            """This is the chat history so far:
            {chat_history}

            Tell the user that they made it to the end of the text
            and that they did good work. Thank the user and make sure
            to use "CogniFlow" in your thanks.
            
            {human_input}"""
        )
    )

    # Sequentially get the next NUM_SENTENCES.
    summaries = []

    # Cursor to track what sentence we're at in the text. Start
    # at the beginning
    c = 0

    # Specify which chain we want to use
    intro_chain = LLMChain(
        llm=llm,
        prompt=intro_prompt,
        memory=memory,
        verbose=False
    )

    summary_chain = LLMChain(
        llm=llm,
        prompt=summary_prompt,
        memory=memory,
        verbose=False
    )

    discussion_chain = LLMChain(
        llm=llm,
        prompt=discussion_prompt,
        memory=memory,
        verbose=False
    )

    end_chain = LLMChain(
        llm=llm,
        prompt=end_prompt,
        memory=memory,
        verbose=False
    )

    # Get the bot to tell the user how to use this tool.
    instruction_output = intro_chain.predict(
        human_input="",
        number_of_sentences=NUM_SENTENCES,
    )
    print(instruction_output)

    # Flag indicating whether the user is ready to keep going or not
    # By default, assume they'll do one interation.
    keep_going = True

    while(keep_going):
        next_sentences = get_next_sentences(document, c, NUM_SENTENCES)
        summary = summary_chain.run(
            {"human_input" : next_sentences}
        )
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
        
        summaries.append(summary)

        continue_conversation = True

        while(continue_conversation):
            user_input = input("Human: ")
            discussion_output = discussion_chain.predict(
                human_input=user_input,
                most_recent_summary=summary,
                summaries=" ".join(summaries),
            )
            print("Chatbot: " + discussion_output)
            if "Let's keep going" in discussion_output:
                continue_conversation=False
            if "Let's stop" in discussion_output:
                continue_conversation=False
                keep_going=False

        print("\n\n")
    
    end_output = end_chain.predict(human_input="")
    print(end_output)


if __name__ == "__main__":
    main()