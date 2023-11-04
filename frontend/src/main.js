import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useLocation } from 'react-router-dom';
import './App.css';

function CogniFlow() {
  // const [userInput, setUserInput] = useState("")
  const [summary, setSummary] = useState("")
  const [humanText, setHumanText] = useState('')
  const [conversation, setConversation] = useState('')
  const [status, setStatus] = useState('')
  const [summaries, setSummaries] = useState("")
  const [listItems, setListItems] = useState("")

  const { state } = useLocation()
  const id = state.id
  console.log(state)


  // const { id } = useParams() // on way

  //^ is a shortcut to do this



  // const newId = paramsObject.id
  // useParams is passing an object with all the params. it will be
  // a dictionary {id : 22}. Instead of assigning the object to the var
  // (e.g. const new value = var.id), just immediately
  // assign id to this variable id.

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
    setHumanText('')
    setConversation(response.data.conversation)
    setStatus(response.data.status)
    const summaries = JSON.parse(response.data.summaries)
    console.log(summaries)
    const listItems = summaries.map((summary) =>
    <li>{summary}</li>
    );
    setListItems(listItems)
    // Could also have done
    // axios.post('http://127.0.0.1:5000/', formData).then(response => setSummary(response.data.summary))
  }
  
  return (
    <div className="App">
      <header className="App-header">
        {/*<p>Init ouptut is: {initOutput}</p>*/}
        <p>The id is: {id}</p>
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
        <p>
            {summary}
            <br/>
            <br/>
            {status}
            <br/>
            <br/>
            <ul>{listItems}</ul>
        </p>
      </header>
    </div>
  )
}

export default CogniFlow;
