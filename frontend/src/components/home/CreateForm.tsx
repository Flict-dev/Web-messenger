import React, { useState } from "react";
import {
  RoomFormValues,
  RoomFormElement,
} from "../../utils/interfaces/interfacesForm";
import { RequestOtions } from "../../utils/reuests";
import { Form } from "./Form";
import { FormRes } from "./FormRes";
import { FormError } from "./FormError";

type Error = {
  show: boolean;
  error: string;
};

const CreateForm: React.FC = () => {
  const [showForm, setForm] = useState<Boolean>(true);
  const [showRes, setRes] = useState<Boolean>(false);
  const [error, setError] = useState<Error>({ show: false, error: "" });
  const [path, setPath] = useState<String>("/");

  const handleSubmit = async (event: React.FormEvent<RoomFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formValues: RoomFormValues = {
      name: form.elements.roomName.value,
      password: form.elements.roomPassword.value,
    };
    const rOptions = RequestOtions.Post(
      { name: formValues.name, password: formValues.password },
      { "Content-Type": "application/json" }
    );

    await fetch("/v1/", rOptions).then((response) => {
      if (response.ok) {
        document.cookie = response.headers.get("Cookie") || "";
        response.json().then((response) => {
          setForm(false);
          setPath(response.link);
          setRes(true);
        });
      } else {
        response.json().then((response) => {
          setError({ show: true, error: response.error })
        });
      }
    });
  };

  return (
    <div className="room_form_wrapper">
      {showForm && <Form handleSubmit={handleSubmit} />}
      {showRes && <FormRes link={`${path}`} />}
      <div className="errors_wrapper">
        {error.show && (
          <FormError data={{ show: error.show, error: error.error }} />
        )}
      </div>
    </div>
  );
};

export default CreateForm;
