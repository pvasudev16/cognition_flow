import React, { useState, useEffect } from 'react';
import axios from 'axios'
import { useNavigate } from 'react-router-dom';

function LandingPage() {
  const navigate = useNavigate()
  const [landingData, setLandingData] = useState('');
  const [initOutput, setInitOutput] = useState("")
  const [id, setID] = useState("")

  useEffect(() => {
    // fetch('/landing')
    //   .then(response => response.text())
    //   .then(data => {
    //     setLandingData(data);
    //   });
    axios.post('http://127.0.0.1:5000/landing').then(response => {setLandingData(response.data)})
  }, []);

  const initParamsSubmit = async (e) => {
    e.preventDefault();
    // console.log(e);
    const form = e.target;
    const formData = new FormData(form);
    const response = await axios.post('http://127.0.0.1:5000/initialization', formData)
    setInitOutput(response.data.initialized)
    // setID(response.data.id) by the time we get to the next line,
    // since these are asynchronous requests, the variable "id" prb
    // isn't defined; to make sure it works, just do response.data.id
    // directly

    navigate(`/cogniflow`, {state: {id: response.data.id}})
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
              defaultValue="../elephants_short.txt"
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
      </header>
    </div>
);

}

export default LandingPage;
