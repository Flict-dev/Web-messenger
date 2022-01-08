import React, {useState, useEffect} from 'react';


const RoomUsers = () => {
  const path = document.location.pathname

  const getRoomUsers = async () => {
    const requestOptions = {
      'method': 'GET',
      'headers': {
        'Content-Type': 'application/json'
      },
    }; 
    const usersElements = await fetch(`/v1${path}`, requestOptions).then((response) => {
      if (response.ok){
        return response.json()
      }else{
        console.error()
      }
    }).then(data => {
      let usersElements = document.createElement('ul');
      data.Users.map((user) => {
        let li = document.createElement('li');
        li.textContent = user;
        usersElements.insertAdjacentElement("afterbegin", li)
      })
      return usersElements
    })
    let usersList = document.querySelector('.users_list');

    usersList.insertAdjacentElement("afterbegin", usersElements);
  };
  getRoomUsers();
  return (
    <div>
      <h2>Room users</h2>
      <div className="users_list"></div>
    </div>
  )
};

export default RoomUsers;