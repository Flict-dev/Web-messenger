namespace RequestOtions {
  export function Get(headers: object): object {
    const getOptions = {
      method: "GET",
      headers: headers,
    };
    return getOptions;
  }
  export function Post(headers: object): object {
    const postOptions = {
      method: "POST",
      headers: headers,
    };
    return postOptions;
  }

  export function Patch(headers: object): object {
    const postOptions = {
      method: "PATCH",
      headers: headers,
    };
    return postOptions;
  }
}

export { RequestOtions };
