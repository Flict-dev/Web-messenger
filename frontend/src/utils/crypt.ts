import jwt_decode from "jwt-decode";
import { MessageType } from "../components/room/roomTypes";
import { getCookie } from "./helpers";

export type Session = {
  name: string;
  password: string;
  username: string;
  msg_key: string;
};


const decodeMessages: Function = (
  encryptedMessages: Array<MessageType>
): Array<MessageType> => {
  let CryptoJS = require("crypto-js");
  const session: Session = jwt_decode(getCookie("session"));
  encryptedMessages.forEach((message) => {
    let bytes = CryptoJS.AES.decrypt(Object(message).Message, session.msg_key);
    Object(message).Message = bytes.toString(CryptoJS.enc.Utf8);
  });
  return encryptedMessages;
};

const encodeMessage: Function = (message: string): string => {
  let CryptoJS = require("crypto-js");
  const session: Session = jwt_decode(getCookie("session"));
  let encrypted = CryptoJS.AES.encrypt(message, session.msg_key);
  return encrypted.toString();
};


export { decodeMessages, encodeMessage};
