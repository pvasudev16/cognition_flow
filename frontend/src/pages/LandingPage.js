import React, {useState, useEffect} from 'react'
import httpClient from '../httpClient';
import { Link } from 'react-router-dom';

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
            <div class="bodycontent">
                <div>
                    <h1 class="title">CogniFlow</h1>
                    <h2 class="subtitle">Let's Make Reading Easy And Fun!</h2>
                    <p className="bodytext">
                        CogniFlow is an AI reading assistant that helps you read
                        web articles in digestible chunks.
                    </p>
                </div>
                {user != null ? (
                    <div>
                        <p className="bodytext">
                            To get started, specify the URL of the website
                            you'd like to read followed by the number of
                            sentences you'd like to read at a time.
                        </p>
                        <form>
                            <div className="leftalign">
                                <label>URL: </label>
                                <input
                                    type="text"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    className="url"
                                />
                            </div>
                            <div className="leftalign">
                                <label>Number of sentences: </label>
                                <input
                                    type="text"
                                    value={numSentences}
                                    onChange={(e) => setNumSentences(e.target.value)}
                                    className="numSentences"
                                />
                                <br/>
                            </div>
                            <div className="leftalign">
                                <button
                                    type="button"
                                    onClick={() => initializeParametersSubmit()}
                                    className="buttons"
                                >
                                    Get started reading!
                                </button>
                            </div>
                        </form>
                    </div>
                ) : (
                    <div className="leftalign">
                        <p className='bodytext'>
                            To get started, <Link to="/login" className='App-link'>login</Link> or <Link to="/register" className='App-link'>register</Link>!
                        </p>
                    </div>
                )}
                <div>
                    <br/>
                    <h2 class="subtitle">How it works:</h2>
                    <iframe
                        width="800px"
                        height="447px"
                        src="https://www.youtube.com/embed/rFfomw-Z4uE?si=ZBP0U1FiD1VxeuQ9"
                        title="YouTube video player"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        allowfullscreen
                    />
                </div>
                <div className="leftalign">
                    <p className='bodytext'>
                        CogniFlow gets the text from long articles, processs it to understand it
                        just like you or I, and it shows it to you in segments of a few sentences.
                        CogniFlows displays a summary of the sentences followed by the sentences themselves.
                        In between, you can ask CogniFlow questions or have a conversation. Try it out!
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LandingPage;