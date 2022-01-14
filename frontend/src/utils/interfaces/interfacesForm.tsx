export interface RoomFormValues {
  name: string
  password: string
}

export interface HomeGetRequest {
  method: string
  headers?: object
}



export interface HomePostRequest {
  method: string
  headers?: object
  body: JSON
}

interface FormElements extends HTMLFormControlsCollection {
  roomName: HTMLInputElement
  roomPassword: HTMLInputElement
}
export interface RoomFormElement extends HTMLFormElement {
  readonly elements: FormElements
}
