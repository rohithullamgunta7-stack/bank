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


// // Detect if running locally
// const isLocal = window.location.hostname === "localhost" || 
//                  window.location.hostname === "127.0.0.1";

// // API Configuration
// const API_BASE_URL = isLocal
//   ? "http://127.0.0.1:8000"
//   : (process.env.REACT_APP_API_URL || "https://bank-3-zgrw.onrender.com");

// // WebSocket Configuration
// const WS_BASE_URL = isLocal
//   ? "ws://127.0.0.1:8000"
//   : (process.env.REACT_APP_WS_URL || "wss://bank-3-zgrw.onrender.com");

// // Debug logging - Check what's being used
// console.log("🔧 API Configuration:");
// console.log("  📍 Hostname:", window.location.hostname);
// console.log("  🏠 Is Local:", isLocal);
// console.log("  🌐 API_BASE_URL:", API_BASE_URL);
// console.log("  🔌 WS_BASE_URL:", WS_BASE_URL);
// console.log("  📦 process.env.REACT_APP_API_URL:", process.env.REACT_APP_API_URL);

// // Validation check
// if (!API_BASE_URL) {
//   console.error("❌ CRITICAL: API_BASE_URL is undefined!");
//   console.error("   This will cause all API calls to fail!");
// }

// // Test API connectivity
// const testConnection = async () => {
//   try {
//     console.log(`🔍 Testing connection to: ${API_BASE_URL}/health`);
//     const response = await fetch(`${API_BASE_URL}/health`, {
//       method: 'GET',
//       headers: { 'Content-Type': 'application/json' }
//     });
//     const data = await response.json();
//     console.log("✅ API Health Check:", data);
//   } catch (error) {
//     console.error("❌ API Connection Failed:", error.message);
//     console.error("   Backend URL:", API_BASE_URL);
//     console.error("   Make sure your backend is running!");
//   }
// };

// // Run health check on load (only in development)
// if (process.env.NODE_ENV === 'development') {
//   setTimeout(testConnection, 1000);
// }



// ============================================
// API & WebSocket CONFIGURATION
// ============================================

// Detect if running locally
const isLocal = window.location.hostname === "localhost" || 
                 window.location.hostname === "127.0.0.1";

// Backend URLs - Development
const LOCAL_API = "http://127.0.0.1:8000";
const LOCAL_WS = "ws://127.0.0.1:8000";

// Backend URLs - Production (from environment variables or fallback)
const PRODUCTION_API = process.env.REACT_APP_API_URL || "https://bank-3-zgrw.onrender.com";
const PRODUCTION_WS = process.env.REACT_APP_WS_URL || "wss://bank-3-zgrw.onrender.com";

// Choose based on environment
const API_BASE_URL = isLocal ? LOCAL_API : PRODUCTION_API;
const WS_BASE_URL = isLocal ? LOCAL_WS : PRODUCTION_WS;

// ============================================
// VALIDATION & DEBUG
// ============================================
console.log("🔧 Configuration:");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("📍 Hostname:", window.location.hostname);
console.log("🏠 Environment:", isLocal ? "LOCAL" : "PRODUCTION");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("🌐 API_BASE_URL:", API_BASE_URL);
console.log("🔌 WS_BASE_URL:", WS_BASE_URL);
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
console.log("📦 Environment Variables:");
console.log("   REACT_APP_API_URL:", process.env.REACT_APP_API_URL || "(not set)");
console.log("   REACT_APP_WS_URL:", process.env.REACT_APP_WS_URL || "(not set)");
console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

// ============================================
// VALIDATION CHECKS
// ============================================
const validationErrors = [];

if (!API_BASE_URL) {
  validationErrors.push("API_BASE_URL is undefined");
}

if (API_BASE_URL && API_BASE_URL.includes("vercel.app")) {
  validationErrors.push("API_BASE_URL points to Vercel frontend instead of backend");
}

if (!WS_BASE_URL) {
  validationErrors.push("WS_BASE_URL is undefined");
}

if (WS_BASE_URL && !WS_BASE_URL.startsWith("ws")) {
  validationErrors.push("WS_BASE_URL should start with ws:// or wss://");
}

if (validationErrors.length > 0) {
  console.error("❌ CONFIGURATION ERRORS:");
  validationErrors.forEach((error, index) => {
    console.error(`   ${index + 1}. ${error}`);
  });
  console.error("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.error("Expected values:");
  console.error("   API: https://bank-3-zgrw.onrender.com");
  console.error("   WS:  wss://bank-3-zgrw.onrender.com");
}

// ============================================
// CONNECTION TESTS
// ============================================
const testAPIConnection = async () => {
  try {
    console.log("🔍 Testing API connection...");
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log("✅ API Connected:", {
      status: data.status,
      database: data.database,
      ai_service: data.ai_service
    });
  } catch (error) {
    console.error("❌ API Connection Failed:", error.message);
    console.error("   URL:", `${API_BASE_URL}/health`);
  }
};

const testWSConnection = () => {
  try {
    console.log("🔍 Testing WebSocket connection...");
    
    // Test WebSocket URL format (don't actually connect yet)
    const wsUrl = `${WS_BASE_URL}/ws/test`;
    console.log("   WebSocket URL:", wsUrl);
    
    if (!WS_BASE_URL.startsWith("ws")) {
      throw new Error("Invalid WebSocket URL protocol");
    }
    
    console.log("✅ WebSocket URL is valid");
    console.log("   Note: Actual connection will be made when needed");
    
  } catch (error) {
    console.error("❌ WebSocket Configuration Error:", error.message);
  }
};

// Run tests (with delays to avoid rate limits)
if (isLocal || process.env.NODE_ENV === 'development') {
  setTimeout(testAPIConnection, 1000);
  setTimeout(testWSConnection, 2000);
}

// ============================================
// EXPORTS
// ============================================
export default API_BASE_URL;
export { 
  WS_BASE_URL, 
  API_BASE_URL as API_URL,
  isLocal 
};

// ============================================
// USAGE EXAMPLES:
// ============================================
// 
// API Requests:
//   import API_BASE_URL from "./config";
//   fetch(`${API_BASE_URL}/auth/login`, { ... })
//
// WebSocket Connection:
//   import { WS_BASE_URL } from "./config";
//   const ws = new WebSocket(`${WS_BASE_URL}/ws/chat`);
//
// ============================================

// // Export as default and named exports
// export default API_BASE_URL;
// export { WS_BASE_URL, API_BASE_URL as API_URL };
