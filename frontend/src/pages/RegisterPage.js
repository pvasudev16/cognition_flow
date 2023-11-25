import React, { useState } from "react";
import httpClient from "../httpClient";

const RegisterPage =() => {
  const [email, setEmail] = useState("pvasudev@pvasudev.ca");
  const [password, setPassword] = useState("Shrinkulitos");

  const registerUser = async () => {
    try {
      await httpClient.post("//localhost:5000/register", {
        email,
        password,
      });

      window.location.href = "/";
    } catch (error) {
      if (error.response.status === 401) {
        alert("Invalid credentials");
      }
    }
  };

  return (
    <div class="App">
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