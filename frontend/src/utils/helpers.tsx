import { GetRequest, PostRequest } from "./interfaces/InterfacesReq";

const getCookie = (name: string): string => {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    let c = cookies[i].trim().split("=");
    if (c[0] === name) {
      return c[1];
    }
  }
  return "";
};

export { getCookie };

const getRequestOptions = (
  method: string,
  headers?: object,
  body?: JSON
): Object => {
  const reqTypes = {
    'Get': {
      'method': method,
      'headers': headers,
    },
    'Post': {
      'method': method,
      'headers': headers,
      'body': body
    }
  }
  return
};
