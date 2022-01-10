import React  from 'react';

const User = (user) => {
    let currentUser = user.user
    let userStatus = `user_status_${currentUser.status}`;      
    return (
        <div className="user_wrapper">
          <div className={userStatus} ></div>
          <div id={currentUser.name} className="user_name" >{currentUser.name}</div>
        </div>
      )
};

export default User;