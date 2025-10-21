
// import React, { useState } from "react";
// import API_BASE_URL from "./config";

// function AdminLogin({ onLoginSuccess }) {
//   const [isSignup, setIsSignup] = useState(false);
//   const [formData, setFormData] = useState({
//     name: "",
//     email: "",
//     password: "",
//     role: "customer_support_agent",
//     admin_secret: ""
//   });
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState("");

//   const handleInputChange = (e) => {
//     setFormData({
//       ...formData,
//       [e.target.name]: e.target.value
//     });
//     setError(""); // Clear error when user types
//   };

//   const handleLogin = async (e) => {
//     e.preventDefault();
    
//     if (!formData.email || !formData.password) {
//       setError("Email and password are required");
//       return;
//     }

//     setIsLoading(true);
//     setError("");

//     try {
//       // 1. Login endpoint
//       const response = await fetch(`${API_BASE_URL}/auth/login`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/x-www-form-urlencoded",
//         },
//         body: new URLSearchParams({
//           username: formData.email,
//           password: formData.password,
//         }),
//       });

//       const data = await response.json();

//       if (response.ok) {
//         // 2. Fetch user info to verify role
//         const userInfoResponse = await fetch(`${API_BASE_URL}/auth/me`, {
//           headers: {
//             Authorization: `Bearer ${data.access_token}`,
//           },
//         });

//         if (userInfoResponse.ok) {
//           const userInfo = await userInfoResponse.json();
          
//           // Check if user has admin or support role
//           if (userInfo.role === "admin" || userInfo.role === "customer_support_agent") {
//             onLoginSuccess(data.access_token, userInfo);
//           } else {
//             setError("Access denied. Admin or Support role required.");
//           }
//         } else {
//           setError("Failed to verify user information");
//         }
//       } else {
//         setError(data.detail || "Login failed");
//       }
//     } catch (err) {
//       setError("Connection error. Please try again.");
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleSignup = async (e) => {
//     e.preventDefault();
    
//     if (!formData.name || !formData.email || !formData.password || !formData.admin_secret) {
//       setError("All fields are required");
//       return;
//     }

//     if (formData.password.length < 8) {
//       setError("Password must be at least 8 characters long");
//       return;
//     }

//     setIsLoading(true);
//     setError("");

//     try {
//       // 3. Admin Signup endpoint
//       const response = await fetch(`${API_BASE_URL}/auth/admin-signup`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           name: formData.name,
//           email: formData.email,
//           password: formData.password,
//           role: formData.role,
//           admin_secret: formData.admin_secret
//         }),
//       });

//       const data = await response.json();

//       if (response.ok) {
//         // 4. Fetch user info
//         const userInfoResponse = await fetch(`${API_BASE_URL}/auth/me`, {
//           headers: {
//             Authorization: `Bearer ${data.access_token}`,
//           },
//         });

//         if (userInfoResponse.ok) {
//           const userInfo = await userInfoResponse.json();
//           onLoginSuccess(data.access_token, userInfo);
//         } else {
//           setError("Account created but failed to fetch user info");
//         }
//       } else {
//         if (Array.isArray(data.detail)) {
//           const errors = data.detail.map(err => {
//             const field = err.loc ? err.loc[err.loc.length - 1] : "input";
//             return `${field}: ${err.msg || "Invalid input"}`;
//           }).join(", ");
//           setError(errors);
//         } else {
//           setError(data.detail || "Signup failed");
//         }
//       }
//     } catch (err) {
//       setError("Connection error. Please try again.");
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="login-container">
//       <div className="login-card">
//         <h2>{isSignup ? "Admin/Support Signup" : "Admin/Support Login"}</h2>
        
//         <form onSubmit={isSignup ? handleSignup : handleLogin}>
//           {isSignup && (
//             <>
//               <div className="form-group">
//                 <label htmlFor="name">Full Name</label>
//                 <input
//                   type="text"
//                   id="name"
//                   name="name"
//                   value={formData.name}
//                   onChange={handleInputChange}
//                   placeholder="Enter your full name"
//                   disabled={isLoading}
//                   required
//                 />
//               </div>

//               <div className="form-group">
//                 <label htmlFor="role">Role</label>
//                 <select
//                   id="role"
//                   name="role"
//                   value={formData.role}
//                   onChange={handleInputChange}
//                   disabled={isLoading}
//                   required
//                 >
//                   <option value="customer_support_agent">Customer Support Agent</option>
//                   <option value="admin">Admin</option>
//                 </select>
//               </div>
//             </>
//           )}

//           <div className="form-group">
//             <label htmlFor="email">Email</label>
//             <input
//               type="email"
//               id="email"
//               name="email"
//               value={formData.email}
//               onChange={handleInputChange}
//               placeholder="Enter your email"
//               disabled={isLoading}
//               required
//             />
//           </div>

//           <div className="form-group">
//             <label htmlFor="password">Password</label>
//             <input
//               type="password"
//               id="password"
//               name="password"
//               value={formData.password}
//               onChange={handleInputChange}
//               placeholder="Enter your password"
//               disabled={isLoading}
//               required
//             />
//           </div>

//           {isSignup && (
//             <div className="form-group">
//               <label htmlFor="admin_secret">Admin Secret Key</label>
//               <input
//                 type="password"
//                 id="admin_secret"
//                 name="admin_secret"
//                 value={formData.admin_secret}
//                 onChange={handleInputChange}
//                 placeholder="Enter admin secret key"
//                 disabled={isLoading}
//                 required
//               />
//               <small className="form-help">
//                 Contact your administrator for the secret key
//               </small>
//             </div>
//           )}

//           {error && <div className="error-message">{error}</div>}

//           <button 
//             type="submit" 
//             className="submit-btn"
//             disabled={isLoading}
//           >
//             {isLoading ? "Processing..." : (isSignup ? "Create Account" : "Login")}
//           </button>
//         </form>

//         <div className="form-toggle">
//           {isSignup ? (
//             <p>
//               Already have an account?{" "}
//               <button
//                 type="button"
//                 className="link-btn"
//                 onClick={() => {
//                   setIsSignup(false);
//                   setError("");
//                   setFormData({
//                     name: "",
//                     email: "",
//                     password: "",
//                     role: "customer_support_agent",
//                     admin_secret: ""
//                   });
//                 }}
//                 disabled={isLoading}
//               >
//                 Login here
//               </button>
//             </p>
//           ) : (
//             <p>
//               Need to create an account?{" "}
//               <button
//                 type="button"
//                 className="link-btn"
//                 onClick={() => {
//                   setIsSignup(true);
//                   setError("");
//                   setFormData({
//                     name: "",
//                     email: "",
//                     password: "",
//                     role: "customer_support_agent",
//                     admin_secret: ""
//                   });
//                 }}
//                 disabled={isLoading}
//               >
//                 Sign up here
//               </button>
//             </p>
//           )}
//         </div>

//         <div className="info-note">
//           <p><strong>Note:</strong> This portal is for administrators and customer support agents only.</p>
//           <p>Regular users should use the main customer portal.</p>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default AdminLogin;




// // import React, { useState } from "react";
// // import API_BASE_URL from "./config";

// // function AdminLogin({ onLoginSuccess }) {
// //   const [isSignup, setIsSignup] = useState(false);
// //   const [formData, setFormData] = useState({
// //     name: "",
// //     email: "",
// //     password: "",
// //     role: "customer_support_agent",
// //     admin_secret: ""
// //   });
// //   const [isLoading, setIsLoading] = useState(false);
// //   const [error, setError] = useState("");

// //   const handleInputChange = (e) => {
// //     setFormData({
// //       ...formData,
// //       [e.target.name]: e.target.value
// //     });
// //     setError("");
// //   };

// //   const handleLogin = async (e) => {
// //     e.preventDefault();
    
// //     if (!formData.email || !formData.password) {
// //       setError("Email and password are required");
// //       return;
// //     }

// //     setIsLoading(true);
// //     setError("");

// //     try {
// //       console.log("🔐 LOGIN ATTEMPT");
// //       console.log("📧 Email:", formData.email);
// //       console.log("🌐 API URL:", API_BASE_URL);
      
// //       // 1. Login endpoint
// //       const loginUrl = `${API_BASE_URL}/auth/login`;
// //       console.log("📤 Sending login request to:", loginUrl);
      
// //       const response = await fetch(loginUrl, {
// //         method: "POST",
// //         headers: {
// //           "Content-Type": "application/x-www-form-urlencoded",
// //         },
// //         body: new URLSearchParams({
// //           username: formData.email,
// //           password: formData.password,
// //         }),
// //       });

// //       console.log("📥 Login response status:", response.status);
// //       const data = await response.json();
// //       console.log("📥 Login response data:", data);

// //       if (response.ok) {
// //         console.log("✅ Login successful!");
// //         console.log("🎫 Token received:", data.access_token ? "YES" : "NO");
        
// //         // 2. Fetch user info to verify role
// //         const userInfoUrl = `${API_BASE_URL}/auth/me`;
// //         console.log("📤 Fetching user info from:", userInfoUrl);
        
// //         const userInfoResponse = await fetch(userInfoUrl, {
// //           method: "GET",
// //           headers: {
// //             "Authorization": `Bearer ${data.access_token}`,
// //             "Content-Type": "application/json"
// //           },
// //         });

// //         console.log("📥 User info response status:", userInfoResponse.status);

// //         if (userInfoResponse.ok) {
// //           const userInfo = await userInfoResponse.json();
// //           console.log("📥 User info received:", userInfo);
// //           console.log("👤 User role:", userInfo.role);
          
// //           // Check if user has admin or support role
// //           if (userInfo.role === "admin" || userInfo.role === "customer_support_agent") {
// //             console.log("✅ ROLE VERIFIED - Logging in as:", userInfo.role);
// //             onLoginSuccess(data.access_token, userInfo);
// //           } else {
// //             console.warn("⚠️ INVALID ROLE:", userInfo.role);
// //             console.warn("Expected: admin or customer_support_agent");
// //             setError(`Access denied. You have role "${userInfo.role}" but admin or support role is required.`);
// //           }
// //         } else {
// //           const errorData = await userInfoResponse.json().catch(() => ({}));
// //           console.error("❌ User info fetch failed");
// //           console.error("Status:", userInfoResponse.status);
// //           console.error("Error:", errorData);
// //           setError(errorData.detail || "Failed to verify user information");
// //         }
// //       } else {
// //         console.error("❌ Login failed");
// //         console.error("Status:", response.status);
// //         console.error("Error:", data);
// //         setError(data.detail || "Login failed");
// //       }
// //     } catch (err) {
// //       console.error("❌ CRITICAL ERROR:", err);
// //       console.error("Error name:", err.name);
// //       console.error("Error message:", err.message);
// //       console.error("Error stack:", err.stack);
// //       setError(`Connection error: ${err.message}. Please check if the backend is running at ${API_BASE_URL}`);
// //     } finally {
// //       setIsLoading(false);
// //     }
// //   };

// //   const handleSignup = async (e) => {
// //     e.preventDefault();
    
// //     if (!formData.name || !formData.email || !formData.password || !formData.admin_secret) {
// //       setError("All fields are required");
// //       return;
// //     }

// //     if (formData.password.length < 8) {
// //       setError("Password must be at least 8 characters long");
// //       return;
// //     }

// //     setIsLoading(true);
// //     setError("");

// //     try {
// //       console.log("📝 SIGNUP ATTEMPT");
// //       console.log("👤 Name:", formData.name);
// //       console.log("📧 Email:", formData.email);
// //       console.log("🎭 Role:", formData.role);
// //       console.log("🌐 API URL:", API_BASE_URL);
      
// //       const signupUrl = `${API_BASE_URL}/auth/admin-signup`;
// //       console.log("📤 Sending signup request to:", signupUrl);
      
// //       const response = await fetch(signupUrl, {
// //         method: "POST",
// //         headers: {
// //           "Content-Type": "application/json",
// //         },
// //         body: JSON.stringify({
// //           name: formData.name,
// //           email: formData.email,
// //           password: formData.password,
// //           role: formData.role,
// //           admin_secret: formData.admin_secret
// //         }),
// //       });

// //       console.log("📥 Signup response status:", response.status);
// //       const data = await response.json();
// //       console.log("📥 Signup response data:", data);

// //       if (response.ok) {
// //         console.log("✅ Signup successful!");
// //         console.log("🎫 Token received:", data.access_token ? "YES" : "NO");
        
// //         // Fetch user info
// //         const userInfoUrl = `${API_BASE_URL}/auth/me`;
// //         console.log("📤 Fetching user info from:", userInfoUrl);
        
// //         const userInfoResponse = await fetch(userInfoUrl, {
// //           method: "GET",
// //           headers: {
// //             "Authorization": `Bearer ${data.access_token}`,
// //             "Content-Type": "application/json"
// //           },
// //         });

// //         console.log("📥 User info response status:", userInfoResponse.status);

// //         if (userInfoResponse.ok) {
// //           const userInfo = await userInfoResponse.json();
// //           console.log("📥 User info received:", userInfo);
// //           console.log("✅ ACCOUNT CREATED - Role:", userInfo.role);
// //           onLoginSuccess(data.access_token, userInfo);
// //         } else {
// //           const errorData = await userInfoResponse.json().catch(() => ({}));
// //           console.error("❌ User info fetch failed after signup");
// //           console.error("Status:", userInfoResponse.status);
// //           console.error("Error:", errorData);
// //           setError("Account created but failed to fetch user info. Please try logging in.");
// //         }
// //       } else {
// //         console.error("❌ Signup failed");
// //         console.error("Status:", response.status);
// //         console.error("Error:", data);
        
// //         if (Array.isArray(data.detail)) {
// //           const errors = data.detail.map(err => {
// //             const field = err.loc ? err.loc[err.loc.length - 1] : "input";
// //             return `${field}: ${err.msg || "Invalid input"}`;
// //           }).join(", ");
// //           setError(errors);
// //         } else {
// //           setError(data.detail || "Signup failed");
// //         }
// //       }
// //     } catch (err) {
// //       console.error("❌ CRITICAL ERROR:", err);
// //       console.error("Error name:", err.name);
// //       console.error("Error message:", err.message);
// //       console.error("Error stack:", err.stack);
// //       setError(`Connection error: ${err.message}. Please check if the backend is running at ${API_BASE_URL}`);
// //     } finally {
// //       setIsLoading(false);
// //     }
// //   };

// //   return (
// //     <div className="login-container">
// //       <div className="login-card">
// //         <h2>{isSignup ? "Admin/Support Signup" : "Admin/Support Login"}</h2>
        
// //         {/* Debug Info (remove in production) */}
// //         <div style={{ 
// //           fontSize: '10px', 
// //           padding: '5px', 
// //           background: '#f0f0f0', 
// //           marginBottom: '10px',
// //           borderRadius: '4px'
// //         }}>
// //           <strong>API:</strong> {API_BASE_URL}
// //         </div>
        
// //         <form onSubmit={isSignup ? handleSignup : handleLogin}>
// //           {isSignup && (
// //             <>
// //               <div className="form-group">
// //                 <label htmlFor="name">Full Name</label>
// //                 <input
// //                   type="text"
// //                   id="name"
// //                   name="name"
// //                   value={formData.name}
// //                   onChange={handleInputChange}
// //                   placeholder="Enter your full name"
// //                   disabled={isLoading}
// //                   required
// //                 />
// //               </div>

// //               <div className="form-group">
// //                 <label htmlFor="role">Role</label>
// //                 <select
// //                   id="role"
// //                   name="role"
// //                   value={formData.role}
// //                   onChange={handleInputChange}
// //                   disabled={isLoading}
// //                   required
// //                 >
// //                   <option value="customer_support_agent">Customer Support Agent</option>
// //                   <option value="admin">Admin</option>
// //                 </select>
// //               </div>
// //             </>
// //           )}

// //           <div className="form-group">
// //             <label htmlFor="email">Email</label>
// //             <input
// //               type="email"
// //               id="email"
// //               name="email"
// //               value={formData.email}
// //               onChange={handleInputChange}
// //               placeholder="Enter your email"
// //               disabled={isLoading}
// //               required
// //             />
// //           </div>

// //           <div className="form-group">
// //             <label htmlFor="password">Password</label>
// //             <input
// //               type="password"
// //               id="password"
// //               name="password"
// //               value={formData.password}
// //               onChange={handleInputChange}
// //               placeholder="Enter your password"
// //               disabled={isLoading}
// //               required
// //             />
// //           </div>

// //           {isSignup && (
// //             <div className="form-group">
// //               <label htmlFor="admin_secret">Admin Secret Key</label>
// //               <input
// //                 type="password"
// //                 id="admin_secret"
// //                 name="admin_secret"
// //                 value={formData.admin_secret}
// //                 onChange={handleInputChange}
// //                 placeholder="Enter admin secret key"
// //                 disabled={isLoading}
// //                 required
// //               />
// //               <small className="form-help">
// //                 Contact your administrator for the secret key
// //               </small>
// //             </div>
// //           )}

// //           {error && <div className="error-message">{error}</div>}

// //           <button 
// //             type="submit" 
// //             className="submit-btn"
// //             disabled={isLoading}
// //           >
// //             {isLoading ? "Processing..." : (isSignup ? "Create Account" : "Login")}
// //           </button>
// //         </form>

// //         <div className="form-toggle">
// //           {isSignup ? (
// //             <p>
// //               Already have an account?{" "}
// //               <button
// //                 type="button"
// //                 className="link-btn"
// //                 onClick={() => {
// //                   setIsSignup(false);
// //                   setError("");
// //                   setFormData({
// //                     name: "",
// //                     email: "",
// //                     password: "",
// //                     role: "customer_support_agent",
// //                     admin_secret: ""
// //                   });
// //                 }}
// //                 disabled={isLoading}
// //               >
// //                 Sign up here
// //               </button>
// //             </p>
// //           )}
// //         </div>

// //         <div className="info-note">
// //           <p><strong>Note:</strong> This portal is for administrators and customer support agents only.</p>
// //           <p>Regular users should use the main customer portal.</p>
// //         </div>
// //       </div>
// //     </div>
// //   );
// // }

// // export default AdminLogin;



import React, { useState } from "react";
import API_BASE_URL from "./config";

function AdminLogin({ onLoginSuccess }) {
  const [isSignup, setIsSignup] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "customer_support_agent",
    admin_secret: ""
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(""); // Clear error when user types
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    
    if (!formData.email || !formData.password) {
      setError("Email and password are required");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      console.log("🔐 Attempting login to:", `${API_BASE_URL}/auth/login`);
      
      // 1. Login endpoint
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }).toString(), // ✅ Added .toString() for proper encoding
      });

      const data = await response.json();
      console.log("📥 Login response:", response.status, data);

      if (response.ok) {
        console.log("✅ Login successful, fetching user info...");
        
        // 2. Fetch user info to verify role
        const userInfoResponse = await fetch(`${API_BASE_URL}/auth/me`, {
          method: "GET", // ✅ Explicitly set method
          headers: {
            "Authorization": `Bearer ${data.access_token}`,
            "Content-Type": "application/json" // ✅ Added content-type
          },
        });

        if (userInfoResponse.ok) {
          const userInfo = await userInfoResponse.json();
          console.log("✅ User info received:", userInfo);
          
          // Check if user has admin or support role
          if (userInfo.role === "admin" || userInfo.role === "customer_support_agent") {
            console.log("✅ Role verified:", userInfo.role);
            onLoginSuccess(data.access_token, userInfo);
          } else {
            console.warn("⚠️ Invalid role:", userInfo.role);
            setError(`Access denied. You have role "${userInfo.role}" but admin or support role is required.`);
          }
        } else {
          const errorData = await userInfoResponse.json().catch(() => ({}));
          console.error("❌ Failed to fetch user info:", userInfoResponse.status, errorData);
          setError(errorData.detail || "Failed to verify user information");
        }
      } else {
        console.error("❌ Login failed:", response.status, data);
        setError(data.detail || "Login failed. Please check your credentials.");
      }
    } catch (err) {
      console.error("❌ Connection error:", err);
      setError(`Connection error: ${err.message}. Please check if backend is running at ${API_BASE_URL}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.password || !formData.admin_secret) {
      setError("All fields are required");
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      console.log("📝 Attempting signup to:", `${API_BASE_URL}/auth/admin-signup`);
      
      // 3. Admin Signup endpoint
      const response = await fetch(`${API_BASE_URL}/auth/admin-signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          role: formData.role,
          admin_secret: formData.admin_secret
        }),
      });

      const data = await response.json();
      console.log("📥 Signup response:", response.status, data);

      if (response.ok) {
        console.log("✅ Signup successful, fetching user info...");
        
        // 4. Fetch user info
        const userInfoResponse = await fetch(`${API_BASE_URL}/auth/me`, {
          method: "GET", // ✅ Explicitly set method
          headers: {
            "Authorization": `Bearer ${data.access_token}`,
            "Content-Type": "application/json" // ✅ Added content-type
          },
        });

        if (userInfoResponse.ok) {
          const userInfo = await userInfoResponse.json();
          console.log("✅ User info received:", userInfo);
          onLoginSuccess(data.access_token, userInfo);
        } else {
          const errorData = await userInfoResponse.json().catch(() => ({}));
          console.error("❌ Failed to fetch user info:", userInfoResponse.status, errorData);
          setError("Account created but failed to fetch user info. Please try logging in.");
        }
      } else {
        console.error("❌ Signup failed:", response.status, data);
        
        if (Array.isArray(data.detail)) {
          const errors = data.detail.map(err => {
            const field = err.loc ? err.loc[err.loc.length - 1] : "input";
            return `${field}: ${err.msg || "Invalid input"}`;
          }).join(", ");
          setError(errors);
        } else {
          setError(data.detail || "Signup failed. Please try again.");
        }
      }
    } catch (err) {
      console.error("❌ Connection error:", err);
      setError(`Connection error: ${err.message}. Please check if backend is running at ${API_BASE_URL}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>{isSignup ? "Admin/Support Signup" : "Admin/Support Login"}</h2>
        
        {/* Debug info - remove in production */}
        {process.env.NODE_ENV === 'development' && (
          <div style={{ 
            fontSize: '11px', 
            padding: '8px', 
            background: '#e8f4f8', 
            marginBottom: '10px',
            borderRadius: '4px',
            border: '1px solid #b3d9e8'
          }}>
            <div><strong>🌐 Backend:</strong> {API_BASE_URL}</div>
            <div style={{ marginTop: '4px', fontSize: '10px', color: '#666' }}>
              Mode: {isSignup ? "Signup" : "Login"}
            </div>
          </div>
        )}
        
        <form onSubmit={isSignup ? handleSignup : handleLogin}>
          {isSignup && (
            <>
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Enter your full name"
                  disabled={isLoading}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="role">Role</label>
                <select
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  disabled={isLoading}
                  required
                >
                  <option value="customer_support_agent">Customer Support Agent</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Enter your email"
              disabled={isLoading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Enter your password"
              disabled={isLoading}
              required
            />
          </div>

          {isSignup && (
            <div className="form-group">
              <label htmlFor="admin_secret">Admin Secret Key</label>
              <input
                type="password"
                id="admin_secret"
                name="admin_secret"
                value={formData.admin_secret}
                onChange={handleInputChange}
                placeholder="Enter admin secret key"
                disabled={isLoading}
                required
              />
              <small className="form-help">
                Contact your administrator for the secret key
              </small>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="submit-btn"
            disabled={isLoading}
          >
            {isLoading ? "Processing..." : (isSignup ? "Create Account" : "Login")}
          </button>
        </form>

        <div className="form-toggle">
          {isSignup ? (
            <p>
              Already have an account?{" "}
              <button
                type="button"
                className="link-btn"
                onClick={() => {
                  setIsSignup(false);
                  setError("");
                  setFormData({
                    name: "",
                    email: "",
                    password: "",
                    role: "customer_support_agent",
                    admin_secret: ""
                  });
                }}
                disabled={isLoading}
              >
                Login here
              </button>
            </p>
          ) : (
            <p>
              Need to create an account?{" "}
              <button
                type="button"
                className="link-btn"
                onClick={() => {
                  setIsSignup(true);
                  setError("");
                  setFormData({
                    name: "",
                    email: "",
                    password: "",
                    role: "customer_support_agent",
                    admin_secret: ""
                  });
                }}
                disabled={isLoading}
              >
                Sign up here
              </button>
            </p>
          )}
        </div>

        <div className="info-note">
          <p><strong>Note:</strong> This portal is for administrators and customer support agents only.</p>
          <p>Regular users should use the main customer portal.</p>
        </div>
      </div>
    </div>
  );
}

export default AdminLogin;
