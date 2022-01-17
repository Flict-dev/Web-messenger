import React, {useState, useEffect} from 'react';
import User from './User';

const RoomUsers = ({users}) => {
  return (
    <div>
      <h2>Room users</h2>
      <div className="users_list">
        {users.map((user, index) => {
          return (
            <User user={user} key={index}/>
          )
        })}
      </div>
    </div>
  )
};

export default RoomUsers;