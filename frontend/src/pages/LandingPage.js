import React, {useState, useEffect} from 'react'
import httpClient from '../httpClient';
import Cookies from 'js-cookie'

const LandingPage = () => {
    const [user, setUser] = useState(null)

    const logoutUser = async () => {
        await httpClient.post("//localhost:5000/logout");
        Cookies.remove("token", {path : "/"})
        window.location.href = "/";
    };

    useEffect(() => {
        (async () => {
            try {
                const token = Cookies.get("token")
                // console.log(token)
                const resp = await httpClient.get(
                    "//localhost:5000/@me",
                    {
                        headers : {
                            "token" : token
                        }
                    }
                );
                // console.log(resp)
                setUser(resp.data);
            } catch(error) {
                // console.log("Not authenticated")
                Cookies.remove("token", {path : "/"})
            }
        })();
    }, []);

    return(
        <div>
            <h1>Welcome to CogniFlow!</h1>
            {user != null ? (
                <div>
                    <h2>Logged in</h2>
                    <h3>ID: {user.id}</h3>
                    <h3>Email: {user.email}</h3>
                    <button onClick={logoutUser}>Logout</button>
                </div>
            ) : (
                <div>
                    <p>You aren't logged in</p>
                    <div className="buttons">
                        <a href="/login">
                            <button>Login</button>
                        </a>
                        <a href="/register">
                            <button>Register</button>
                        </a>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LandingPage;