import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import NotFound from "./pages/NotFound";
import RegisterPage from "./pages/RegisterPage";
import CogniFlow from "./pages/CogniFlow";
import ProfilePage from "./pages/ProfilePage"
import LogoutPage from "./pages/LogoutPage";
import NavBar from "./components/NavBar";

const Router = () => {
  return (
    <BrowserRouter>
    <div className="App">
        <NavBar/>
        <Routes>
          <Route path="/" exact element={<LandingPage/>} />
          <Route path="/login" exact element={<LoginPage/>} />
          <Route path="/register" exact element={<RegisterPage />} />
          <Route path="/app" exact element={<CogniFlow/>}/>
          <Route path="/profile" exact element={<ProfilePage/>}/>
          <Route path="/logout" exact element={<LogoutPage/>}/>
          <Route path="*" element={<NotFound/>} />
        </Routes>
    </div>
    </BrowserRouter>
  );
};

export default Router;