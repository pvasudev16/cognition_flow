import React, {useState, useEffect} from 'react';
import httpClient from '../httpClient';

const CogniFlow = () => {
    // const [summary, setSummary] = useState(null)
    // const [status, setStatus] = useState(null)
    let [listItems, setListItems] = useState([])
    const [humanText, setHumanText] = useState(null)

    const chatbotIO = async (e) => {
        // Post the human message so it's in the database
        let response = await httpClient.post(
            "//localhost:5000/post_human_message",
            {
                humanText
            }
        )
        let conversation = JSON.parse(response.data.conversation);
        let listItems = conversation.map((conversationElement) =>
            <div>{conversationElement}</div>
        );
        setListItems(listItems)

        // Get the AI response; post the human message again.
        response = await httpClient.post(
            "//localhost:5000/get_ai_response",
            {
                humanText
            }
        )
        conversation = JSON.parse(response.data.conversation);
        listItems = conversation.map((conversationElement) =>
            <div>{conversationElement}</div>
        );
        setListItems(listItems)
    }

    return(
        <div>
            <div>
                {listItems}
            </div>
            <div>
                <form>
                    <textarea
                        name="humanMessage"
                        rows={5}
                        cols={80}
                        value={humanText}
                        onChange={e => setHumanText(e.target.value)}
                    />
                </form>
                <button type="button" onClick={() => chatbotIO()}>
                    Return
                </button>
            </div>
        </div>
    )
};

export default CogniFlow;