import React, {useState, useEffect} from 'react'
import httpClient from '../httpClient';

const LandingPage = () => {
    const [user, setUser] = useState(null)

    const logoutUser = async () => {
        await httpClient.post("//localhost:5000/logout");
        window.location.href = "/";
    };

    useEffect(() => {
        (async () => {
            try {
                const resp = await httpClient.get("http://127.0.0.1:5000/@me");
                console.log(resp)
                setUser(resp.data);
            } catch(error) {
                console.log("Not authenticated")
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