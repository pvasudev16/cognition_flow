from src.models.llm_specification_model import LLMSpecification


import stanza
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


def get_next_sentences(
    document : stanza.Document,
    starting_position : int,
    number_of_sentences : int
):
    sentences = ""
    for j in range(int(number_of_sentences)):
        if starting_position + j >= len(document.sentences):
            break
        sentences += document.sentences[starting_position + j].text
        sentences += " "
    return sentences


def cogniflow_core(raw_text, num_of_sentences, model_hub, model_name):
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
      template="{text_to_summarize}?",
    )


    # Define which LLM we want to use. Right now, limit it to OpenAI
    # or HuggingFaceHub.
    llm = LLMSpecification(model_hub, model_name).get_llm()

    # Sequentially get the next num_of_sentences.
    summaries = []

    print(f"{num_of_sentences=}, {number_of_sentences_in_document=}")
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(raw_text)
    for i in range(
        0,
        number_of_sentences_in_document,
        int(num_of_sentences)
    ):
        next_sentences = get_next_sentences(document, i, num_of_sentences)
        print(f"{next_sentences=}")
        chain = LLMChain(llm=llm, prompt=prompt)
        summaries.append(chain.run(next_sentences))
        print(f"{summaries=}")
        print("LLM's summary:\n" + summaries[-1])
        print("\n")
        print("The actual text:\n" + next_sentences)
        print("\n\n\n\n")
    
    return response