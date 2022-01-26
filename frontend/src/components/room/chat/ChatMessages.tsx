import React from "react";
import { MessageType } from "../roomTypes";
import Message from "./Message";

const ChatMessages: React.FC<{
  messages: Array<MessageType>;
  name: string;
}> = ({ messages, name }) => {
  console.log(messages)
  return (
    <div className="messages">
      {messages.map((message, index) => {
        message.Username == name
          ? (message.current = true)
          : (message.current = false);
        return <Message data={message} key={index}/>;
      })}
    </div>
  );
};

export default ChatMessages;
