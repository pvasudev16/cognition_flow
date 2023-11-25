import React, {useState, useEffect} from 'react'
import httpClient from '../httpClient';

const LandingPage = () => {
    const [user, setUser] = useState(null)
    const [url, setUrl] = useState("https://www.theguardian.com/football/2023/nov/24/premier-league-10-things-to-look-out-for-this-weekend")
    const [numSentences, setNumSentences] = useState(3)

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

    const initializeParametersSubmit = async (e) => {
        const response = await httpClient.post(
            "//localhost:5000/initialization", {
                url,
                numSentences
            }
        );
        console.log(response)
        window.location.href = "/app";
    }

    return(
        <div class="App">
            <h1>Welcome to CogniFlow!</h1>
        
            {user != null ? (
                <div>
                    <h2>
                        Welcome {user.email}, identified by {user.id}!
                    </h2>
                    <p>
                        To get started, specify the URL of the website
                        you'd like to read followed by the number of
                        sentences you'd like to read at a time.
                    </p>
                    <form>
                        <div>
                            <label>URL: </label>
                            <input
                                type="text"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                id="url"
                            />
                            </div>
                            <div>
                            <label>Number of sentences: </label>
                            <input
                                type="text"
                                value={numSentences}
                                onChange={(e) => setNumSentences(e.target.value)}
                                id="sdfsdf"
                            />
                        </div>
                        <button type="button" onClick={() => initializeParametersSubmit()}>
                        Submit
                        </button>
                    </form>
                    <p>
                        If you're done, thanks for using CogniFlow!
                    </p>
                    <button onClick={logoutUser}>Logout</button>
                </div>
            ) : (
                <div>
                    <p>
                        CogniFlow is an AI reading assistant that helps you 
                        read and understand articles on the Internet quickly.
                        CogniFlow displays the article by showing you summaries
                        of some sentences followed by the sentences themselves.
                        In between summaries, you can interact with the AI 
                        assistant and ask it questions to enhance your reading
                        experience!
                    </p>
                    <p>To get started, login!</p>
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