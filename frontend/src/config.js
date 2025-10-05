// src/config.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://192.168.0.104:8000';
export const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://192.168.0.104:8000';

export default API_BASE_URL;