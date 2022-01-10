import React, {useState, useEffect} from 'react';
import RoomUsers from './RoomUsers';
import jwt_decode from "jwt-decode";
import {startRoom} from './utils/wsclient';
import {getCookie} from './utils/helpers';

const Room = () => {
    // let [users, setUser] = useState([])
    const url = document.location.pathname

    const initialRequest = async () => {
      const requestOptions = {
        'method': 'GET',
        'headers': {
          'Content-Type': 'application/json'
        },
      }; 
      const roomData = fetch(`/v1${url}`, requestOptions).then((response) => {
        if (response.ok){
          return response.json()
        }else{
          console.error()
        }
      })
    };
    
    

    useEffect(() => {
      startRoom(url, getCookie('session'))
    }, [])
    let users = {"John": {"name": "John", "status": true, "id": 1}, "Alice": {"name": "Alice", "status": true, "id": 2}}
    return (
      <div className="container">
        <div className="admin_container"></div>
        <div className="msg_container">
          <div className="messages"></div>
          <div className="send_wrapper">
            <input type="text" className="msg_input" id="msg_input"  placeholder="message" />
            <input type="submit" className="msg_btn" id="msg_btn" value="send" />
          </div>
        </div>
        <div className="users_container">
          <RoomUsers props={users}/>
        </div>
      </div>
    )
};

export default Room;