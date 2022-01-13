import React from 'react';
import { RoomFormValues, RoomFormElement } from '../../utils/interfaces';
const CreateForm:React.FC = () => {
  // const renderError = (form, error) => {
  //     let errorMsgBox = document.createElement('div');
  //     errorMsgBox.className = 'error_box';
  //     let errorMsg = document.createElement('p');
  //     errorMsg.textContent = error;
  //     errorMsg.className = 'error_text';
  //     errorMsgBox.appendChild(errorMsg);
  //     console.log(errorMsgBox);
  //     form.appendChild(errorMsgBox);
  // };
  // const renderResults = (form, link) => {
  //     let formTitle = document.querySelector('.room_form_title');
  //     formTitle.textContent = 'Your room is ready ';
  //     let resultContainer = document.createElement('div');
  //     resultContainer.className = 'result_container';
  //     let resltBtn = document.createElement('a');
  //     resltBtn.textContent = "Let's hack!"
  //     resltBtn.className = 'reslt_btn';
  //     resltBtn.href = link;
  //     let resltText = document.createElement('p');
  //     resltText.className = 'reslt_text';
  //     resltText.insertAdjacentElement("afterBegin", resltBtn);
  //     resultContainer.appendChild(resltText);
  //     let roomFormWrapper = document.querySelector('.room_form_wrapper');
  //     roomFormWrapper.replaceChild(resultContainer, form);
  // };

  const handleSubmit = async (event: React.FormEvent<RoomFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formValues: RoomFormValues = {
      'name': form.elements.roomName.value,
      'password': form.elements.roomPassword.value,
    }
    console.log(formValues)
    // console.log(event.target.username.value)
    // console.log(this.inputNode.value)
    // const formElements: roomForm = {
    //   'name': form.elements[0],
    //   'password': form.elements[1]
    // }
    // const formElements = {
    //   'name': event.currentTarget.elements.
    // }
    // const requestOptions = {
    //   'method': 'POST',
    //   'headers': {
    //     'Content-Type': 'application/json'
    //   },
    //   'body': JSON.stringify({
    //     'name': roomName,
    //     'password': roomPassword
    //   })
    // };
    // await fetch('/v1/', requestOptions)
    //   .then(response => {
    //       if (response.ok){
    //         document.cookie = response.headers.get('Cookie')
    //         response.json().then(response => {
    //           renderResults(form, response.link)
    //         });
    //       }else{
    //         response.json().then(response => {
    //           renderError(form, response.error) 
    //         })
    //       }
    //   })
  };

  return (
    <div className="room_form_wrapper">
      <h2 className="room_form_title">Creating a room</h2>
      <form onSubmit={handleSubmit} id="form">
        <input placeholder="Room name" name="roomName" className="form_input" id="room_name"/>
        <input placeholder="Room password" name="roomPassword" className="form_input" id="room_password" />
        <input type="submit" value="Create" />
      </form>
    </div>
  ) 
};

export default CreateForm;