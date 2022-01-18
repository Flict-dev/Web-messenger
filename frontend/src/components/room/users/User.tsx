import React from "react";
import { UserType } from "../Room";

const OnlineBlock: React.FC<{ user: UserType }> = ({ user }) => {
  if (!user.status) {
    return (
      <div className="status status_blocked">
        <p>Blocked</p>
      </div>
    );
  } else if (user.online) {
    return (
      <div className="status status_online">
        <p>Online</p>
      </div>
    );
  }
  return (
    <div className="status status_disconnected">
      <p>Be at {user.time}</p>
    </div>
  );
};

const User: React.FC<{ user: UserType }> = ({ user }) => {
  let userStatus:string = `user_status_${user.status}`;
  return (
    <div className="user_wrapper">
      <div className={userStatus}></div>
      <div id={user.name} className="user_name">
        {user.name}
      </div>
    </div>
  );
};

export default User;
