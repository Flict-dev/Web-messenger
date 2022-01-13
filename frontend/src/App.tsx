import React from "react";
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import Home from "./components/home/Home";
import Room from "./components/room/Room";

const App:React.FC = () => {
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
