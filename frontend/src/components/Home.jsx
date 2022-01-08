import React, { useState, useEffect } from "react";
import CreateForm from "./CreateForm";

const Home = () => {
  const [ip, setIP] = useState("");

  const getIP = async () => {
    const requestOptions = {
      'method': 'GET',
      'headers': {
        'Content-type': 'application/json'
      },
    };

    await fetch('/v1/', requestOptions)
      .then(response => {
        if (response.ok){
          return response.json();
        }else{
          console.error('Error!')
        };
      }).then(data => {setIP(data.ip);});
  };

  useEffect(() => {
    getIP();
  }, [])

  return (
    <div className="App">
      <h1>Hello friend from {ip}</h1>
      <CreateForm/>
    </div>
  );
};

export default Home