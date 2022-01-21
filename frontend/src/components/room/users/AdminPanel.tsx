import React from "react";
import { UserType } from "../roomTypes";

const AdUser: React.FC<{ user: UserType }> = ({ user }) => {
  let userStatus: string = `user_status_${user.status}`;
  return (
    <div className="user_ad_wrapper">
      <div id={user.name} className="user_ad_name_wrapper">
        <p className="user_name">{user.name}</p>
        <div className="user_ad_options">
          <input className="user_send_key" type="submit" value="Share key" />
          <input className="user_ban" type="submit" value="Ban user" />
        </div>
      </div>
    </div>
  );
};

const AdminPanel: React.FC<{ users: Array<UserType> }> = ({ users }) => {
  return (
    <div className="admin_panel">
      <div className="admin_panel_title">
        <h1 className="admin_title">
          <span className="mr_robot mr_robot_r">Admin</span>
        </h1>
      </div>
      <div className="admin_panel_users">
        {users.map((user, index) => {
          return <AdUser user={user} key={index} />;
        })}
      </div>
      <div className="admin_panel_delete_r">
        <input className="delte_r_btn" type="submit" value="Delete room" />
      </div>
    </div>
  );
};

export default AdminPanel;
