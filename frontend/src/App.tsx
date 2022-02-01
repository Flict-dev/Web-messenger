import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./components/home/Home";
import Room from "./components/room/Room";

import "./style/Default.css";
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/rooms/:rooms_slug" element={<Room />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
