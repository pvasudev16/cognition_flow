import React, { useState, useEffect } from 'react';
import axios from 'axios'

function CogniFlow() {
  const [mainData, setMainData] = useState('');

  useEffect(() => {
    // This will run when the component mounts
    fetch('/')
      .then(response => response.text())
      .then(data => {
        setMainData(data); // Store the data in your component's state
      });
  }, []); // The empty dependency array means this effect runs once when the component mounts

  // const [userInput, setUserInput] = useState("")
  const [summary, setSummary] = useState("")
  const [initOutput, setInitOutput] = useState("")
  const [id, setID] = useState("")

  // For debugging
  // console.log(summary)
  // console.log(initOutput)

  const handleSubmit = async (e) => {
    e.preventDefault();
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
    // console.log(e);
    const form = e.target;
    const formData = new FormData(form);
    const response = await axios.post('http://127.0.0.1:5000/initialization', formData)
    setInitOutput(response.data.initialized)
    setID(response.data.id)
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
              defaultValue="./elephants_short.txt"
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
          <button type="submit">Initialize</button>
        </form>
        {/*<p>Init ouptut is: {initOutput}</p>*/}
        {/*<p>The id is: {id}</p>*/}
        <br/>
        <br/>
        <form onSubmit={handleSubmit}>
        <label>
            ID:
            <input
              name="ID"
              value={id}
            />
          </label>
          <br/>
          <label>
            <br/>
            <textarea
              name="HUMAN_MESSAGE"
              defaultValue=""
              rows={5}
              cols={80}
            />
          </label>
          <br/>
          <button type="submit">Return</button>
        </form>
        <p>Chatbot ouptut is: {summary}</p>
      </header>
    </div>
  )
}

export default CogniFlow;
