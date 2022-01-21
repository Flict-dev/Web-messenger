import React from "react";

const FormRes: React.FC<{ link: string }> = ({ link }) => {
  return (
      <div className="form_res">
        <h2 className="form_res_title">Your room has been created</h2>
        <a href={link} className="room_link">Let's get started</a>
      </div>
  );
};

export { FormRes };
