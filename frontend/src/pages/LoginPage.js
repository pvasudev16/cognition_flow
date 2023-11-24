import React, {useState} from 'react'
import httpClient from '../httpClient'
import Cookies from 'js-cookie'

const LoginPage = () => {
    const [email, setEmail] = useState("pvasudev@pvasudev.ca")
    const [password, setPassword] = useState("Shrinkulitos")

    const logInUser = async (e) => {
        console.log(email, password);
        try {
            const response = await httpClient.post("//localhost:5000/login",{
                email,
                password
            });

            // Get the token and store it in a cookie
            Cookies.set("token", response.data.token, {path : "/"})
            console.log(Cookies.get('token'));

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
        <div>
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