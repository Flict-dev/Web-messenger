import React from 'react';

const startRoom = (url, session) => {
  const ws = new WebSocket(
    `ws://192.168.1.45:8000/api/v1${url}?session=${session}`
  );
  ws.onopen = (e) => {
    console.log(e);
  };
  ws.onclose = () => console.log('ws closed');
  ws.onmessage = e => {
    const message = JSON.parse(e.data);
    console.log('e', message);
  };
};

export { startRoom }