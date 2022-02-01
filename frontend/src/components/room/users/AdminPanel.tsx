import React from "react";
import { UserType } from "../roomTypes";

const AdUser: React.FC<{
  user: UserType;
  shareHandler: Function;
  banHandler: Function;
}> = ({ user, shareHandler, banHandler }) => {
  const shareWrapHadnler = (event: React.MouseEvent<HTMLInputElement>) => {
    event.preventDefault();
    shareHandler(user.name);
  };

  const banWrapHadnler = (event: React.MouseEvent<HTMLInputElement>) => {
    event.preventDefault();
    banHandler(user.name);
  };
  return (
    <div className="user_ad_wrapper">
      <div id={user.name} className="user_ad_name_wrapper">
        <p className="user_name">{user.name}</p>
        <div className="user_ad_options">
          <input
            className="user_send_key"
            type="submit"
            value="Share key"
            onClick={shareWrapHadnler}
          />
          <input
            className="user_ban"
            type="submit"
            value="Ban user"
            onClick={banWrapHadnler}
          />
        </div>
      </div>
    </div>
  );
};

const AdminPanel: React.FC<{
  users: Array<UserType>;
  shareHandler: Function;
  banHandler: Function;
  deleteRoomHadnler: React.MouseEventHandler<HTMLInputElement>;
}> = ({ users, shareHandler, banHandler, deleteRoomHadnler }) => {
  return (
    <div className="admin_panel">
      <div className="admin_panel_title">
        <h1 className="admin_title">
          <span className="mr_robot mr_robot_r">Admin</span>
        </h1>
      </div>
      <div className="admin_panel_users">
        {users.map((user, index) => {
          return (
            <AdUser
              user={user}
              key={index}
              shareHandler={shareHandler}
              banHandler={banHandler}
            />
          );
        })}
      </div>
      <div className="admin_panel_delete_r">
        <input
          className="delte_r_btn delete"
          type="submit"
          value="Delete room"
          onClick={deleteRoomHadnler}
        />
      </div>
    </div>
  );
};

export default AdminPanel;
