import React, {useState} from 'react'
import httpClient from '../httpClient'

const LoginPage = () => {
    const [email, setEmail] = useState("pvasudev@pvasudev.ca")
    const [password, setPassword] = useState("Shrinkulitos")

    const logInUser = async (e) => {
        console.log(email, password);
        try {
            await httpClient.post("//localhost:5000/login",{
                email,
                password
            });
            window.location.href = "/";
        }
        catch(error) {
            if (error.response.status === 401)
            {
                alert("Invalid credentials")
            }
        }
    };
    return (
        <div class="App">
            <h1>Log into your account </h1>
            <form>
                <div>
                    <label>Email:</label>
                    <input
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    id="f"
                    />
                </div>
                <div>
                    <label>Password:</label>
                    <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    id="i"
                    />
                </div>
                <button type="button" onClick={() => logInUser()}>
                    Submit
                </button>
            </form>
        </div>
    );
};

export default LoginPage;