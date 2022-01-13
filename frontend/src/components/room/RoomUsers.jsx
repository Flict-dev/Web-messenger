import React, {useState, useEffect} from 'react';
import User from './User';

const RoomUsers = ({users}) => {
  return (
    <div>
      <h2>Room users</h2>
      <div className="users_list">
        {Object.keys(users).forEach((key, index) => {
          return (
            <User user={users[key]} key={index}/>
          )
        })}
      </div>
    </div>
  )
};

export default RoomUsers;