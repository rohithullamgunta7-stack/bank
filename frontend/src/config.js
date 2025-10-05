// // src/config.js
// const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://192.168.0.104:8000';
// export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://192.168.0.104:8000';

// export default API_BASE_URL;
// src/config.js
// const API_BASE_URL =
//   process.env.REACT_APP_API_URL || 'https://foodhub-support-system-2.onrender.com';

// export const WS_BASE_URL =
//   process.env.REACT_APP_WS_URL || 'wss://foodhub-support-system-2.onrender.com';

// export default API_BASE_URL;


const isLocal = window.location.hostname === "localhost";

const API_BASE_URL = isLocal
  ? "http://127.0.0.1:8000"
  : process.env.REACT_APP_API_URL || "https://foodhub-support-system-2.onrender.com";

export const WS_BASE_URL = isLocal
  ? "ws://127.0.0.1:8000"
  : process.env.REACT_APP_WS_URL || "wss://foodhub-support-system-2.onrender.com";

export default API_BASE_URL;

