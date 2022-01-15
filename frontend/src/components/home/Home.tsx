import React, { useState, useEffect } from "react";
import CreateForm from "./CreateForm";
import { RequestOtions } from "../../utils/reuests";

const Home = () => {
  const [ip, setIP] = useState("");

  const getIP = async () => {
    const rOptions = RequestOtions.Get({ "Content-type": "application/json" });

    await fetch("/v1/", rOptions)
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          console.error("Error!");
        }
      })
      .then((data) => {
        setIP(data.ip);
      });
  };

  useEffect(() => {
    getIP();
  }, []);

  return (
    <div className="App">
      <h1>Hello friend from {ip}</h1>
      <CreateForm />
    </div>
  );
};

export default Home;
