import React, {useState, useEffect} from 'react'
import httpClient from '../httpClient';
import { Link } from 'react-router-dom';

const LogoutPage = () => {
    useEffect(() => {
        window.location.href = "/";
    }, []);

    return(
        <div className='App'/>
    );
};

export default LogoutPage;