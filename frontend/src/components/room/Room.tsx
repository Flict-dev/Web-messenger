import React, { useState, useEffect, useRef } from "react";
import { getCookie } from "../../utils/helpers";
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
import { Response } from "./wsHandler";
namespace ReqSettings {
  export const url = document.location.pathname;
  export const session = getCookie("session");
  export function decode_session(session: string): Session {
    if (session !== "") {
      return jwt_decode(session);
    } else {
      return { admin: false };
    }
  }
}

const Room: React.FC = () => {
  const [users, setUsers] = useState<Array<UserType>>([]);
  const [messages, setMessages] = useState<Array<MessageType>>([]);
  const [username, setName] = useState<string>("");
  const [animMsg, setAnimMsg] = useState<string>("Loading...");
  const [csrf, setCsrf] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [encryption, setEncryption] = useState<boolean>(false);
  const [showError, setShowError] = useState<boolean>(false);
  const [showAuth, setShowAuth] = useState<boolean>(false);
  const [erorrWs, setWsError] = useState<boolean>(false);
  const [showAnim, setAnim] = useState<boolean>(true);
  const [wsMsg, setWsMsg] = useState<WebSocket>();
  const inputEl = useRef<HTMLInputElement>(null);
  const [inValue, setInValue] = useState<string>("");
  const [disabled, setDisabled] = useState<boolean>(false);
  const wsFunctions = {
    users: (data: Response, messagesGet?: Array<MessageType>) => {
      setUsers(data.users);
      setAnim(data.animation);
    },
    message: (data: Response, messagesGet?: Array<MessageType>) => {
      // @ts-ignore
      messagesGet?.push(data.message);
      setMessages([...(messagesGet || [])]);
    },
    void: (data: Response, messagesGet?: Array<MessageType>) => {
      const newSession = data.session;
      if (newSession !== "") {
        // @ts-ignore
        document.cookie = `session=${newSession}`;
      }
      window.location.reload();
    },
    ban: (data: Response, messagesGet?: Array<MessageType>) => {
      setAnim(data.animation);
      document.cookie = "";
      localStorage.clear();
      setWsError(true);
      setAnimMsg("U have been banned!");
    },
  };
  const wsManager = (
    usersGet: Array<UserType>,
    messagesGet?: Array<MessageType>
  ): void => {
    type wsResponse = {
      status: keyof typeof wsHandler;
      username?: string;
      message: string;
      connections?: Array<UserType>;
      time: string;
    };
    const ws = new WebSocket(
      `ws://localhost:8080/api/v1${ReqSettings.url}?session=${ReqSettings.session}`
    );
    ws.onopen = (e) => {};
    ws.onclose = (event: CloseEvent) => {
      setWsError(true);
      setAnimMsg("Connection closed!");
    };
    ws.onmessage = (event: MessageEvent) => {
      const response: wsResponse = JSON.parse(event.data);
      const hadnler = wsHandler[response.status];
      let result = hadnler(Object(response), usersGet);
      // @ts-ignore
      let wsFunc = wsFunctions[result.typeWs];
      wsFunc(result.response, messagesGet);
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
        try {
          const messagesGet = decodeMessages(response.data.Messages);
          setMessages(messagesGet);
          wsManager(response.data.Users, messagesGet);
        } catch (error) {
          wsManager(response.data.Users, []);
        }
      })
      .catch((error) => {
        if (error.response.status === 404) {
          setWsError(true);
          setAnimMsg(`${error.response.data.detail}`);
        } else if (error.response.status === 401) {
          setAnim(false);
          setAnimMsg(error.response.data.detail.Error);
          setShowAuth(true);
        }
      });
  };

  const authHandler = async (event: React.FormEvent<RoomFormAuthElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formValues: RoomFormAuthValues = {
      username: form.elements.roomUsername.value,
      password: form.elements.roomPassword.value,
    };
    if (formValues.username && formValues.password) {
      setAnim(true);
      setAnimMsg("Authorization");
      const rOptions = RequestOtions.Post({
        "Content-Type": "application/json",
        "X-Token": localStorage.getItem("x-token") || "",
        Authorization: ReqSettings.session,
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
          if (error.response.status === 401) {
            setAnim(false);
            setErrorMsg(error.response.data.detail.Error);
            setShowError(true);
            setTimeout((): void => {
              setShowError(false);
              setErrorMsg("");
            }, 3000);
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
  const deleteRoomHadnler = (event: React.MouseEvent<HTMLInputElement>) => {
    event.preventDefault();
    const rOptions = RequestOtions.Delete({
      "Content-Type": "application/json",
      Authorization: ReqSettings.session,
      "X-CSRF-Token": csrf,
    });
    axios
      .delete(`/v1${ReqSettings.url}`, rOptions)
      .then((response) => {
        console.log(response);
        window.location.reload();
      })
      .catch((error) => {
        console.log(error);
      });
  };
  const shareHandler = (userData: string) => {
    // @ts-ignore
    SendMessage(wsMsg, {
      status: 206,
      username: userData,
      message: ReqSettings.decode_session(ReqSettings.session)["msg_key"],
    });
  };

  const banHandler = (userData: string) => {
    console.log(userData);
    // @ts-ignore
    SendMessage(wsMsg, {
      status: 207,
      username: userData,
      message: `${userData} has been banned`,
    });
  };
  const sendInputValue = () => {
    if (inValue !== "" && !disabled) {
      // @ts-ignore
      SendMessage(wsMsg, {
        status: 200,
        username: username,
        message: encodeMessage(inValue) || "",
      });
      // @ts-ignore
      inputEl.current.value = "";
    }
  };

  const messageHandler: React.MouseEventHandler = async (
    event: React.MouseEvent<HTMLInputElement>
  ) => {
    event.preventDefault();
    sendInputValue();
  };
  const keyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      sendInputValue();
      setInValue("");
    }
  };

  const changeHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInValue(event.currentTarget.value);
  };

  useEffect(() => {
    initialRequest();
    if (!ReqSettings.decode_session(ReqSettings.session)["msg_key"]) {
      setEncryption(true);
      setDisabled(true);
    }
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
            {ReqSettings.decode_session(ReqSettings.session)["admin"] ? (
              <AdminPanel
                users={users.filter((user) => user.name !== "Admin")}
                shareHandler={shareHandler}
                banHandler={banHandler}
                deleteRoomHadnler={deleteRoomHadnler}
              />
            ) : (
              <RoomUser username={username} />
            )}
            <div className="errors_wrapper">
              {showError && <FormError error={`${errorMsg}`} />}
            </div>
          </div>
          <div className="msg_container">
            <div className="chat">
              <div className="messages_wrapper">
                {encryption ? (
                  <h3 className="not_key">You don't have an encryption key</h3>
                ) : (
                  <ChatMessages messages={messages} name={username} />
                )}
              </div>
              <div className="send_wrapper">
                <input
                  type="text"
                  className="msg_input"
                  id="msg_input"
                  placeholder="message"
                  onChange={changeHandler}
                  onKeyPress={keyPress}
                  disabled={disabled}
                  ref={inputEl}
                />
                <input
                  type="submit"
                  className="msg_btn"
                  id="msg_btn"
                  value="send"
                  name="roomMessage"
                  onClick={messageHandler}
                  disabled={disabled}
                />
              </div>
            </div>
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
