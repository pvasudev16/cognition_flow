# Cognition Flow
Noun: An app that summarizes and displays text in digestible bits
Verb: The act of running Cognition Flow

FYI, "CogniFlow" is the marketing name of the app

## Quickstart Guide
For something that works, run:
```bash
python3 main.py ./elephants_short.txt 4 OpenAI text-davinci-003
```
(You'll need to get some OpenAI credits).

For something that works less well, but is free, run:
```bash
python3 main.py ./elephants_short.txt 4 HuggingFaceHubg gpt2
```

Positional arguments are:
1. Path to the file containing text to Cognition Flow
2. The number of sentences to be displayed and summarized
3. Either "OpenAI" or "HuggingFaceHub" specifying where to look for the LLM.
   This is the so-called model hub.
4. The model name. If the model hub is "OpenAI" then write "text-davinci-003".
   If the model hub is "HuggingFaceHub", then you have some choices.
   Find a model on [HuggingFace](https://huggingface.co/) and then copy
   everything in the URL after "huggingface.co". So, for example:
   "gpt2" or "nomic-ai/gpt4all-j". (The former doesn't really work,
   and the latter doesn't work at all)

Using OpenAI's davinci-text-003 model to summarize the text in
`./elephants_short.txt`, this is the output:
```
$python3 main.py ./elephants_short.txt 4 OpenAI text-davinci-003
LLM's summary:
Elephants are largest land animals; three species survive; family Elephantidae and order Proboscidea.

The actual text:
Elephants are the largest existing land animals. Three living species 
are currently recognised: the African bush elephant, the African forest 
elephant, and the Asian elephant. They are the only surviving members 
of the family Elephantidae and the order Proboscidea. The order was 
formerly much more diverse during the Pleistocene, but most species 
became extinct during the Late Pleistocene epoch. 


LLM's summary:
Elephants have trunk, tusks, large ears, legs. Trunk used for breathing, tusks for weapons, ears for communication.

The actual text:
Distinctive features 
of elephants include a long proboscis called a trunk, tusks, large ear 
flaps, pillar-like legs, and tough but sensitive skin. The trunk is 
used for breathing and is prehensile, bringing food and water to the 
mouth, and grasping objects. Tusks, which are derived from the incisor 
teeth, serve both as weapons and as tools for moving objects and digging.
The large ear flaps assist in maintaining a constant body temperature 
as well as in communication. 

LLM's summary:
Africans: large ears, concave backs; Asians: small ears, convex/level backs.

The actual text:
African elephants have larger ears and 
concave backs, whereas Asian elephants have smaller ears, and convex 
or level backs. 
```

## Setup

### Get API access to HuggingFace and/or OpenAI
Get an API key from OpenAI and HuggingFaceHub.

For OpenAI, log into your account and go to your profile, and you should
be able to manage your API tokens. If you lose yours, make a new one
and copy it. Save it in a password manager or somewhere safe.

For a HuggingFaceHub API token, go to your HuggingFace profile, click
settings, and click Tokens. You should be able to copy yours.

Once you have these tokens, create a file called `.env` in the same
directory as the `main.py` folder. In it, it should look like:
```bash
HUGGINGFACEHUB_API_TOKEN=hf_m0reG4Rb4gEhErE4nDM0R3G4rb4g3
OPEN_AI_KEY=sk-g4arb4geEL0NMU5KL0V35R0BdeS4n7I5 
```

### Python virtual environment and packages
Make a [Python virtual environment](https://docs.python.org/3/library/venv.html)
for this project. (If you're using Windows
replace `python3` with `python`). 
```bash
python3 -m venv ./my_venv
```

and then activate it
```bash
source ./my_venv/bin/activate # Mac
.\my_venv\Scripts\Activate.ps1 # Windows PowerShell
```

Then install the requirements via
```bash
python3 -m pip install -r requirements.txt
```
## Roadmap
Lowest-hanging fruit:
- Incorporate a reading time estimate

Next lowest-hanging fruit:
- After summarizing and displaying the first `N` sentences, wait for
  user input before proceeding. Right now, it just cycles through
  the whole text.

Higher hanging fruit (but not that hard)
- Introduce some user-feedback and conversation. At the beginning,
  Cognition Flow can greet the user. Then as the summaries go on,
  Cognition Flow can ask the user if they are satisfied, and re-adjust
  the number of sentences to summarize and display.
- Introduce metrics on the summarization, as outlined [here](https://python.langchain.com/en/latest/modules/chains/index_examples/summarize.html)

The next steps:
- Wrap this basic functionality up in a Django (or other) framework
- With the Django framework, use React to display the text word-by-word
  instead of using a Python-style print-dump. To see what I mean here,
  think of how chatGPT replies to your queries when you use it.
- Write up an API to ping CogniFlow. A base idea could be to ping it
  with the command line arguments shown above.


