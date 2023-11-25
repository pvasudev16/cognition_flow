import React, {useState, useEffect} from 'react'
import httpClient from '../httpClient';

const ProfilePage = () => {
    const [user, setUser] = useState(null)

    const logoutUser = async () => {
        await httpClient.post("//localhost:5000/logout");
        window.location.href = "/";
    };

    useEffect(() => {
        (async () => {
            try {
                const resp = await httpClient.get("//localhost:5000/@me");
                setUser(resp.data);
            } catch(error) {
                console.log("Not authenticated")
            }
        })();
    }, []);

    return(
        <div class="App">
            <h1>Welcome to CogniFlow!</h1>
            {user != null ? (
                <div>
                    <h2>
                        Welcome {user.email}, identified by {user.id}!
                    </h2>

                    <button onClick={logoutUser}>Logout</button>
                </div>
            ) : (
                <div>
                    <p>
                        You aren't logged in!
                    </p>
                </div>
            )}
        </div>
    );
};

export default ProfilePage;