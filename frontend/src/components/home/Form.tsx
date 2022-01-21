import React from "react";

type Props = {
  handleSubmit: React.FormEventHandler;
};

const Form = ({ handleSubmit }: Props) => {
  return (
    <div className="room_form">
      
      <form onSubmit={handleSubmit} id="form" className="form">
      <h2 className="room_form_title">Creating a room</h2>
        <input
          placeholder="Room name"
          name="roomName"
          className="form_input"
          id="room_name"
        />
        <input
          placeholder="Room password"
          name="roomPassword"
          className="form_input form_input_pswd"
          id="room_password"
        />
        <input type="submit" value="Create your room" className="room_btn"/>
      </form>
    </div>
  );
};

export { Form };
