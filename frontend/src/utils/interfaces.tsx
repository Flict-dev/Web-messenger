export interface RoomFormValues {
  name: string
  password: string
}

interface FormElements extends HTMLFormControlsCollection {
  roomName: HTMLInputElement
  roomPassword: HTMLInputElement
}
export interface RoomFormElement extends HTMLFormElement {
  readonly elements: FormElements
}