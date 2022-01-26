namespace RequestOtions {
  export function Get(headers: object):object {
    const getOptions = {
      method: 'Get',
      headers: headers,
      credentials: 'same-origin',
    };
    return getOptions;
  }
  export function Post(headers: object):object {
    const postOptions = {
      method: 'POST',
      headers: headers,
      credentials: 'same-origin'
      
    };
    return postOptions;
  }
}

export { RequestOtions };
