import React, { useState, useEffect } from "react";
import RoomUsers from "./users/RoomUsers";
import { getCookie } from "../../utils/helpers";
import { RequestOtions } from "../../utils/reuests";
import { decodeMessages } from "../../utils/crypt";

type DbUser = {
  name: string;
  status: boolean;
};

interface RoomUser extends DbUser {
  online: boolean;
  time: string;
}

type Message = {
  Message: string;
  Created_at: string;
  Status: boolean;
  Username: string;
};

namespace ReqSettings {
  export const url = document.location.pathname;
  export const session = getCookie("session");
}

const Room: React.FC = () => {
  const [allUsers, setAUsers] = useState<Array<DbUser>>([]);
  // const []
  const [messages, setMessages] = useState<Array<Message>>([]);
  const [username, setName] = useState<string>("");

  const startRoom = (): void => {
    const ws = new WebSocket(
      `ws://192.168.1.45:8000/api/v1${ReqSettings.url}?session=${ReqSettings.session}`
    );
    ws.onopen = (e) => {
      console.log(e);
    };
    ws.onclose = () => console.log("ws closed");
    ws.onmessage = (e) => {
      const message = JSON.parse(e.data);
      console.log("e", message);
    };
  };

  const initialRequest = async () => {
    const rOptions = RequestOtions.Get({ "Content-Type": "application/json" });
    fetch(`/v1${ReqSettings.url}`, rOptions).then((response) => {
      if (response.ok) {
        response.json().then((response) => {
          setName(response.User);
          console.log(response.Users);
          const decodedMessages = decodeMessages(response.Messages);
          setMessages(decodedMessages);
        });
      } else {
        console.error();
      }
    });
  };

  useEffect(() => {
    startRoom();
    initialRequest();
  }, []);
  return (
    <div className="container">
      <div className="admin_container"></div>
      <div className="msg_container">
        <div className="messages"></div>
        <div className="send_wrapper">
          <input
            type="text"
            className="msg_input"
            id="msg_input"
            placeholder="message"
          />
          <input type="submit" className="msg_btn" id="msg_btn" value="send" />
        </div>
      </div>
      <div className="users_container">
        <RoomUsers users={allUsers} />
      </div>
    </div>
  );
};

export default Room;
