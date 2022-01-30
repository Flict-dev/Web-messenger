import React, { useState } from "react";
import { UserType } from "../roomTypes";

const OnlineBlock: React.FC<{ user: UserType }> = ({ user }) => {
  if (!user.status) {
    return (
      <div className="status status_blocked">
        <p>
          <span className="status_bl_t">Banned</span>
        </p>
      </div>
    );
  } else if (user.online) {
    return (
      <div className="status status_online">
        <p>
          <span className="status_on_t">Online</span>
        </p>
      </div>
    );
  }
  return (
    <div className="status status_disconnected">
      <p>
        <span className="status_dis_t">
          Was at {user.time ? user.time : localStorage.getItem(user.name)}
        </span>
      </p>
    </div>
  );
};

const User: React.FC<{ user: UserType }> = ({ user }) => {
  return (
    <div className="user_wrapper">
      <div id={user.name} className="user_name_wrapper">
        <p className="user_name">{user.name}:</p> <OnlineBlock user={user} />
      </div>
    </div>
  );
};

export default User;
