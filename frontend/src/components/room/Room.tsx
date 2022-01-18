import React, { useState, useEffect } from "react";
import RoomUsers from "./users/RoomUsers";
import { getCookie } from "../../utils/helpers";
import { RequestOtions } from "../../utils/reuests";
import { decodeMessages } from "../../utils/crypt";

export type UserType = {
  name: string;
  status: boolean;
  online?: boolean;
  time: string;
};

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


// namespace WsFunctions {
//   export function setOnline()
// }

const Room: React.FC = () => {
  const [users, setUsers] = useState<Array<UserType>>([]);
  const [messages, setMessages] = useState<Array<Message>>([]);
  const [username, setName] = useState<string>("");

  const startRoom = (): void => {
    type wsResponse = {
      status: keyof typeof wsHandler;
      username?: string;
      message?: string;
      connections?: Array<UserType>;
      time: string;
    };

    const wsHandler = {
      200: () => {
        console.log(200, "lox");
      },
      201: () => {
        console.log(201);
      },
      202: () => {
        console.log(202);
      },
      203: () => {
        console.log(203);
      },
    };

    const ws = new WebSocket(
      `ws://192.168.1.45:8000/api/v1${ReqSettings.url}?session=${ReqSettings.session}`
    );
    ws.onopen = (e) => {};
    ws.onclose = () => console.log("ws closed");
    ws.onmessage = (event: MessageEvent) => {
      const response: wsResponse = JSON.parse(event.data);
      const hadnler = wsHandler[response.status];
      hadnler();
    };
  };

  const initialRequest = async () => {
    const rOptions = RequestOtions.Get({ "Content-Type": "application/json" });
    fetch(`/v1${ReqSettings.url}`, rOptions).then((response) => {
      if (response.ok) {
        response.json().then((response) => {
          setName(response.User);
          setUsers(response.Users);
          setMessages(decodeMessages(response.Messages));
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
        <RoomUsers users={users} />
      </div>
    </div>
  );
};

export default Room;
