// import React, { useState } from "react";

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
//       const response = await fetch("http://127.0.0.1:8000/auth/login", {
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
//         // Fetch user info to verify role
//         const userInfoResponse = await fetch("http://127.0.0.1:8000/auth/me", {
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
//       const response = await fetch("http://127.0.0.1:8000/auth/admin-signup", {
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
//         // Fetch user info
//         const userInfoResponse = await fetch("http://127.0.0.1:8000/auth/me", {
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
      // 1. Login endpoint
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // 2. Fetch user info to verify role
        const userInfoResponse = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${data.access_token}`,
          },
        });

        if (userInfoResponse.ok) {
          const userInfo = await userInfoResponse.json();
          
          // Check if user has admin or support role
          if (userInfo.role === "admin" || userInfo.role === "customer_support_agent") {
            onLoginSuccess(data.access_token, userInfo);
          } else {
            setError("Access denied. Admin or Support role required.");
          }
        } else {
          setError("Failed to verify user information");
        }
      } else {
        setError(data.detail || "Login failed");
      }
    } catch (err) {
      setError("Connection error. Please try again.");
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

      if (response.ok) {
        // 4. Fetch user info
        const userInfoResponse = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${data.access_token}`,
          },
        });

        if (userInfoResponse.ok) {
          const userInfo = await userInfoResponse.json();
          onLoginSuccess(data.access_token, userInfo);
        } else {
          setError("Account created but failed to fetch user info");
        }
      } else {
        if (Array.isArray(data.detail)) {
          const errors = data.detail.map(err => {
            const field = err.loc ? err.loc[err.loc.length - 1] : "input";
            return `${field}: ${err.msg || "Invalid input"}`;
          }).join(", ");
          setError(errors);
        } else {
          setError(data.detail || "Signup failed");
        }
      }
    } catch (err) {
      setError("Connection error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>{isSignup ? "Admin/Support Signup" : "Admin/Support Login"}</h2>
        
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
