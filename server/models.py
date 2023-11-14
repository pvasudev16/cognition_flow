from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Following SQLAlchemy tutorial at 
# https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application

# For each CogniFlow session, we will have one Configuration record,
# which tracks the input parameters and the state of the conversation
class Configuration(db.Model):
    #### Primary integer key
    id = db.Column(db.Integer, primary_key=True)

    #### Input paramers:
    ####
    # Number of sentences to parse at a time
    num_sentences = db.Column(db.Integer)

    # Local path to text file or URL to web page
    path_to_file = db.Column(db.String(4096))

    # Model hub to use (by deafult, OpeanAI)
    model_hub = db.Column(db.String(100))

    # Model to use (by default, text-davinci-003) 
    model_name = db.Column(db.String(100))

    #### CogniFlow State Variables
    ####
    # A boolean flag indicating if CogniFlow has read in the
    # number of sentences to parse, the path to file/URL,
    # the model hub, and the model
    preprocessed = db.Column(db.Boolean)

    # The raw text read in from the URL or the text file. If 
    # path_to_file is a URL, this variable will not only hold the
    # actual text but also all the metadata
    raw_text = db.Column(db.Text)

    # The vector database. Get the embeddings (using the same
    # model_hub and model_name), chunk the text, and form a
    # FAISS vector database, holding the semantic meaning of the text
    vector_db = db.Column(db.LargeBinary)

    # The memory buffer as a string. To decode the memory into a
    # LangChain ConversationBufferMemory object, use
    # cfc.get_memory_buffer_from_string(). To encode a
    # ConversationBufferMemory object into a string, we just do
    # memory.buffer_as_str
    memory_buffer_string = db.Column(db.Text)

    # A JSON dump of the vector of the human-parseable sentences
    # in the text. This excludes any metadata/garbage in text
    # scraped from URLs.
    sentences = db.Column(db.Text)

    # The number of sentences in the text
    number_of_sentences_in_text = db.Column(db.Integer)

    # A cursor indicating how many sentences have been summarized
    # and displayed.
    cursor = db.Column(db.Integer)

    # A JSON dump of the conversation history, which will alternate
    # between what the chatbot says (including actual text of)
    # the article and what the human says.
    conversation_history = db.Column(db.Text)

    # A boolean flag indicating in the summarization whether
    # the user is ready to keep going.
    summarization_keep_going = db.Column(db.Boolean)

    # A JSON dump of the vector of summaries CogniFlow has made
    # so far
    summaries = db.Column(db.Text)

    # A boolean flag indicating after displaying the summaries if
    # to keep going in the conversation.
    summarization_continue_conversation = db.Column(db.Boolean)

    # Status
    status = db.Column(db.String(50))

    def __repr__(self):
        return f'memory_buffer: {self.memory_buffer_string}'