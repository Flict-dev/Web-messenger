import React from 'react';

const CreateForm = () => {
  const onError = (errr) => {};
  
  const onSubmit = async (e) => {
    e.preventDefault();
    const form = document.getElementById("form")
    const roomName = form[0].value
    const roomPassword = form[1].value
    const requestOptions = {
      'method': 'POST',
      'headers': {
        'Content-Type': 'application/json'
      },
      'body': JSON.stringify({
        'name': roomName,
        'password': roomPassword
      })
    };
    await fetch('/v1/', requestOptions)
      .then(response => {
          console.log(response);
      })
  };

  return (
    <div className="room_form">
      <h2 className="room_form_title">Creating a room</h2>
      <form onSubmit={onSubmit} id="form">
        <input placeholder="Room name" className="form_input" id="room_name"/>
        <input placeholder="Room password" className="form_input" id="room_password"/>
        <input type="submit" value="Create" />
      </form>
    </div>
  )
};

export default CreateForm