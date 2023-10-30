import './App.css';
import React, { useEffect, useState } from 'react';

import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import LandingPage from './landing_page';
import CogniFlow from './main';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <Router>
          <div>
            <Link className="App-link" to="/">Main</Link> | <Link className="App-link" to="/landing">Landing</Link>
          </div>
          <Routes>
            <Route exact path="/" element={<CogniFlow/>}>
              Main page
            </Route>
            <Route path="/landing" element={<LandingPage/>}>
              Hello this is landing page
            </Route>
          </Routes>
        </Router>
      </header>
    </div>
  );
}

export default App