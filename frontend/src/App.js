import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios'

const App = () => {
  const [userInput, setUserInput] = useState("")
  const [summary, setSummary] = useState("")

  // For debugging
  console.log(summary)

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Read the form data
    const form = e.target;
    const formData = new FormData(form);
    setUserInput("")
    const response = await axios.post('http://127.0.0.1:5000/', formData)
    setSummary(response.data.summary)
    // Could also have done
    // axios.post('http://127.0.0.1:5000/', formData).then(response => setSummary(response.data.summary))
  }

  return (<div className="App">
          <header className="App-header">
            <form onSubmit={handleSubmit}>{ // method="post"
              <label>
                Input the number of sentences you wish to summarize at
                a time
                <input name="numSentences" onChange={(e)=>setUserInput(e.target.value)} value={userInput}/>
              </label>
            }
            <br></br>
              <label>
                Enter the text you want to summarize
                <textarea
                  name="postContent"
                  defaultValue=""
                  rows={20}
                  cols={80}
                />
              </label>
              <hr />
              <button type="submit">Get Summary</button>
              {/* <button type="submit">Get Summary</button> */}
            </form>
            <p>Your summary is: {summary}</p>
            <p>Cognition Flow</p>
          </header>
        </div>)
}

export default App