import React, { useState, useEffect } from "react";
import Cookies from "js-cookie";
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
import RoomAuthForm from "./RoomAuth";
import axios from "axios";

import {
  RoomFormAuthValues,
  RoomFormAuthElement,
} from "../../utils/interfaces/interfacesForm";
import { FormError } from "../errors/FormError";
axios.defaults.withCredentials = true;
namespace ReqSettings {
  export const url = document.location.pathname;
  export const session = getCookie("session");
}

const Room: React.FC = () => {
  const [users, setUsers] = useState<Array<UserType>>([]);
  const [messages, setMessages] = useState<Array<Message>>([]);
  const [username, setName] = useState<string>("");
  const [animMsg, setAnimMsg] = useState<string>("Loading...");
  const [csrf, setCsrf] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [showError, setShowError] = useState<boolean>(false);
  const [showAuth, setShowAuth] = useState<boolean>(false);
  const [erorrWs, setWsError] = useState<boolean>(false);
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
    ws.onclose = (event: CloseEvent) => {
      setWsError(true);
      setAnimMsg("Connection closed, session already exists");
    };
    ws.onmessage = (event: MessageEvent) => {
      const response: wsResponse = JSON.parse(event.data);
      const hadnler = wsHandler[response.status];
      let result = hadnler(Object(response), usersGet);
      setUsers(result.users);
      setAnim(result.animation);
    };
  };

  const initialRequest = async () => {
    const rOptions = RequestOtions.Get({
      "Content-Type": "application/json",
      Authorization: ReqSettings.session,
    });

    await axios(`/v1${ReqSettings.url}`, rOptions)
      .then((response) => {
        setCsrf(response.headers["x-csrf-token"] || "");
        localStorage.setItem("x-token", response.headers["x-token"] || "");
        setName(response.data.User);
        setMessages(decodeMessages(response.data.Messages));
        startRoom(response.data.Users);
      })
      .catch((error) => {
        console.log(error)
        setAnim(false);
        setShowAuth(true);
      });

    // await fetch(`/v1${ReqSettings.url}`, rOptions).then((response) => {
    //   if (response.status === 200) {
    //     setCsrf(response.headers.get("X-CSRF-Token") || "");
    //     localStorage.setItem("x-token", response.headers.get("X-Token") || "");
    //     response.json().then((response) => {
    //       setName(response.User);
    //       setMessages(response.Messages);
    //       setMessages(decodeMessages(response.Messages));
    //       startRoom(response.Users);
    //     });
    //   } else if (response.status === 401) {
    //     setAnim(false);
    //     setShowAuth(true);
    //   }
    // });
  };

  const authHandler = async (event: React.FormEvent<RoomFormAuthElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formValues: RoomFormAuthValues = {
      username: form.elements.roomUsername.value,
      password: form.elements.roomPassword.value,
    };
    if (formValues.username && formValues.password) {
      const rOptions = RequestOtions.Post(
        { username: formValues.username, password: formValues.password },
        {
          "Content-Type": "application/json",
          "X-Token": localStorage.getItem("x-token") || "",
        }
      );
      await fetch(`/v1${ReqSettings.url}/auth`, rOptions).then((response) => {
        if (response.status === 200) {
          localStorage.setItem(
            "x-token",
            response.headers.get("X-Token") || ""
          );
          const newSession = response.headers.get("Cookie") || "";
          document.cookie = `session=${newSession.slice(8)}`;
          setShowAuth(false);
          window.location.reload();
        } else if (response.status === 401) {
          response.json().then((response) => {
            console.log(response);
          });
        }
      });
    } else {
      setErrorMsg("You'r name or password can't be empty");
      setShowError(true);
      setTimeout((): void => {
        setShowError(false);
        setErrorMsg("");
      }, 3000);
    }
  };

  useEffect(() => {
    initialRequest();
  }, []);

  return (
    <div className="app_wrapper">
      {showAnim ? (
        <CssLoader message={animMsg} showE={erorrWs} />
      ) : showAuth ? (
        <RoomAuthForm handleSubmit={authHandler} />
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
      <input type="hidden" value={csrf} />
    </div>
  );
};

export default Room;
