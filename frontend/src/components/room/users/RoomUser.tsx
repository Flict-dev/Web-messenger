import React from "react";

const RoomUser: React.FC<{ username: string }> = ({ username }) => {
  return (
    <div className="r_user_container">
      <h1 className="username">
        <span className="mr_robot mr_robot_r">{username}</span>
      </h1>
    </div>
  );
};

export default RoomUser;
