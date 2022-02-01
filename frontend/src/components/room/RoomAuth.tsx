import React from "react";


const RoomAuthForm: React.FC<{ handleSubmit: React.FormEventHandler }> = ({ handleSubmit }) => {
  return (
    <div className="room_form">
      <form onSubmit={handleSubmit} id="form" className="form">
        <h2 className="room_form_title">Sign in</h2>
        <input
          placeholder="You'r name in room"
          name="roomUsername"
          className="form_input"
          id="room_name"
        />
        <input
          placeholder="Room password"
          name="roomPassword"
          className="form_input form_input_pswd"
          id="room_password"
        />
        <input type="submit" value="Sign in" className="room_btn" />
      </form>
      
    </div>
  );
};

export default RoomAuthForm;
