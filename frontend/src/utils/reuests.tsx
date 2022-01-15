namespace RequestOtions {
  export function Get(headers: object):object {
    const getOptions = {
      'method': 'Get',
      'headers': headers,
    };
    return getOptions;
  }
  export function Post(body: object, headers: object):object {
    const postOptions = {
      'method': 'POST',
      'headers': headers,
      'body': JSON.stringify(body)
    };
    return postOptions;
  }
}

export { RequestOtions };
