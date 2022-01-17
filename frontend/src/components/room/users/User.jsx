import React  from 'react';

const User = ({user}) => {
    let userStatus = `user_status_${user.status}`;      
    return (
        <div className="user_wrapper">
          <div className={userStatus} ></div>
          <div id={user.name} className="user_name" >{user.name}</div>
        </div>
      )
};

export default User;