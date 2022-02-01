import { sortUsers } from "../../utils/helpers";
import { decodeMessages } from "../../utils/crypt";
import {
  MessageType,
  UserType,
  defaultWsRequest,
  wsRequest203,
} from "./roomTypes";

export type Response = {
  users: Array<UserType>;
  animation: boolean;
  message?: MessageType;
  session?: string;
  username?: string;
};

type Result = {
  typeWs: string;
  response: Response;
};

type WsData = {
  status: number;
  username: string;
  message: string;
};

const response: Response = {
  users: [],
  animation: true,
};

const wsHandler = {
  200: (r: defaultWsRequest): Result => {
    const encMessage: MessageType = {
      Message: r.message,
      Created_at: r.time,
      Username: r.username,
      current: false,
    };
    response.message = decodeMessages(Array(encMessage))[0];
    return { typeWs: "message", response: response };
  },

  201: (r: defaultWsRequest, usersGet: Array<UserType>): Result => {
    let index = usersGet.findIndex((user) => user.name === r.username);
    if (index >= 0) {
      let current_user = usersGet[index];
      current_user.online = true;
      response.users = [...sortUsers(usersGet)];
      return { typeWs: "users", response: response };
    } else {
      usersGet.push({ name: r.username, status: true, online: true });
      response.users = [...sortUsers(usersGet)];
      return { typeWs: "users", response: response };
    }
  },

  202: (r: defaultWsRequest, usersGet: Array<UserType>): Result => {
    let index = usersGet.findIndex((user) => user.name === r.username);
    if (index >= 0) {
      let current_user = usersGet[index];
      current_user.online = false;
      current_user.time = r.time;
      localStorage.setItem(r.username, r.time);
      response.users = [...sortUsers(usersGet)];
      return { typeWs: "users", response: response };
    } else {
      console.log("errror");
      return { typeWs: "users", response: response }; // debug it
    }
  },

  203: (r: wsRequest203, usersGet: Array<UserType>): Result => {
    usersGet.forEach((user) => {
      r.connections.forEach((connection) => {
        if (user.name === connection.name) {
          user.online = true;
        }
      });
    });
    response.users = [...sortUsers(usersGet)];
    response.animation = false;
    return { typeWs: "users", response: response };
  },

  206: (r: defaultWsRequest, usersGet: Array<UserType>): Result => {
    response.session = r.message;
    return { typeWs: "void", response: response };
  },

  207: (r: defaultWsRequest, usersGet: Array<UserType>): Result => {
    response.animation = true;
    return { typeWs: "ban", response: response };
  },

  208: (r: defaultWsRequest, usersGet: Array<UserType>): Result => {
    let index = usersGet.findIndex((user) => user.name === r.username);
    let current_user = usersGet[index];
    current_user.status = false;
    response.users = [...sortUsers(usersGet)];
    return { typeWs: "users", response: response };
  },
};

export const SendMessage = (ws: WebSocket, data: WsData) => {
  try {
    ws.send(JSON.stringify(data));
  } catch (error) {
    console.log(error);
  }
};
export default wsHandler;
