import logo from './logo.svg';
import './App.css';
import React, { useEffect, useState } from 'react';
import axios from 'axios'


class Form extends React.Component {
  state = {
    summary: '',
  };

  handleSubmit = (e) => {
    e.preventDefault();

    // Read the form data
    const form = e.target;
    const formData = new FormData(form);

    // Pass formData as a fetch body directly
    fetch('http://127.0.0.1:5000/', {
      headers: {
        Accept: 'application/json',
      }, method: form.method, body: formData
    })
      .then(function (response) {
        return response.json();
      })
      .then(data =>
        this.setState({
          summary: data
        }));
  };


  render() {
    return (
      <div className="App">
        <header className="App-header">
          <form method="post" onSubmit={this.handleSubmit}>
            {<label>
              input number of sentences
          <input name="numSentences" defaultValue="" />
        </label>}
            <label>
              <textarea
                name="postContent"
                defaultValue="Paste the text here.."
                rows={20}
                cols={80}
              />
            </label>
            <hr />
            <button type="submit">Get Summary</button>
          </form>
          <p>Your summary is: {this.state.summary['summary']}</p>
          <img src={logo} className="App-logo" alt="logo" />
          <p>Cognition Flow</p>
        </header>
      </div>

    );
  }
}


export default Form;