import React, { useState} from "react";
import httpClient from "../httpClient";
import Cookies from 'js-cookie'

const RegisterPage =() => {
  const [email, setEmail] = useState("pvasudev@pvasudev.ca");
  const [password, setPassword] = useState("Shrinkulitos");

  const registerUser = async () => {
    try {
      const response = await httpClient.post("//localhost:5000/register", {
        email,
        password,
      });

      // Get the token and store it in a cookie
      Cookies.set("token", response.data.token, {path : "/"})
      // console.log(Cookies.get('token'));

      window.location.href = "/";
    } catch (error) {
      if (error.response.status === 401) {
        alert("Invalid credentials");
      }
      else if(error.response.status === 409) {
        alert("User already exists")
      }
    }
  };

  return (
    <div>
      <h1>Create an account</h1>
      <form>
        <div>
          <label>Email: </label>
          <input
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            id="sfsdf"
          />
        </div>
        <div>
          <label>Password: </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            id="sdfsdf"
          />
        </div>
        <button type="button" onClick={() => registerUser()}>
          Submit
        </button>
      </form>
    </div>
  );
};

export default RegisterPage;