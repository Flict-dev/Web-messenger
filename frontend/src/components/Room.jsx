import React, {useState, useEffect} from 'react';
import RoomUsers from './RoomUsers';
const Room = () => {
    // let [users, setUser] = useState([])
    const url = document.location.pathname

    const getCookie = (name) => {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          let c = cookies[i].trim().split('=');
          if (c[0] === name) {
              return c[1];
          }
      }
      return "";
    } 

    useEffect(() => {
      const ws = new WebSocket(
        `ws://192.168.1.45:8000/api/v1${url}?session=${getCookie('session')}`
      );
      ws.onopen = (e) => {
        console.log(e);
      };
      ws.onclose = () => console.log('ws closed');
      ws.onmessage = e => {
        const message = JSON.parse(e.data);
        console.log('e', message);
      };
  
    }, [])

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
          <RoomUsers/>
        </div>
      </div>
    )
};

export default Room;