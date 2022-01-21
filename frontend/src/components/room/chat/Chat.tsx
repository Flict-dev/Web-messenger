import React from "react";

import { Message } from "../roomTypes";

const Chat: React.FC<{ messages: Array<Message> }> = ({ messages }) => {
  return (
    <div className="chat">
      <div className="messages">{messages}</div>
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
  );
};

export default Chat;
