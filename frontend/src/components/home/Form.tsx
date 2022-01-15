import React from "react";

type Props = {
  handleSubmit: React.FormEventHandler;
};

const Form = ({ handleSubmit }: Props) => {
  return (
    <div>
      <h2 className="room_form_title">Creating a room</h2>
      <form onSubmit={handleSubmit} id="form">
        <input
          placeholder="Room name"
          name="roomName"
          className="form_input"
          id="room_name"
        />
        <input
          placeholder="Room password"
          name="roomPassword"
          className="form_input"
          id="room_password"
        />
        <input type="submit" value="Create" />
      </form>
    </div>
  );
};

export { Form };
