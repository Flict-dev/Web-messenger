import jwt_decode from "jwt-decode";
import Message from "../components/room/Room";
import { getCookie } from "./helpers";

export type Session = {
  name: string;
  password: string;
  username: string;
  msg_key: string;
};

const decodeMessages: Function = (
  encryptedMessages: Array<typeof Message>
): Array<typeof Message> => {
  let CryptoJS = require("crypto-js");
  const session: Session = jwt_decode(getCookie("session"));
  encryptedMessages.forEach((message) => {
    let bytes = CryptoJS.AES.decrypt(Object(message).Message, session.msg_key);
    Object(message).Message = bytes.toString(CryptoJS.enc.Utf8);
  });
  return encryptedMessages;
};

export { decodeMessages };
