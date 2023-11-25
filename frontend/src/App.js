import './App.css';
import React, { useEffect, useState } from 'react';

import { BrowserRouter as Router, Route, Routes, Link, useParams } from 'react-router-dom';
import LandingPage from './landing_page';
import CogniFlow from './main';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <Router>
          <div>
            <Link className="App-link" to="/">Landing</Link> | <Link className="App-link" to="/cogniflow">CogniFlow</Link>
          </div>
          <Routes>
            <Route exact path="/cogniflow" element={<CogniFlow/>}/>
            <Route path="/" element={<LandingPage/>}/>
            {/* <Route path="/:id" element={<LandingPage/>}/> */}
          </Routes>
        </Router>
      </header>
    </div>
  );
}

export default App