import { type } from "os";
import { sortUsers } from "../../utils/helpers";
import { decodeMessages } from "../../utils/crypt";
import {
  MessageType,
  UserType,
  wsRequest200,
  wsRequest201,
  wsRequest202,
  wsRequest203,
} from "./roomTypes";

type Response = {
  users: Array<UserType>;
  animation: boolean;
  message?: MessageType;
};

const response: Response = {
  users: [],
  animation: true,
};

const wsHandler = {
  200: (r: wsRequest200): Response => {
    console.log(r);
    const encMessage: MessageType = {
      Message: r.message,
      Created_at: r.time,
      Username: r.username,
      current: false,
    };
    response.message = decodeMessages(Array(encMessage))[0];
    return response;
  },

  201: (r: wsRequest201, usersGet: Array<UserType>): Response => {
    let index = usersGet.findIndex((user) => user.name === r.username);
    if (index >= 0) {
      let c_user = usersGet[index];
      c_user.online = true;
      response.users = [...sortUsers(usersGet)];
      return response;
    } else {
      usersGet.push({ name: r.username, status: true, online: true });
      response.users = [...sortUsers(usersGet)];
      return response;
    }
  },

  202: (r: wsRequest202, usersGet: Array<UserType>): Response => {
    let index = usersGet.findIndex((user) => user.name === r.username);
    if (index >= 0) {
      let c_user = usersGet[index];
      c_user.online = false;
      c_user.time = r.time;
      localStorage.setItem(r.username, r.time);
      response.users = [...sortUsers(usersGet)];
      return response;
    } else {
      console.log("errror");
      return response; // debug it
    }
  },

  203: (r: wsRequest203, usersGet: Array<UserType>): Response => {
    usersGet.forEach((user) => {
      r.connections.forEach((connection) => {
        if (user.name === connection.name) {
          user.online = true;
        }
      });
    });
    response.users = [...sortUsers(usersGet)];
    response.animation = false;
    return response;
  },
};

type WsData = {
  status: number;
  username: string;
  message: string;
};
export const SendMessage = (ws: WebSocket, data: WsData) => {
  try {
    ws.send(JSON.stringify(data));
  } catch (error) {
    console.log(error);
  }
};
export default wsHandler;
