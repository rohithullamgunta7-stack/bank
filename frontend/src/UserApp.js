
// import React, { useState, useEffect } from "react";
// import ChatWindow from "./ChatWindow";
// import API_BASE_URL from "./config"; // ✅ import your backend URL config
// import "./auth-styles.css";

// function UserApp() {
//   const [name, setName] = useState("");
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [token, setToken] = useState("");
//   const [started, setStarted] = useState(false);
//   const [isSignup, setIsSignup] = useState(false);
//   const [isLoading, setIsLoading] = useState(false);
//   const [showPassword, setShowPassword] = useState(false);

//   useEffect(() => {
//     const savedToken = localStorage.getItem("user_token");
//     if (savedToken) {
//       setToken(savedToken);
//       setStarted(true);
//     }
//   }, []);

//   // ✅ Signup
//   const signup = async () => {
//     if (!name || !email || !password) {
//       alert("Name, Email & Password required");
//       return;
//     }

//     setIsLoading(true);

//     try {
//       const res = await fetch(`${API_BASE_URL}/auth/signup`, {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ name, email, password, role: "user" }),
//       });

//       const data = await res.json();

//       if (res.ok) {
//         const receivedToken = data.access_token;
//         setToken(receivedToken);
//         localStorage.setItem("user_token", receivedToken);
//         setStarted(true);
//         setName("");
//         setEmail("");
//         setPassword("");
//       } else {
//         if (Array.isArray(data.detail)) {
//           const errors = data.detail
//             .map((err) => {
//               const field = err.loc ? err.loc[err.loc.length - 1] : "input";
//               return `${field}: ${err.msg || "Invalid input"}`;
//             })
//             .join(", ");
//           alert(errors);
//         } else {
//           alert(data.detail || "Signup failed");
//         }
//       }
//     } catch (err) {
//       console.error("Signup error:", err);
//       alert("Server error. Please try again.");
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   // ✅ Login
//   const login = async () => {
//     if (!email || !password) {
//       alert("Email & Password required");
//       return;
//     }

//     setIsLoading(true);

//     try {
//       const res = await fetch(`${API_BASE_URL}/auth/login`, {
//         method: "POST",
//         headers: { "Content-Type": "application/x-www-form-urlencoded" },
//         body: new URLSearchParams({
//           username: email,
//           password: password,
//         }),
//       });

//       const data = await res.json();

//       if (res.ok) {
//         const receivedToken = data.access_token;
//         if (!receivedToken) {
//           alert("Login succeeded but no token returned.");
//           return;
//         }

//         setToken(receivedToken);
//         localStorage.setItem("user_token", receivedToken);
//         setStarted(true);
//         setEmail("");
//         setPassword("");
//       } else {
//         alert(data.detail || "Login failed");
//       }
//     } catch (err) {
//       console.error("Login error:", err);
//       alert("Server error. Please try again.");
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const logout = () => {
//     localStorage.removeItem("user_token");
//     setToken("");
//     setStarted(false);
//     setEmail("");
//     setPassword("");
//     setName("");
//   };

//   // ✅ Auth Page
//   if (!started) {
//     return (
//       <div className="auth-container">
//         <div className="auth-background"></div>

//         <div className="auth-card">
//           <div className="auth-brand">
//             <div className="auth-logo">
//               <svg width="60" height="60" viewBox="0 0 60 60">
//                 <circle cx="30" cy="30" r="30" fill="url(#grad1)" />
//                 <path d="M30 18L38 34H22L30 18Z" fill="white" />
//                 <circle cx="30" cy="42" r="3.5" fill="white" />
//                 <defs>
//                   <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
//                     <stop
//                       offset="0%"
//                       style={{ stopColor: "#667eea", stopOpacity: 1 }}
//                     />
//                     <stop
//                       offset="100%"
//                       style={{ stopColor: "#764ba2", stopOpacity: 1 }}
//                     />
//                   </linearGradient>
//                 </defs>
//               </svg>
//             </div>
//             <h1 className="auth-title">Customer Support Portal</h1>
//             <p className="auth-subtitle">
//               {isSignup
//                 ? "Create your account to get started"
//                 : "Welcome back! Please login to continue"}
//             </p>
//           </div>

//           <div className="auth-form">
//             {isSignup && (
//               <div className="input-group">
//                 <label className="input-label">Full Name</label>
//                 <div className="input-wrapper">
//                   <span className="input-icon">👤</span>
//                   <input
//                     type="text"
//                     placeholder="Enter your full name"
//                     value={name}
//                     onChange={(e) => setName(e.target.value)}
//                     disabled={isLoading}
//                     className="auth-input"
//                   />
//                 </div>
//               </div>
//             )}

//             <div className="input-group">
//               <label className="input-label">Email Address</label>
//               <div className="input-wrapper">
//                 <span className="input-icon">📧</span>
//                 <input
//                   type="email"
//                   placeholder="you@example.com"
//                   value={email}
//                   onChange={(e) => setEmail(e.target.value)}
//                   disabled={isLoading}
//                   className="auth-input"
//                 />
//               </div>
//             </div>

//             <div className="input-group">
//               <label className="input-label">Password</label>
//               <div className="input-wrapper">
//                 <span className="input-icon">🔒</span>
//                 <input
//                   type={showPassword ? "text" : "password"}
//                   placeholder="Enter your password"
//                   value={password}
//                   onChange={(e) => setPassword(e.target.value)}
//                   disabled={isLoading}
//                   className="auth-input"
//                 />
//                 <button
//                   type="button"
//                   onClick={() => setShowPassword(!showPassword)}
//                   className="password-toggle"
//                 >
//                   {showPassword ? "👁️" : "👁️‍🗨️"}
//                 </button>
//               </div>
//             </div>

//             {isSignup ? (
//               <button
//                 onClick={signup}
//                 disabled={isLoading}
//                 className="auth-submit"
//               >
//                 {isLoading ? <div className="spinner"></div> : "Create Account"}
//               </button>
//             ) : (
//               <button
//                 onClick={login}
//                 disabled={isLoading}
//                 className="auth-submit"
//               >
//                 {isLoading ? <div className="spinner"></div> : "Sign In"}
//               </button>
//             )}
//           </div>

//           <div className="auth-divider">
//             <span className="divider-line"></span>
//             <span className="divider-text">or</span>
//             <span className="divider-line"></span>
//           </div>

//           <div className="auth-toggle">
//             <p className="toggle-text">
//               {isSignup
//                 ? "Already have an account?"
//                 : "Don't have an account?"}{" "}
//               <button
//                 onClick={() => !isLoading && setIsSignup(!isSignup)}
//                 className="toggle-button"
//                 disabled={isLoading}
//               >
//                 {isSignup ? "Sign in" : "Sign up"}
//               </button>
//             </p>
//           </div>

//           <div className="trust-indicators">
//             <div className="trust-item">
//               <span className="trust-icon">🔐</span>
//               <span className="trust-text">Secure</span>
//             </div>
//             <div className="trust-item">
//               <span className="trust-icon">⚡</span>
//               <span className="trust-text">Fast</span>
//             </div>
//             <div className="trust-item">
//               <span className="trust-icon">✓</span>
//               <span className="trust-text">24/7</span>
//             </div>
//           </div>
//         </div>

//         <div className="auth-footer">
//           <p>By continuing, you agree to our Terms & Privacy Policy</p>
//         </div>
//       </div>
//     );
//   }

//   // ✅ After login
//   return (
//     <div>
//       <div
//         style={{
//           padding: "15px 20px",
//           display: "flex",
//           justifyContent: "space-between",
//           alignItems: "center",
//           borderBottom: "2px solid #eee",
//           background: "white",
//         }}
//       >
//         <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
//           <svg width="35" height="35" viewBox="0 0 60 60">
//             <circle cx="30" cy="30" r="30" fill="url(#grad2)" />
//             <path d="M30 18L38 34H22L30 18Z" fill="white" />
//             <circle cx="30" cy="42" r="3.5" fill="white" />
//             <defs>
//               <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
//                 <stop
//                   offset="0%"
//                   style={{ stopColor: "#667eea", stopOpacity: 1 }}
//                 />
//                 <stop
//                   offset="100%"
//                   style={{ stopColor: "#764ba2", stopOpacity: 1 }}
//                 />
//               </linearGradient>
//             </defs>
//           </svg>
//           <span
//             style={{
//               fontWeight: "600",
//               fontSize: "1.1rem",
//               color: "#333",
//             }}
//           >
//             Support Portal
//           </span>
//         </div>
//         <button
//           onClick={logout}
//           style={{
//             padding: "10px 20px",
//             backgroundColor: "#f44336",
//             color: "white",
//             border: "none",
//             borderRadius: "8px",
//             cursor: "pointer",
//             fontWeight: "500",
//             fontSize: "0.9rem",
//             transition: "all 0.2s",
//           }}
//         >
//           Sign Out
//         </button>
//       </div>
//       <ChatWindow token={token} />
//     </div>
//   );
// }

// export default UserApp;

import React, { useState, useEffect } from "react";
import ChatWindow from "./ChatWindow";
import "./auth-styles.css";

// BACKEND URL CONFIGURATION
const isLocal = window.location.hostname === "localhost" || 
                window.location.hostname === "127.0.0.1";

const BACKEND_URL = isLocal 
  ? "http://127.0.0.1:8000"
  : "https://bank-3-zgrw.onrender.com";

console.log("🔧 UserApp Configuration:");
console.log("  📍 Frontend hostname:", window.location.hostname);
console.log("  🏠 Is Local:", isLocal);
console.log("  🌐 Backend URL:", BACKEND_URL);

function UserApp() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [started, setStarted] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    const savedToken = sessionStorage.getItem("user_token");
    if (savedToken) {
      setToken(savedToken);
      setStarted(true);
    }
  }, []);

  const signup = async () => {
    if (!name || !email || !password) {
      alert("Name, Email & Password required");
      return;
    }

    setIsLoading(true);

    try {
      const url = `${BACKEND_URL}/auth/signup`;
      console.log(`🚀 Signup request to: ${url}`);
      
      const res = await fetch(url, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ name, email, password, role: "user" }),
      });

      console.log("📥 Signup Response Status:", res.status);
      console.log("📥 Response Headers:", Object.fromEntries(res.headers.entries()));

      if (!res.ok) {
        const errorText = await res.text();
        console.error("❌ Signup Error Response:", errorText);
        
        let errorMessage;
        try {
          const errorData = JSON.parse(errorText);
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail
              .map((err) => {
                const field = err.loc ? err.loc[err.loc.length - 1] : "input";
                return `${field}: ${err.msg || "Invalid input"}`;
              })
              .join(", ");
          } else {
            errorMessage = errorData.detail || errorData.message || `Signup failed with status ${res.status}`;
          }
        } catch {
          errorMessage = errorText || `Signup failed with status ${res.status}`;
        }
        
        alert(errorMessage);
        setIsLoading(false);
        return;
      }

      const data = await res.json();
      console.log("✅ Signup Success:", data);

      const receivedToken = data.access_token;
      if (!receivedToken) {
        alert("Signup succeeded but no token returned.");
        setIsLoading(false);
        return;
      }

      setToken(receivedToken);
      sessionStorage.setItem("user_token", receivedToken);
      setStarted(true);
      setName("");
      setEmail("");
      setPassword("");
    } catch (err) {
      console.error("💥 Signup Exception:", err);
      alert(`Server error: ${err.message}. Backend might be sleeping or unavailable.`);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async () => {
    if (!email || !password) {
      alert("Email & Password required");
      return;
    }

    setIsLoading(true);

    try {
      const url = `${BACKEND_URL}/auth/login`;
      console.log(`🚀 Login request to: ${url}`);
      
      const res = await fetch(url, {
        method: "POST",
        headers: { 
          "Content-Type": "application/x-www-form-urlencoded",
          "Accept": "application/json"
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      console.log("📥 Login Response Status:", res.status);
      console.log("📥 Response URL:", res.url);
      console.log("📥 Response Headers:", Object.fromEntries(res.headers.entries()));

      if (!res.ok) {
        const errorText = await res.text();
        console.error("❌ Login Error Response:", errorText);
        
        let errorMessage;
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || `Login failed with status ${res.status}`;
        } catch {
          errorMessage = errorText || `Login failed with status ${res.status}`;
        }
        
        alert(errorMessage);
        setIsLoading(false);
        return;
      }

      const data = await res.json();
      console.log("✅ Login Success:", data);

      const receivedToken = data.access_token;
      if (!receivedToken) {
        alert("Login succeeded but no token returned.");
        setIsLoading(false);
        return;
      }

      setToken(receivedToken);
      sessionStorage.setItem("user_token", receivedToken);
      setStarted(true);
      setEmail("");
      setPassword("");
    } catch (err) {
      console.error("💥 Login Exception:", err);
      alert(`Server error: ${err.message}. Backend might be sleeping or unavailable.`);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    sessionStorage.removeItem("user_token");
    setToken("");
    setStarted(false);
    setEmail("");
    setPassword("");
    setName("");
  };

  if (!started) {
    return (
      <div className="auth-container">
        <div className="auth-background"></div>

        <div className="auth-card">
          <div className="auth-brand">
            <div className="auth-logo">
              <svg width="60" height="60" viewBox="0 0 60 60">
                <circle cx="30" cy="30" r="30" fill="url(#grad1)" />
                <path d="M30 18L38 34H22L30 18Z" fill="white" />
                <circle cx="30" cy="42" r="3.5" fill="white" />
                <defs>
                  <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{ stopColor: "#667eea", stopOpacity: 1 }} />
                    <stop offset="100%" style={{ stopColor: "#764ba2", stopOpacity: 1 }} />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <h1 className="auth-title">Customer Support Portal</h1>
            <p className="auth-subtitle">
              {isSignup ? "Create your account to get started" : "Welcome back! Please login to continue"}
            </p>
          </div>

          <div className="auth-form">
            {isSignup && (
              <div className="input-group">
                <label className="input-label">Full Name</label>
                <div className="input-wrapper">
                  <span className="input-icon">👤</span>
                  <input
                    type="text"
                    placeholder="Enter your full name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    disabled={isLoading}
                    className="auth-input"
                  />
                </div>
              </div>
            )}

            <div className="input-group">
              <label className="input-label">Email Address</label>
              <div className="input-wrapper">
                <span className="input-icon">📧</span>
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  className="auth-input"
                />
              </div>
            </div>

            <div className="input-group">
              <label className="input-label">Password</label>
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="auth-input"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !isLoading) {
                      isSignup ? signup() : login();
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="password-toggle"
                >
                  {showPassword ? "👁️" : "👁️‍🗨️"}
                </button>
              </div>
            </div>

            {isSignup ? (
              <button onClick={signup} disabled={isLoading} className="auth-submit">
                {isLoading ? <div className="spinner"></div> : "Create Account"}
              </button>
            ) : (
              <button onClick={login} disabled={isLoading} className="auth-submit">
                {isLoading ? <div className="spinner"></div> : "Sign In"}
              </button>
            )}
          </div>

          <div className="auth-divider">
            <span className="divider-line"></span>
            <span className="divider-text">or</span>
            <span className="divider-line"></span>
          </div>

          <div className="auth-toggle">
            <p className="toggle-text">
              {isSignup ? "Already have an account?" : "Don't have an account?"}{" "}
              <button
                onClick={() => !isLoading && setIsSignup(!isSignup)}
                className="toggle-button"
                disabled={isLoading}
              >
                {isSignup ? "Sign in" : "Sign up"}
              </button>
            </p>
          </div>

          <div className="trust-indicators">
            <div className="trust-item">
              <span className="trust-icon">🔒</span>
              <span className="trust-text">Secure</span>
            </div>
            <div className="trust-item">
              <span className="trust-icon">⚡</span>
              <span className="trust-text">Fast</span>
            </div>
            <div className="trust-item">
              <span className="trust-icon">✓</span>
              <span className="trust-text">24/7</span>
            </div>
          </div>
        </div>

        <div className="auth-footer">
          <p>By continuing, you agree to our Terms & Privacy Policy</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={{
        padding: "15px 20px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        borderBottom: "2px solid #eee",
        background: "white",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <svg width="35" height="35" viewBox="0 0 60 60">
            <circle cx="30" cy="30" r="30" fill="url(#grad2)" />
            <path d="M30 18L38 34H22L30 18Z" fill="white" />
            <circle cx="30" cy="42" r="3.5" fill="white" />
            <defs>
              <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: "#667eea", stopOpacity: 1 }} />
                <stop offset="100%" style={{ stopColor: "#764ba2", stopOpacity: 1 }} />
              </linearGradient>
            </defs>
          </svg>
          <span style={{ fontWeight: "600", fontSize: "1.1rem", color: "#333" }}>
            Support Portal
          </span>
        </div>
        <button onClick={logout} style={{
          padding: "10px 20px",
          backgroundColor: "#f44336",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
          fontWeight: "500",
          fontSize: "0.9rem",
          transition: "all 0.2s",
        }}>
          Sign Out
        </button>
      </div>
      <ChatWindow token={token} backendUrl={BACKEND_URL} />
    </div>
  );
}

export default UserApp;
