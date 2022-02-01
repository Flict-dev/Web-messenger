import React, { useState } from "react";
import {
  RoomFormValues,
  RoomFormElement,
} from "../../utils/interfaces/interfacesForm";
import { RequestOtions } from "../../utils/reuests";
import { Form } from "./Form";
import { FormRes } from "./FormRes";
import { FormError } from "../errors/FormError";
import axios from "axios";

const CreateForm: React.FC = () => {
  const [showForm, setForm] = useState<Boolean>(true);
  const [showRes, setRes] = useState<Boolean>(false);
  const [errorMsg, setErrorMsg] = useState<String>("");
  const [showError, setShow] = useState<Boolean>(false);
  const [path, setPath] = useState<String>("/");

  const handleSubmit = async (event: React.FormEvent<RoomFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formValues: RoomFormValues = {
      name: form.elements.roomName.value,
      password: form.elements.roomPassword.value,
    };
    if (formValues.name && formValues.password) {
      const rOptions = RequestOtions.Post({
        "Content-Type": "application/json",
      });

      await axios
        .post(
          "/v1/",
          { name: formValues.name, password: formValues.password },
          rOptions
        )
        .then((response) => {
          const newSession = response.headers["cookie"] || "";
          document.cookie = `session=${newSession.slice(8)}`;
          setForm(false);
          setPath(response.data.link);
          setRes(true);
        })
        .catch((error) => {
          setErrorMsg(error);
          setShow(true);
          setTimeout((): void => {
            setShow(false);
            setErrorMsg("");
          }, 3000);
        });
    } else {
      setErrorMsg("Room name or password can't be empty");
      setShow(true);
      setTimeout((): void => {
        setShow(false);
        setErrorMsg("");
      }, 3000);
    }
  };

  return (
    <div className="room_form_wrapper">
      {showForm && <Form handleSubmit={handleSubmit} />}
      {showRes && <FormRes link={`${path}`} />}
      <div className="errors_wrapper">
        {showError && <FormError error={`${errorMsg}`} />}
      </div>
    </div>
  );
};

export default CreateForm;
