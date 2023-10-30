import React, { useState, useEffect } from 'react';

function LandingPage() {
//   const [landingData, setLandingData] = useState('');

//   useEffect(() => {
//     fetch('/landing')
//       .then(response => response.text())
//       .then(data => {
//         setLandingData(data);
//       });
//   }, []);

return (
<div className="landing-page">
    <header>
    <h1>Welcome to My Website</h1>
    </header>
    <section className="content">
   {/*<p>{landingData}</p>*/}
    <button>Get Started</button>
    </section>
    <footer>
    &copy; 2023 Your Website
    </footer>
</div>
);
}

export default LandingPage;
