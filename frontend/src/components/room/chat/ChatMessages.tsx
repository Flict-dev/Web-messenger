import React, { useRef, useEffect } from "react";
import { MessageType } from "../roomTypes";
import Message from "./Message";

const ChatMessages: React.FC<{
  messages: Array<MessageType>;
  name: string;
}> = ({ messages, name }) => {
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "auto" });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="messages">
      {messages.map((message, index) => {
        message.Username == name
          ? (message.current = true)
          : (message.current = false);
        return <Message data={message} key={index} />;
      })}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatMessages;
