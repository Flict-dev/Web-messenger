import React from "react";

const RoomUser: React.FC<{ username: string }> = ({ username }) => {
  return (
    <div className="r_user_container">
      <h1 className="username"><span className="mr_robot mr_robot_r">{username}</span></h1>
      < input type="submit" value="Leave room" className="delte_r_btn leave_btn"/>
    </div>
  );
};

export default RoomUser;
