

export type UserType = {
  name: string;
  status: boolean;
  online?: boolean;
  time?: string;
};

export type Message = {
  Message: string;
  Created_at: string;
  Status: boolean;
  Username: string;
};

export type wsRequest201 = {
  status: number;
  username: string;
  messgae: string;
  time: string;
};


export type wsRequest202 = {
  status: number;
  username: string;
  messgae: string;
  time: string;
};

export type wsRequest203 = {
  status: number;
  connections: Array<UserType>;
};


export type RoomReq = {}

