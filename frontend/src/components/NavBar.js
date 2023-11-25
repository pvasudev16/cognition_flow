import React, { useState, useEffect} from "react";
import httpClient from "../httpClient";

import "./NavBar.css";
import { Link, NavLink } from "react-router-dom";

// Taken from https://github.com/CodeCompleteYT/react-navbar

const NavBar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
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

    return (
        <nav>
            <Link to="/" className="title">
                Website
            </Link>
            <div className="menu" onClick={() => setMenuOpen(!menuOpen)}>
                <span></span>
                <span></span>
                <span></span>
            </div>
            <ul className={menuOpen ? "open" : ""}>
            {
                user != null ? (
                    <>
                        <li>
                            <NavLink to="/profile">Profile</NavLink>
                        </li>
                        <li>
                            <NavLink to="/dummy" onClick={logoutUser}>Logout</NavLink>
                        </li>
                    </>
                ) : (
                    <>
                        <li>
                            <NavLink to="/login">Login</NavLink>
                        </li>
                        <li>
                            <NavLink to="/register">Logout</NavLink>
                        </li>
                    </>
                )
            }
            </ul>
        </nav>
    );
};

export default NavBar;