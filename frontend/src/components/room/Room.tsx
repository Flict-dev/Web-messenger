import React, { useState, useEffect } from "react";
import { getCookie } from "../../utils/helpers";
import { RequestOtions } from "../../utils/reuests";
import { decodeMessages } from "../../utils/crypt";
import {
  UserType,
  Message,
  wsRequest201,
  wsRequest202,
  wsRequest203,
} from "./roomTypes";
import RoomUsers from "./users/RoomUsers";
namespace ReqSettings {
  export const url = document.location.pathname;
  export const session = getCookie("session");
}

const Room: React.FC = () => {
  const [users, setUsers] = useState<Array<UserType>>([]);
  const [messages, setMessages] = useState<Array<Message>>([]);
  const [username, setName] = useState<string>("");

  const startRoom = (usersGet: Array<UserType>): void => {
    type wsResponse = {
      status: keyof typeof wsHandler;
      username?: string;
      message: string;
      connections?: Array<UserType>;
      time: string;
    };

    const wsHandler = {
      200: (r: object) => {
        console.log(r, "plain text");
      },

      201: (r: wsRequest201) => {
        let index = usersGet.findIndex((user) => user.name == r.username);
        if (index >= 0) {
          let c_user = usersGet[index];
          c_user.online = true;
          setUsers([...usersGet]);
        } else {
          const new_user: UserType = {
            name: r.username,
            status: true,
            online: true,
          };
          setUsers([...usersGet, new_user]);
        }
      },

      202: (r: wsRequest202) => {
        let index = usersGet.findIndex((user) => user.name == r.username);
        if (index >= 0) {
          let c_user = usersGet[index];
          c_user.online = false;
          c_user.time = r.time;
          localStorage.setItem(r.username, r.time);
          setUsers([...usersGet]);
        } else {
          console.log("errror");
        }
      },

      203: (r: wsRequest203) => {
        usersGet.forEach((user) => {
          r.connections.forEach((connection) => {
            if (user.name == connection.name) {
              user.online = true;
            }
          });
        });
        setUsers(usersGet);
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
      hadnler(Object(response));
    };
  };

  const initialRequest = async () => {
    const rOptions = RequestOtions.Get({ "Content-Type": "application/json" });
    await fetch(`/v1${ReqSettings.url}`, rOptions).then((response) => {
      response.status === 200
        ? response.json().then((response) => {
            setName(response.User);
            setMessages(decodeMessages(response.Messages));
            startRoom(response.Users);
          })
        : response.status === 401
        ? console.log("401 uant")
        : console.log("Error");
    });
  };

  useEffect(() => {
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
      <RoomUsers users={users} />
    </div>
  );
};

export default Room;
