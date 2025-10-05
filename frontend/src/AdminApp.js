// import React, { useState, useEffect } from "react";
// import AdminLogin from "./AdminLogin";
// import AdminDashboard from "./AdminDashboard";
// import SupportDashboard from "./SupportDashboard";
// import "./admin-styles.css";

// function AdminApp() {
//   const [token, setToken] = useState("");
//   const [userInfo, setUserInfo] = useState(null);
//   const [isLoading, setIsLoading] = useState(true);

//   // Check for existing token on app load
//   useEffect(() => {
//     const savedToken = localStorage.getItem("admin_token");
//     if (savedToken) {
//       setToken(savedToken);
//       fetchUserInfo(savedToken);
//     } else {
//       setIsLoading(false);
//     }
//   }, []);

//   const fetchUserInfo = async (authToken) => {
//     try {
//       const response = await fetch("http://127.0.0.1:8000/auth/me", {
//         headers: {
//           Authorization: `Bearer ${authToken}`,
//         },
//       });

//       if (response.ok) {
//         const userData = await response.json();
//         setUserInfo(userData);
//       } else {
//         // Invalid token, remove it
//         localStorage.removeItem("admin_token");
//         setToken("");
//       }
//     } catch (error) {
//       console.error("Failed to fetch user info:", error);
//       localStorage.removeItem("admin_token");
//       setToken("");
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   const handleLoginSuccess = (newToken, userData) => {
//     setToken(newToken);
//     setUserInfo(userData);
//     localStorage.setItem("admin_token", newToken);
//   };

//   const handleLogout = () => {
//     localStorage.removeItem("admin_token");
//     setToken("");
//     setUserInfo(null);
//   };

//   if (isLoading) {
//     return (
//       <div style={{ 
//         display: "flex", 
//         flexDirection: "column", 
//         alignItems: "center", 
//         justifyContent: "center", 
//         minHeight: "calc(100vh - 80px)",
//         background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
//         color: "white"
//       }}>
//         <div style={{
//           width: "40px",
//           height: "40px",
//           border: "4px solid rgba(255, 255, 255, 0.3)",
//           borderRadius: "50%",
//           borderTopColor: "#fff",
//           animation: "spin 1s ease-in-out infinite",
//           marginBottom: "1rem"
//         }}></div>
//         <p>Loading admin portal...</p>
//       </div>
//     );
//   }

//   if (!token || !userInfo) {
//     return (
//       <div style={{ minHeight: "calc(100vh - 80px)" }}>
//         <AdminLogin onLoginSuccess={handleLoginSuccess} />
//       </div>
//     );
//   }

//   return (
//     <div style={{ minHeight: "calc(100vh - 80px)" }}>
//       <header className="app-header">
//         <div className="header-content">
//           <h1>
//             {userInfo.role === "admin" ? "Admin Dashboard" : "Support Dashboard"}
//           </h1>
//           <div className="header-info">
//             <span className="user-info">
//               Welcome, {userInfo.name} ({userInfo.role})
//             </span>
//             <button onClick={handleLogout} className="logout-btn">
//               Logout
//             </button>
//           </div>
//         </div>
//       </header>

//       <main className="main-content">
//         {userInfo.role === "admin" ? (
//           <AdminDashboard token={token} userInfo={userInfo} />
//         ) : userInfo.role === "customer_support_agent" ? (
//           <SupportDashboard token={token} userInfo={userInfo} />
//         ) : (
//           <div className="error-container">
//             <h2>Access Denied</h2>
//             <p>You don't have permission to access this dashboard.</p>
//             <button onClick={handleLogout}>Login with different account</button>
//           </div>
//         )}
//       </main>
//     </div>
//   );
// }

// export default AdminApp;


import React, { useState, useEffect } from "react";
import AdminLogin from "./AdminLogin";
import AdminDashboard from "./AdminDashboard";
import SupportDashboard from "./SupportDashboard";
import "./admin-styles.css";
import API_BASE_URL from "./config"; // ADDED IMPORT

function AdminApp() {
  const [token, setToken] = useState("");
  const [userInfo, setUserInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on app load
  useEffect(() => {
    const savedToken = localStorage.getItem("admin_token");
    if (savedToken) {
      setToken(savedToken);
      fetchUserInfo(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserInfo = async (authToken) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, { // REPLACED URL
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUserInfo(userData);
      } else {
        // Invalid token, remove it
        localStorage.removeItem("admin_token");
        setToken("");
      }
    } catch (error) {
      console.error("Failed to fetch user info:", error);
      localStorage.removeItem("admin_token");
      setToken("");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = (newToken, userData) => {
    setToken(newToken);
    setUserInfo(userData);
    localStorage.setItem("admin_token", newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    setToken("");
    setUserInfo(null);
  };

  if (isLoading) {
    return (
      <div style={{ 
        display: "flex", 
        flexDirection: "column", 
        alignItems: "center", 
        justifyContent: "center", 
        minHeight: "calc(100vh - 80px)",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "white"
      }}>
        <div style={{
          width: "40px",
          height: "40px",
          border: "4px solid rgba(255, 255, 255, 0.3)",
          borderRadius: "50%",
          borderTopColor: "#fff",
          animation: "spin 1s ease-in-out infinite",
          marginBottom: "1rem"
        }}></div>
        <p>Loading admin portal...</p>
      </div>
    );
  }

  if (!token || !userInfo) {
    return (
      <div style={{ minHeight: "calc(100vh - 80px)" }}>
        <AdminLogin onLoginSuccess={handleLoginSuccess} />
      </div>
    );
  }

  return (
    <div style={{ minHeight: "calc(100vh - 80px)" }}>
      <header className="app-header">
        <div className="header-content">
          <h1>
            {userInfo.role === "admin" ? "Admin Dashboard" : "Support Dashboard"}
          </h1>
          <div className="header-info">
            <span className="user-info">
              Welcome, {userInfo.name} ({userInfo.role})
            </span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {userInfo.role === "admin" ? (
          <AdminDashboard token={token} userInfo={userInfo} />
        ) : userInfo.role === "customer_support_agent" ? (
          <SupportDashboard token={token} userInfo={userInfo} />
        ) : (
          <div className="error-container">
            <h2>Access Denied</h2>
            <p>You don't have permission to access this dashboard.</p>
            <button onClick={handleLogout}>Login with different account</button>
          </div>
        )}
      </main>
    </div>
  );
}

export default AdminApp;
