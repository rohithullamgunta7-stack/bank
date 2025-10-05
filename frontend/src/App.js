// import React from "react";
// import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
// import UserApp from "./UserApp";
// import AdminApp from "./AdminApp";
// import "./styles.css";
// import "./auth-styles.css";

// function Navigation() {
//   const location = useLocation();
  
//   return (
//     <nav style={navStyle}>
//       <div style={navContent}>
//         <div style={logoSection}>
//           <svg width="35" height="35" viewBox="0 0 60 60">
//             <circle cx="30" cy="30" r="30" fill="white" opacity="0.2" />
//             <circle cx="30" cy="30" r="28" fill="url(#navGrad)" />
//             <path d="M30 18L38 34H22L30 18Z" fill="white" />
//             <circle cx="30" cy="42" r="3.5" fill="white" />
//             <defs>
//               <linearGradient id="navGrad" x1="0%" y1="0%" x2="100%" y2="100%">
//                 <stop offset="0%" style={{stopColor: '#667eea', stopOpacity: 1}} />
//                 <stop offset="100%" style={{stopColor: '#764ba2', stopOpacity: 1}} />
//               </linearGradient>
//             </defs>
//           </svg>
//           <h3 style={titleStyle}>Support System</h3>
//         </div>
//         <div style={linkContainer}>
//           <Link 
//             to="/" 
//             style={{
//               ...linkStyle,
//               ...(location.pathname === '/' ? activeLinkStyle : {})
//             }}
//           >
//             <span style={iconStyle}>👤</span>
//             <span style={linkTextStyle}>Customer</span>
//           </Link>
//           <Link 
//             to="/admin" 
//             style={{
//               ...linkStyle,
//               ...(location.pathname === '/admin' ? activeLinkStyle : {})
//             }}
//           >
//             <span style={iconStyle}>🛡️</span>
//             <span style={linkTextStyle}>Admin/Support</span>
//           </Link>
//         </div>
//       </div>
//     </nav>
//   );
// }

// function App() {
//   return (
//     <Router>
//       <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
//         <Navigation />
//         <Routes>
//           <Route path="/" element={<UserApp />} />
//           <Route path="/admin" element={<AdminApp />} />
//         </Routes>
//       </div>
//     </Router>
//   );
// }

// const navStyle = {
//   padding: "14px 20px",
//   background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
//   color: "white",
//   boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
//   position: "sticky",
//   top: 0,
//   zIndex: 1000,
//   flexShrink: 0
// };

// const navContent = {
//   display: "flex",
//   justifyContent: "space-between",
//   alignItems: "center",
//   maxWidth: "1200px",
//   margin: "0 auto",
//   gap: "16px"
// };

// const logoSection = {
//   display: 'flex',
//   alignItems: 'center',
//   gap: '10px',
//   minWidth: 0,
//   flex: '0 1 auto'
// };

// const titleStyle = {
//   margin: 0,
//   fontSize: "1.2rem",
//   fontWeight: "600",
//   letterSpacing: "-0.5px",
//   whiteSpace: "nowrap",
//   overflow: "hidden",
//   textOverflow: "ellipsis"
// };

// const linkContainer = {
//   display: "flex",
//   gap: "12px",
//   flexShrink: 0
// };

// const linkStyle = {
//   color: "white",
//   textDecoration: "none",
//   padding: "10px 18px",
//   borderRadius: "8px",
//   fontWeight: "500",
//   transition: "all 0.2s ease",
//   border: "2px solid transparent",
//   display: "flex",
//   alignItems: "center",
//   gap: "6px",
//   fontSize: "14px",
//   whiteSpace: "nowrap"
// };

// const iconStyle = {
//   fontSize: "16px"
// };

// const linkTextStyle = {
//   display: "inline"
// };

// const activeLinkStyle = {
//   backgroundColor: "rgba(255, 255, 255, 0.25)",
//   border: "2px solid rgba(255, 255, 255, 0.4)",
//   boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)"
// };

// export default App;

import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from "react-router-dom";
import UserApp from "./UserApp";
import AdminApp from "./AdminApp";
import "./styles.css";
import "./auth-styles.css";

function Navigation() {
  const location = useLocation();
  
  return (
    <nav style={navStyle}>
      <div style={navContent}>
        <div style={logoSection}>
          <svg width="35" height="35" viewBox="0 0 60 60">
            <circle cx="30" cy="30" r="30" fill="white" opacity="0.2" />
            <circle cx="30" cy="30" r="28" fill="url(#navGrad)" />
            <path d="M30 18L38 34H22L30 18Z" fill="white" />
            <circle cx="30" cy="42" r="3.5" fill="white" />
            <defs>
              <linearGradient id="navGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{stopColor: '#667eea', stopOpacity: 1}} />
                <stop offset="100%" style={{stopColor: '#764ba2', stopOpacity: 1}} />
              </linearGradient>
            </defs>
          </svg>
          <h3 style={titleStyle}>Support System</h3>
        </div>
        <div style={linkContainer}>
          <Link 
            to="/" 
            style={{
              ...linkStyle,
              ...(location.pathname === '/' ? activeLinkStyle : {})
            }}
          >
            <span style={iconStyle}>👤</span>
            <span style={linkTextStyle}>Customer</span>
          </Link>
          <Link 
            to="/admin" 
            style={{
              ...linkStyle,
              ...(location.pathname === '/admin' ? activeLinkStyle : {})
            }}
          >
            <span style={iconStyle}>🛡️</span>
            <span style={linkTextStyle}>Admin/Support</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<UserApp />} />
          <Route path="/admin" element={<AdminApp />} />
        </Routes>
      </div>
    </Router>
  );
}

const navStyle = {
  padding: "14px 20px",
  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  color: "white",
  boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
  position: "sticky",
  top: 0,
  zIndex: 1000,
  flexShrink: 0
};

const navContent = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  maxWidth: "1200px",
  margin: "0 auto",
  gap: "16px"
};

const logoSection = {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  minWidth: 0,
  flex: '0 1 auto'
};

const titleStyle = {
  margin: 0,
  fontSize: "1.2rem",
  fontWeight: "600",
  letterSpacing: "-0.5px",
  whiteSpace: "nowrap",
  overflow: "hidden",
  textOverflow: "ellipsis"
};

const linkContainer = {
  display: "flex",
  gap: "12px",
  flexShrink: 0
};

const linkStyle = {
  color: "white",
  textDecoration: "none",
  padding: "10px 18px",
  borderRadius: "8px",
  fontWeight: "500",
  transition: "all 0.2s ease",
  border: "2px solid transparent",
  display: "flex",
  alignItems: "center",
  gap: "6px",
  fontSize: "14px",
  whiteSpace: "nowrap"
};

const iconStyle = {
  fontSize: "16px"
};

const linkTextStyle = {
  display: "inline"
};

const activeLinkStyle = {
  backgroundColor: "rgba(255, 255, 255, 0.25)",
  border: "2px solid rgba(255, 255, 255, 0.4)",
  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)"
};

export default App;