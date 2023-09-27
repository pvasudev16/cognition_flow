import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios'

const App = () => {
  // const [userInput, setUserInput] = useState("")
  const [summary, setSummary] = useState("")
  const [initOutput, setInitOutput] = useState("")

  // For debugging
  console.log(summary)
  console.log(initOutput)

  const handleSubmit = async (e) => {
    e.preventDefault();

    console.log(e);

    // Read the form data
    const form = e.target;
    const formData = new FormData(form);
    // setUserInput("")
    const response = await axios.post('http://127.0.0.1:5000/', formData)
    setSummary(response.data.summary)
    // Could also have done
    // axios.post('http://127.0.0.1:5000/', formData).then(response => setSummary(response.data.summary))
  }

  const initParamsSubmit = async (e) => {
    e.preventDefault();
    console.log(e);
    const form = e.target;
    const formData = new FormData(form);
    const response = await axios.post('http://127.0.0.1:5000/initialization', formData)
    setInitOutput("ohHai")
  }

  return (
    <div className="App">
      <header className="App-header">
        <form onSubmit={initParamsSubmit} method="post">
          {/*
            Use this to clear the field after hitting submit
            <label>
              NUM_SENTENCES:
              <input
                name="NUM_SENTENCES"
                onChange={(e)=>setUserInput(e.target.value)}
                value={userInput}/>
            </label>
          */}
          <label>
            NUM_SENTENCES:
            <input
              name="NUM_SENTENCES"
              defaultValue="3"
            />
          </label>
          <br/>
          <label>
            PATH_TO_FILE:
            <input
              name="PATH_TO_FILE"
              defaultValue=""
            />
          </label>
          <br/>
          <label>
            MODEL_HUB:
            <input
              name="MODEL_HUB"
              defaultValue="OpenAI"
            />
          </label>
          <br/>
          <label>
            MODEL_NAME:
            <input
              name="MODEL_NAME"
              defaultValue="text-davinci-003"
            />
          </label>
          {/*<label>
            Enter the text you want to summarize
            <textarea
              name="postContent"
              defaultValue=""
              rows={20}
              cols={80}
            />
          </label>
          <hr /> */}
          <br/>
          <button type="submit">Get Summary</button>
        </form>
        <form> {/*onSubmit={humanInputSubmit}>*/}
          <label>
            This is where you write to the chatbot
            <textarea
              name="humanContent"
              defaultValue=""
              rows={20}
              cols={80}
            />
          </label>
        </form>
        <p>Initialization output is: {initOutput}</p>
      </header>
    </div>
  )
}

export default App