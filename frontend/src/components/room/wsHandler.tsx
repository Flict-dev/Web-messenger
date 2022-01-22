import { sortUsers } from "../../utils/helpers";

import {
  UserType,
  wsRequest201,
  wsRequest202,
  wsRequest203,
} from "./roomTypes";

type Response = {
  users: Array<UserType>;
  animation: boolean;
};

const response: Response = {
  users: [],
  animation: true,
};

const wsHandler = {
  200: (r: object): Response => {
    console.log(r, "plain text");
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

export default wsHandler;
