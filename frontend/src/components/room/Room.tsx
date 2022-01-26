import React, { useState, useEffect, useRef } from "react";
import { getCookie, sortUsers } from "../../utils/helpers";
import { RequestOtions } from "../../utils/reuests";
import { decodeMessages, encodeMessage } from "../../utils/crypt";
import { UserType, MessageType, Session } from "./roomTypes";
import RoomUsers from "./users/RoomUsers";
import "../../style/Room.css";
import AdminPanel from "./users/AdminPanel";
import RoomUser from "./users/RoomUser";
import CssLoader from "./Loaders";
import wsHandler, { SendMessage } from "./wsHandler";
import RoomAuthForm from "./RoomAuth";
import axios from "axios";
import { FormError } from "../errors/FormError";
import {
  RoomFormAuthValues,
  RoomFormAuthElement,
} from "../../utils/interfaces/interfacesForm";
import jwt_decode from "jwt-decode";
import ChatMessages from "./chat/ChatMessages";

namespace ReqSettings {
  export const url = document.location.pathname;
  export const session = getCookie("session");
  export const decodedSession: Session = jwt_decode(session);
}

const Room: React.FC = () => {
  const [users, setUsers] = useState<Array<UserType>>([]);
  const [messages, setMessages] = useState<Array<MessageType>>([]);
  const [username, setName] = useState<string>("");
  const [animMsg, setAnimMsg] = useState<string>("Loading...");
  const [csrf, setCsrf] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [showError, setShowError] = useState<boolean>(false);
  const [showAuth, setShowAuth] = useState<boolean>(false);
  const [erorrWs, setWsError] = useState<boolean>(false);
  const [showAnim, setAnim] = useState<boolean>(true);
  const [wsMsg, setWsMsg] = useState<WebSocket>();
  const inputEl = useRef<HTMLInputElement>(null);

  const wsManager = (usersGet: Array<UserType>): void => {
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
    setWsMsg(ws);
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
        wsManager(response.data.Users);
      })
      .catch((error) => {
        setAnim(false);
        setShowAuth(true);
      });
  };

  const messageHandler: React.MouseEventHandler = async (
    event: React.MouseEvent<HTMLInputElement>
  ) => {
    event.preventDefault();
    if (inputEl.current?.value !== "") {
      // @ts-ignore
      SendMessage(wsMsg, {
        status: 200,
        username: username,
        message: encodeMessage(inputEl.current?.value) || "",
      });
      // @ts-ignore
      inputEl.current.value  = ''
    }
  };
  const authHandler = async (event: React.FormEvent<RoomFormAuthElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formValues: RoomFormAuthValues = {
      username: form.elements.roomUsername.value,
      password: form.elements.roomPassword.value,
    };
    if (formValues.username && formValues.password) {
      const rOptions = RequestOtions.Post({
        "Content-Type": "application/json",
        "X-Token": localStorage.getItem("x-token") || "",
      });

      await axios
        .post(
          `/v1${ReqSettings.url}/auth`,
          { username: formValues.username, password: formValues.password },
          rOptions
        )
        .then((response) => {
          localStorage.setItem("x-token", response.headers["x-token"] || "");
          const newSession = response.headers["cookie"] || "";
          document.cookie = `session=${newSession.slice(8)}`;
          window.location.reload();
        })
        .catch((error) => {
          setErrorMsg(error);
          setShowError(true);
          setTimeout((): void => {
            setShowError(false);
            setErrorMsg("");
          }, 3000);
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
        <div className="auth_form_wrapper">
          <RoomAuthForm handleSubmit={authHandler} />
          <div className="errors_wrapper">
            {showError && <FormError error={`${errorMsg}`} />}
          </div>
        </div>
      ) : (
        <div className="container">
          <div className="user_container">
            {ReqSettings.decodedSession["admin"] ? (
              <AdminPanel
                users={users.filter((user) => user.name !== "Admin")}
              />
            ) : (
              <RoomUser username={username} />
            )}
          </div>
          <div className="msg_container">
            <div className="chat">
              <div className="messages_wrapper">
                <ChatMessages messages={messages} name={username} />
              </div>
              <div className="send_wrapper">
                <input
                  type="text"
                  className="msg_input"
                  id="msg_input"
                  placeholder="message"
                  ref={inputEl}
                />
                <input
                  type="submit"
                  className="msg_btn"
                  id="msg_btn"
                  value="send"
                  name="roomMessage"
                  onClick={messageHandler}
                />
              </div>
            </div>
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
