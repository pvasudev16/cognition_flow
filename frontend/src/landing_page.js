import React, { useState, useEffect } from 'react';
import axios from 'axios'

function LandingPage() {
  const [landingData, setLandingData] = useState('');

  useEffect(() => {
    // fetch('/landing')
    //   .then(response => response.text())
    //   .then(data => {
    //     setLandingData(data);
    //   });
    axios.post('http://127.0.0.1:5000/landing').then(response => {setLandingData(response.data)})
  }, []);

return (
<div className="landing-page">
    <header>
    <h1>Welcome to My Website</h1>
    </header>
    <section className="content">
      <p>{landingData}</p>
      <button>Get Started</button>
    </section>
    <footer>
      &copy; 2023 Your Website
    </footer>
</div>
);
}

export default LandingPage;
