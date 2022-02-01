export interface RoomFormValues {
  name: string;
  password: string;
}

interface FormElements extends HTMLFormControlsCollection {
  roomName: HTMLInputElement;
  roomPassword: HTMLInputElement;
}
export interface RoomFormElement extends HTMLFormElement {
  readonly elements: FormElements;
}

export interface RoomFormAuthValues {
  username: string;
  password: string;
}
interface FormAuthElements extends HTMLFormControlsCollection {
  roomUsername: HTMLInputElement;
  roomPassword: HTMLInputElement;
}
export interface RoomFormAuthElement extends HTMLFormElement {
  readonly elements: FormAuthElements;
}

interface FormMsgElements extends HTMLFormControlsCollection {
  roomMessage: HTMLInputElement;
}
export interface RoomFormAuthElement extends HTMLFormElement {
  readonly element: FormMsgElements;
}
