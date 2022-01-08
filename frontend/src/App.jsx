import React from "react";
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import Home from "./components/Home";
import Room from "./components/Room";

const App = () => {
  return (
    <BrowserRouter>
       <Routes>
          <Route path='/' element={<Home/>} />
          <Route path='/rooms/:rooms_slug' element={<Room/>} />
          <Route path='/rooms/:rooms_slug/auth' element={<Home/>} />
       </Routes>
    </BrowserRouter>
  );
}

export default App;
