import React, { useState } from "react";
import { UserType } from "../roomTypes";

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
      <p>Been at {user.time ? user.time : localStorage.getItem(user.name)}</p>
    </div>
  );
};

const User: React.FC<{ user: UserType }> = ({ user }) => {
  let userStatus: string = `user_status_${user.status}`;
  return (
    <div className="user_wrapper">
      <div className={userStatus}></div>
      <div id={user.name} className="user_name_wrapper">
        <p className="user_name">{user.name}</p> <OnlineBlock user={user} />
      </div>
    </div>
  );
};

export default User;
