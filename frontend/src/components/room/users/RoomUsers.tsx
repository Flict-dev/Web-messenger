import React from 'react';
import { UserType } from '../roomTypes';
import User from './User';

const RoomUsers:React.FC<{users: Array<UserType>}> = ({users}) => {
  return (
    <div className="users_container">
        <h2>Room users</h2>
        <div className="users_list">
          {users.map((user, index) => {
            return <User user={user} key={index} />;
          })}
        </div>
    </div>
  )
};

export default RoomUsers;