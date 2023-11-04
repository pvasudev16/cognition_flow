import React, { useState, useEffect} from 'react';
import axios from 'axios'
import { useLocation } from 'react-router-dom';
import './App.css';

function CogniFlow() {
  // const [userInput, setUserInput] = useState("")
  const [summary, setSummary] = useState("")
  const [status, setStatus] = useState("")
  let [listItems, setListItems] = useState([])

  const { state } = useLocation()
  const id = state.id

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Read the form data
    const form = e.target;
    const formData = new FormData(form);
    let response = await axios.post('http://127.0.0.1:5000/post_human_message', formData)
    let convo = JSON.parse(response.data.conversation)
    let listItems = convo.map((conversationElement) =>
    <div>{conversationElement}</div>
    );
    setListItems(listItems)
    console.log(listItems)
    response = await axios.post('http://127.0.0.1:5000/get_ai_response', formData)

    // Kill these two afterwards; just for debugging
    setSummary(response.data.summary)
    setStatus(response.data.status)
    convo = JSON.parse(response.data.conversation)
    listItems = convo.map((conversationElement) =>
    <div>{conversationElement}</div>
    );
    setListItems(listItems)
  }
  
  return (
    <div className="App">
      <header className="App-header">
        <div class="flex-container">
            {listItems}
        </div>
        <p>DEBUGGING: ID={id}</p>
        <br/>
        <br/>
        <form onSubmit={handleSubmit}>
          <input
            name="ID"
            value={id}
            type="hidden"
          />
          <br/>
          <label>
            <br/>
            <textarea
              name="HUMAN_MESSAGE"
              defaultValue=""
            //   value={humanText}
            //   onChange={e => setHumanText(e.target.value)}
              rows={5}
              cols={80}
            />
          </label>
          <br/>
          <button type="submit">Return</button>
        </form>
      </header>
    </div>
  )
}

export default CogniFlow;
