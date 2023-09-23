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
    axios.post('http://127.0.0.1:5000/', formData).then(function (response) {
              console.log(response)
              return response.data;
          })
          .then(data =>
            this.setState({
              summary: data
            }));
          }
  //   fetch('http://127.0.0.1:5000/', { // fetch("http://127.0.0.1:5000/test")
  //     headers: {
  //       Accept: 'application/json',
  //     }, method: form.method, body: formData
  //   })
  //     .then(function (response) {
  //       return response.json();
  //     })
  //     .then(data =>
  //       this.setState({
  //         summary: data
  //       }));
  // };

  // Use an array-map a method in every array in javascript
  // iterates thru the array. use a map method on every element.
  // 

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <form onSubmit={this.handleSubmit}>{ // method="post"
            <label>
              Input the number of sentences you wish to summarize at
              a time
              <input name="numSentences" defaultValue=""/>
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
          <p>Your summary is: {this.state.summary['summary']}</p>
          <p>Cognition Flow</p>
        </header>
      </div>
    );
  }
}


export default Form;