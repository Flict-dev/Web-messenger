import React from "react";
import { MessageType } from "../roomTypes";

const Message: React.FC<{ data: MessageType }> = ({ data }) => {
  return (
    <div className={`message message_u_${data.current}`}>
      <div className="message_wrapper">
        <div className="message_data">
          <h4 className="message_user">{data.Username}</h4>
          <p className="message_time">{data.Created_at}</p>
        </div>
        <div className="message_content">
          <p className="message_text">{data.Message}</p>
        </div>
      </div>
    </div>
  );
};

export default Message;
