export type UserType = {
  name: string;
  status: boolean;
  online: boolean;
  time?: string;
};

export type MessageType = {
  Message: string;
  Created_at: string;
  Username: string;
  current?: boolean;
};

export type defaultWsRequest = {
  status: number;
  username: string;
  message: string;
  time: string;
};

export type wsRequest203 = {
  status: number;
  connections: Array<UserType>;
};

export type Session = {
  name?: string;
  user_id?: number;
  room_id?: number;
  admin: boolean;
  msg_key?: string;
  expires?: number;
};
