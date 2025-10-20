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


// const isLocal = window.location.hostname === "localhost";

// const API_BASE_URL = isLocal
//   ? "http://127.0.0.1:8000"
//   : process.env.REACT_APP_API_URL || "https://bank-3-zgrw.onrender.com";

// export const WS_BASE_URL = isLocal
//   ? "ws://127.0.0.1:8000"
//   : process.env.REACT_APP_WS_URL || "https://bank-3-zgrw.onrender.com";

// export default API_BASE_URL;


// Detect if running locally
const isLocal = window.location.hostname === "localhost" || 
                 window.location.hostname === "127.0.0.1";

// API Configuration
const API_BASE_URL = isLocal
  ? "http://127.0.0.1:8000"
  : (process.env.REACT_APP_API_URL || "https://bank-3-zgrw.onrender.com");

// WebSocket Configuration
const WS_BASE_URL = isLocal
  ? "ws://127.0.0.1:8000"
  : (process.env.REACT_APP_WS_URL || "wss://bank-3-zgrw.onrender.com");

// Debug logging - Check what's being used
console.log("🔧 API Configuration:");
console.log("  📍 Hostname:", window.location.hostname);
console.log("  🏠 Is Local:", isLocal);
console.log("  🌐 API_BASE_URL:", API_BASE_URL);
console.log("  🔌 WS_BASE_URL:", WS_BASE_URL);
console.log("  📦 process.env.REACT_APP_API_URL:", process.env.REACT_APP_API_URL);

// Validation check
if (!API_BASE_URL) {
  console.error("❌ CRITICAL: API_BASE_URL is undefined!");
  console.error("   This will cause all API calls to fail!");
}

// Test API connectivity
const testConnection = async () => {
  try {
    console.log(`🔍 Testing connection to: ${API_BASE_URL}/health`);
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    console.log("✅ API Health Check:", data);
  } catch (error) {
    console.error("❌ API Connection Failed:", error.message);
    console.error("   Backend URL:", API_BASE_URL);
    console.error("   Make sure your backend is running!");
  }
};

// Run health check on load (only in development)
if (process.env.NODE_ENV === 'development') {
  setTimeout(testConnection, 1000);
}

// Export as default and named exports
export default API_BASE_URL;
export { WS_BASE_URL, API_BASE_URL as API_URL };
