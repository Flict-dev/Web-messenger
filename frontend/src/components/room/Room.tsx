import React, { useState, useEffect } from "react";
import { getCookie, sortUsers } from "../../utils/helpers";
import { RequestOtions } from "../../utils/reuests";
import { decodeMessages } from "../../utils/crypt";
import { UserType, Message } from "./roomTypes";
import RoomUsers from "./users/RoomUsers";
import "../../style/Room.css";
import AdminPanel from "./users/AdminPanel";
import RoomUser from "./users/RoomUser";
import CssLoader from "./Loaders";
import Chat from "./chat/Chat";
import wsHandler from "./wsHandler";
namespace ReqSettings {
  export const url = document.location.pathname;
  export const session = getCookie("session");
}

const Room: React.FC = () => {
  const [users, setUsers] = useState<Array<UserType>>([]);
  const [messages, setMessages] = useState<Array<Message>>([]);
  const [username, setName] = useState<string>("");
  const [showAnim, setAnim] = useState<boolean>(true);

  const startRoom = (usersGet: Array<UserType>): void => {
    type wsResponse = {
      status: keyof typeof wsHandler;
      username?: string;
      message: string;
      connections?: Array<UserType>;
      time: string;
    };

    const ws = new WebSocket(
      `ws://192.168.1.45:8000/api/v1${ReqSettings.url}?session=${ReqSettings.session}`
    );
    ws.onopen = (e) => {};
    ws.onclose = () => console.log("ws closed");
    ws.onmessage = (event: MessageEvent) => {
      const response: wsResponse = JSON.parse(event.data);
      const hadnler = wsHandler[response.status];
      let result = hadnler(Object(response), usersGet);
      setUsers(result.users);
      setAnim(result.animation);
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
    <div className="app_wrapper">
      {showAnim ? (
        <CssLoader />
      ) : (
        <div className="container">
          <div className="user_container">
            {username === "Admin" ? (
              <AdminPanel
                users={users.filter((user) => user.name !== "Admin")}
              />
            ) : (
              <RoomUser username={username} />
            )}
          </div>
          <div className="msg_container">
            <Chat messages={messages} />
          </div>
          <div className="users_container">
            <RoomUsers users={users} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Room;
