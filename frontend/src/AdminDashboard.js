

// import React, { useState, useEffect } from "react";
// import ConversationViewer from "./ConversationViewer";
// import FeedbackAnalytics from "./FeedbackAnalytics";
// import FAQManagement from "./FAQManagement";

// function AdminDashboard({ token, userInfo }) {
//   const [activeTab, setActiveTab] = useState("overview");
//   const [dashboardData, setDashboardData] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState("");
//   const [refreshing, setRefreshing] = useState(false);

//   useEffect(() => {
//     fetchDashboardData();
//   }, [token]);

//   const fetchDashboardData = async (isRefresh = false) => {
//     try {
//       if (isRefresh) {
//         setRefreshing(true);
//       } else {
//         setLoading(true);
//       }
      
//       const response = await fetch("http://127.0.0.1:8000/dashboard", {
//         headers: { Authorization: `Bearer ${token}` },
//       });

//       if (response.ok) {
//         const data = await response.json();
//         setDashboardData(data);
//         setError("");
//       } else {
//         setError("Failed to fetch dashboard data");
//       }
//     } catch (err) {
//       setError("Connection error. Please check your internet.");
//     } finally {
//       setLoading(false);
//       setRefreshing(false);
//     }
//   };

//   const renderOverview = () => {
//     if (loading) {
//       return (
//         <div style={styles.loadingContainer}>
//           <div style={styles.spinner}></div>
//           <p style={styles.loadingText}>Loading dashboard...</p>
//         </div>
//       );
//     }

//     if (error) {
//       return (
//         <div style={styles.errorContainer}>
//           <div style={styles.errorIcon}>⚠️</div>
//           <h3 style={styles.errorTitle}>Error Loading Dashboard</h3>
//           <p style={styles.errorMessage}>{error}</p>
//           <button onClick={() => fetchDashboardData()} style={styles.retryButton}>
//             Try Again
//           </button>
//         </div>
//       );
//     }

//     return (
//       <div style={styles.overviewSection}>
//         <div style={styles.headerRow}>
//           <div>
//             <h2 style={styles.sectionTitle}>Dashboard Overview</h2>
//             <p style={styles.sectionSubtitle}>Real-time system statistics and activity</p>
//           </div>
//           <button 
//             onClick={() => fetchDashboardData(true)} 
//             style={styles.refreshButton}
//             disabled={refreshing}
//           >
//             {refreshing ? "Refreshing..." : "Refresh"}
//           </button>
//         </div>

//         <div style={styles.statsGrid}>
//           <div style={{...styles.statCard, ...styles.statCardPurple}}>
//             <div style={styles.statIcon}>👥</div>
//             <div>
//               <h3 style={styles.statLabel}>Total Users</h3>
//               <div style={styles.statNumber}>{dashboardData?.total_users || 0}</div>
//               <p style={styles.statSubtext}>Registered customers</p>
//             </div>
//           </div>

//           <div style={{...styles.statCard, ...styles.statCardGreen}}>
//             <div style={styles.statIcon}>🎧</div>
//             <div>
//               <h3 style={styles.statLabel}>Support Agents</h3>
//               <div style={styles.statNumber}>
//                 {dashboardData?.user_roles_count?.customer_support_agent || 0}
//               </div>
//               <p style={styles.statSubtext}>Active agents</p>
//             </div>
//           </div>

//           <div style={{...styles.statCard, ...styles.statCardOrange}}>
//             <div style={styles.statIcon}>🔐</div>
//             <div>
//               <h3 style={styles.statLabel}>Administrators</h3>
//               <div style={styles.statNumber}>
//                 {dashboardData?.user_roles_count?.admin || 0}
//               </div>
//               <p style={styles.statSubtext}>System admins</p>
//             </div>
//           </div>

//           <div style={{...styles.statCard, ...styles.statCardBlue}}>
//             <div style={styles.statIcon}>💬</div>
//             <div>
//               <h3 style={styles.statLabel}>Conversations</h3>
//               <div style={styles.statNumber}>
//                 {dashboardData?.conversation_summaries?.length || 0}
//               </div>
//               <p style={styles.statSubtext}>Active chats</p>
//             </div>
//           </div>

//           <div style={{...styles.statCard, ...styles.statCardRed}}>
//             <div style={styles.statIcon}>🍕</div>
//             <div>
//               <h3 style={styles.statLabel}>Total Orders</h3>
//               <div style={styles.statNumber}>{dashboardData?.total_orders || 0}</div>
//               <p style={styles.statSubtext}>All time</p>
//             </div>
//           </div>

//           <div style={{...styles.statCard, ...styles.statCardTeal}}>
//             <div style={styles.statIcon}>💰</div>
//             <div>
//               <h3 style={styles.statLabel}>Refund Requests</h3>
//               <div style={styles.statNumber}>{dashboardData?.total_refunds || 0}</div>
//               <p style={styles.statSubtext}>Total processed</p>
//             </div>
//           </div>
//         </div>

//         <div style={styles.recentSection}>
//           <div style={styles.sectionHeader}>
//             <h3 style={styles.recentTitle}>Recent Conversations</h3>
//             <button 
//               onClick={() => setActiveTab("conversations")}
//               style={styles.viewAllButton}
//             >
//               View All →
//             </button>
//           </div>

//           <div style={styles.conversationsList}>
//             {dashboardData?.conversation_summaries?.slice(0, 8).map((conversation, index) => (
//               <div key={index} style={styles.conversationCard}>
//                 <div style={styles.conversationHeader}>
//                   <div style={styles.userAvatar}>
//                     {(conversation.user_name || "U").charAt(0).toUpperCase()}
//                   </div>
//                   <div style={styles.conversationInfo}>
//                     <div style={styles.userName}>
//                       {typeof conversation.user_name === "string"
//                         ? conversation.user_name
//                         : conversation.user_name?.name || "Unknown"}
//                     </div>
//                     <div style={styles.userEmail}>
//                       {typeof conversation.user_email === "string"
//                         ? conversation.user_email
//                         : conversation.user_email?.email || "Unknown"}
//                     </div>
//                   </div>
//                   <div style={styles.messageBadge}>
//                     {conversation.message_count || 0} msgs
//                   </div>
//                 </div>
//                 <div style={styles.lastMessage}>
//                   {conversation.last_message || "-"}
//                 </div>
//                 <div style={styles.timestamp}>
//                   {conversation.last_timestamp
//                     ? new Date(conversation.last_timestamp).toLocaleString()
//                     : "-"}
//                 </div>
//               </div>
//             ))}

//             {(!dashboardData?.conversation_summaries || 
//               dashboardData.conversation_summaries.length === 0) && (
//               <div style={styles.emptyState}>
//                 <div style={styles.emptyIcon}>💬</div>
//                 <p style={styles.emptyText}>No conversations yet</p>
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     );
//   };

//   const renderContent = () => {
//     switch (activeTab) {
//       case "overview":
//         return renderOverview();
//       case "conversations":
//         return <ConversationViewer token={token} role="admin" />;
//       case "feedback":
//         return <FeedbackAnalytics token={token} />;
//       case "faq":
//         return <FAQManagement token={token} />;
//       default:
//         return renderOverview();
//     }
//   };

//   return (
//     <div style={styles.container}>
//       <div style={styles.tabNav}>
//         <button
//           style={{
//             ...styles.tabButton,
//             ...(activeTab === "overview" ? styles.tabButtonActive : {})
//           }}
//           onClick={() => setActiveTab("overview")}
//         >
//           <span style={styles.tabIcon}>📊</span>
//           Overview
//         </button>
//         <button
//           style={{
//             ...styles.tabButton,
//             ...(activeTab === "conversations" ? styles.tabButtonActive : {})
//           }}
//           onClick={() => setActiveTab("conversations")}
//         >
//           <span style={styles.tabIcon}>💬</span>
//           Conversations
//         </button>
//         <button
//           style={{
//             ...styles.tabButton,
//             ...(activeTab === "feedback" ? styles.tabButtonActive : {})
//           }}
//           onClick={() => setActiveTab("feedback")}
//         >
//           <span style={styles.tabIcon}>⭐</span>
//           Feedback
//         </button>
//         <button
//           style={{
//             ...styles.tabButton,
//             ...(activeTab === "faq" ? styles.tabButtonActive : {})
//           }}
//           onClick={() => setActiveTab("faq")}
//         >
//           <span style={styles.tabIcon}>❓</span>
//           FAQ Management
//         </button>
//       </div>

//       <div style={styles.content}>{renderContent()}</div>
//     </div>
//   );
// }

// const styles = {
//   container: {
//     minHeight: "calc(100vh - 150px)"
//   },
//   tabNav: {
//     display: "flex",
//     gap: "0.5rem",
//     marginBottom: "2rem",
//     background: "white",
//     padding: "1rem",
//     borderRadius: "12px",
//     boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
//   },
//   tabButton: {
//     background: "transparent",
//     border: "none",
//     padding: "0.75rem 1.5rem",
//     borderRadius: "8px",
//     cursor: "pointer",
//     fontSize: "0.95rem",
//     fontWeight: "500",
//     color: "#6c757d",
//     transition: "all 0.2s",
//     display: "flex",
//     alignItems: "center",
//     gap: "0.5rem"
//   },
//   tabButtonActive: {
//     background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
//     color: "white",
//     boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)"
//   },
//   tabIcon: {
//     fontSize: "1.2rem"
//   },
//   content: {
//     background: "white",
//     borderRadius: "12px",
//     padding: "2rem",
//     boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
//   },
//   loadingContainer: {
//     display: "flex",
//     flexDirection: "column",
//     alignItems: "center",
//     justifyContent: "center",
//     padding: "4rem",
//     gap: "1rem"
//   },
//   spinner: {
//     width: "50px",
//     height: "50px",
//     border: "4px solid #f3f4f6",
//     borderTop: "4px solid #667eea",
//     borderRadius: "50%",
//     animation: "spin 1s linear infinite"
//   },
//   loadingText: {
//     color: "#6c757d",
//     fontSize: "1rem"
//   },
//   errorContainer: {
//     display: "flex",
//     flexDirection: "column",
//     alignItems: "center",
//     padding: "3rem",
//     gap: "1rem"
//   },
//   errorIcon: {
//     fontSize: "3rem"
//   },
//   errorTitle: {
//     color: "#dc3545",
//     margin: 0
//   },
//   errorMessage: {
//     color: "#6c757d",
//     textAlign: "center"
//   },
//   retryButton: {
//     padding: "0.75rem 2rem",
//     background: "#667eea",
//     color: "white",
//     border: "none",
//     borderRadius: "8px",
//     cursor: "pointer",
//     fontSize: "1rem",
//     fontWeight: "500",
//     transition: "all 0.2s"
//   },
//   overviewSection: {
//     display: "flex",
//     flexDirection: "column",
//     gap: "2rem"
//   },
//   headerRow: {
//     display: "flex",
//     justifyContent: "space-between",
//     alignItems: "flex-start",
//     marginBottom: "1rem"
//   },
//   sectionTitle: {
//     margin: 0,
//     fontSize: "1.75rem",
//     fontWeight: "600",
//     color: "#2d3748"
//   },
//   sectionSubtitle: {
//     margin: "0.5rem 0 0 0",
//     color: "#6c757d",
//     fontSize: "0.95rem"
//   },
//   refreshButton: {
//     padding: "0.75rem 1.5rem",
//     background: "white",
//     border: "2px solid #e2e8f0",
//     borderRadius: "8px",
//     cursor: "pointer",
//     fontSize: "0.9rem",
//     fontWeight: "500",
//     color: "#667eea",
//     transition: "all 0.2s"
//   },
//   statsGrid: {
//     display: "grid",
//     gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
//     gap: "1.5rem"
//   },
//   statCard: {
//     padding: "1.5rem",
//     borderRadius: "12px",
//     display: "flex",
//     alignItems: "center",
//     gap: "1rem",
//     transition: "all 0.3s",
//     cursor: "default"
//   },
//   statCardPurple: {
//     background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
//     color: "white"
//   },
//   statCardGreen: {
//     background: "linear-gradient(135deg, #48bb78 0%, #38a169 100%)",
//     color: "white"
//   },
//   statCardOrange: {
//     background: "linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)",
//     color: "white"
//   },
//   statCardBlue: {
//     background: "linear-gradient(135deg, #4299e1 0%, #3182ce 100%)",
//     color: "white"
//   },
//   statCardRed: {
//     background: "linear-gradient(135deg, #fc8181 0%, #f56565 100%)",
//     color: "white"
//   },
//   statCardTeal: {
//     background: "linear-gradient(135deg, #38b2ac 0%, #319795 100%)",
//     color: "white"
//   },
//   statIcon: {
//     fontSize: "2.5rem",
//     opacity: 0.9
//   },
//   statLabel: {
//     margin: "0 0 0.5rem 0",
//     fontSize: "0.875rem",
//     fontWeight: "500",
//     opacity: 0.9,
//     textTransform: "uppercase",
//     letterSpacing: "0.5px"
//   },
//   statNumber: {
//     fontSize: "2rem",
//     fontWeight: "700",
//     margin: "0.25rem 0"
//   },
//   statSubtext: {
//     margin: "0.25rem 0 0 0",
//     fontSize: "0.8rem",
//     opacity: 0.8
//   },
//   recentSection: {
//     marginTop: "1rem"
//   },
//   sectionHeader: {
//     display: "flex",
//     justifyContent: "space-between",
//     alignItems: "center",
//     marginBottom: "1.5rem"
//   },
//   recentTitle: {
//     margin: 0,
//     fontSize: "1.25rem",
//     fontWeight: "600",
//     color: "#2d3748"
//   },
//   viewAllButton: {
//     padding: "0.5rem 1rem",
//     background: "transparent",
//     border: "none",
//     color: "#667eea",
//     cursor: "pointer",
//     fontSize: "0.9rem",
//     fontWeight: "500",
//     transition: "all 0.2s"
//   },
//   conversationsList: {
//     display: "grid",
//     gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))",
//     gap: "1rem"
//   },
//   conversationCard: {
//     padding: "1.25rem",
//     background: "#f8f9fa",
//     borderRadius: "12px",
//     border: "1px solid #e9ecef",
//     transition: "all 0.2s",
//     cursor: "pointer"
//   },
//   conversationHeader: {
//     display: "flex",
//     alignItems: "center",
//     gap: "0.75rem",
//     marginBottom: "0.75rem"
//   },
//   userAvatar: {
//     width: "45px",
//     height: "45px",
//     borderRadius: "50%",
//     background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
//     display: "flex",
//     alignItems: "center",
//     justifyContent: "center",
//     color: "white",
//     fontWeight: "600",
//     fontSize: "1.1rem",
//     flexShrink: 0
//   },
//   conversationInfo: {
//     flex: 1,
//     minWidth: 0
//   },
//   userName: {
//     fontWeight: "600",
//     color: "#2d3748",
//     fontSize: "0.95rem",
//     whiteSpace: "nowrap",
//     overflow: "hidden",
//     textOverflow: "ellipsis"
//   },
//   userEmail: {
//     color: "#6c757d",
//     fontSize: "0.8rem",
//     whiteSpace: "nowrap",
//     overflow: "hidden",
//     textOverflow: "ellipsis"
//   },
//   messageBadge: {
//     padding: "0.25rem 0.75rem",
//     background: "#667eea",
//     color: "white",
//     borderRadius: "12px",
//     fontSize: "0.75rem",
//     fontWeight: "600",
//     flexShrink: 0
//   },
//   lastMessage: {
//     color: "#495057",
//     fontSize: "0.875rem",
//     marginBottom: "0.5rem",
//     overflow: "hidden",
//     textOverflow: "ellipsis",
//     whiteSpace: "nowrap"
//   },
//   timestamp: {
//     color: "#6c757d",
//     fontSize: "0.75rem"
//   },
//   emptyState: {
//     gridColumn: "1 / -1",
//     textAlign: "center",
//     padding: "3rem",
//     color: "#6c757d"
//   },
//   emptyIcon: {
//     fontSize: "3rem",
//     marginBottom: "1rem"
//   },
//   emptyText: {
//     margin: 0,
//     fontSize: "1rem"
//   }
// };

// const styleSheet = document.createElement("style");
// styleSheet.textContent = `
//   @keyframes spin {
//     to { transform: rotate(360deg); }
//   }
// `;
// if (!document.querySelector('style[data-admin-animations]')) {
//   styleSheet.setAttribute('data-admin-animations', 'true');
//   document.head.appendChild(styleSheet);
// }

// export default AdminDashboard;







import React, { useState, useEffect } from "react";
import ConversationViewer from "./ConversationViewer";
import FeedbackAnalytics from "./FeedbackAnalytics";
import FAQManagement from "./FAQManagement";
import API_BASE_URL from "./config"; // ADDED IMPORT

function AdminDashboard({ token, userInfo }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  const fetchDashboardData = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      const response = await fetch(`${API_BASE_URL}/dashboard`, { // REPLACED URL
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
        setError("");
      } else {
        setError("Failed to fetch dashboard data");
      }
    } catch (err) {
      setError("Connection error. Please check your internet.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const renderOverview = () => {
    if (loading) {
      return (
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading dashboard...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div style={styles.errorContainer}>
          <div style={styles.errorIcon}>⚠️</div>
          <h3 style={styles.errorTitle}>Error Loading Dashboard</h3>
          <p style={styles.errorMessage}>{error}</p>
          <button onClick={() => fetchDashboardData()} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      );
    }

    return (
      <div style={styles.overviewSection}>
        <div style={styles.headerRow}>
          <div>
            <h2 style={styles.sectionTitle}>Dashboard Overview</h2>
            <p style={styles.sectionSubtitle}>Real-time system statistics and activity</p>
          </div>
          <button 
            onClick={() => fetchDashboardData(true)} 
            style={styles.refreshButton}
            disabled={refreshing}
          >
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        <div style={styles.statsGrid}>
          <div style={{...styles.statCard, ...styles.statCardPurple}}>
            <div style={styles.statIcon}>👥</div>
            <div>
              <h3 style={styles.statLabel}>Total Users</h3>
              <div style={styles.statNumber}>{dashboardData?.total_users || 0}</div>
              <p style={styles.statSubtext}>Registered customers</p>
            </div>
          </div>

          <div style={{...styles.statCard, ...styles.statCardGreen}}>
            <div style={styles.statIcon}>🎧</div>
            <div>
              <h3 style={styles.statLabel}>Support Agents</h3>
              <div style={styles.statNumber}>
                {dashboardData?.user_roles_count?.customer_support_agent || 0}
              </div>
              <p style={styles.statSubtext}>Active agents</p>
            </div>
          </div>

          <div style={{...styles.statCard, ...styles.statCardOrange}}>
            <div style={styles.statIcon}>🔐</div>
            <div>
              <h3 style={styles.statLabel}>Administrators</h3>
              <div style={styles.statNumber}>
                {dashboardData?.user_roles_count?.admin || 0}
              </div>
              <p style={styles.statSubtext}>System admins</p>
            </div>
          </div>

          <div style={{...styles.statCard, ...styles.statCardBlue}}>
            <div style={styles.statIcon}>💬</div>
            <div>
              <h3 style={styles.statLabel}>Conversations</h3>
              <div style={styles.statNumber}>
                {dashboardData?.conversation_summaries?.length || 0}
              </div>
              <p style={styles.statSubtext}>Active chats</p>
            </div>
          </div>

          <div style={{...styles.statCard, ...styles.statCardRed}}>
            <div style={styles.statIcon}>🍕</div>
            <div>
              <h3 style={styles.statLabel}>Total Orders</h3>
              <div style={styles.statNumber}>{dashboardData?.total_orders || 0}</div>
              <p style={styles.statSubtext}>All time</p>
            </div>
          </div>

          <div style={{...styles.statCard, ...styles.statCardTeal}}>
            <div style={styles.statIcon}>💰</div>
            <div>
              <h3 style={styles.statLabel}>Refund Requests</h3>
              <div style={styles.statNumber}>{dashboardData?.total_refunds || 0}</div>
              <p style={styles.statSubtext}>Total processed</p>
            </div>
          </div>
        </div>

        <div style={styles.recentSection}>
          <div style={styles.sectionHeader}>
            <h3 style={styles.recentTitle}>Recent Conversations</h3>
            <button 
              onClick={() => setActiveTab("conversations")}
              style={styles.viewAllButton}
            >
              View All →
            </button>
          </div>

          <div style={styles.conversationsList}>
            {dashboardData?.conversation_summaries?.slice(0, 8).map((conversation, index) => (
              <div key={index} style={styles.conversationCard}>
                <div style={styles.conversationHeader}>
                  <div style={styles.userAvatar}>
                    {(conversation.user_name || "U").charAt(0).toUpperCase()}
                  </div>
                  <div style={styles.conversationInfo}>
                    <div style={styles.userName}>
                      {typeof conversation.user_name === "string"
                        ? conversation.user_name
                        : conversation.user_name?.name || "Unknown"}
                    </div>
                    <div style={styles.userEmail}>
                      {typeof conversation.user_email === "string"
                        ? conversation.user_email
                        : conversation.user_email?.email || "Unknown"}
                    </div>
                  </div>
                  <div style={styles.messageBadge}>
                    {conversation.message_count || 0} msgs
                  </div>
                </div>
                <div style={styles.lastMessage}>
                  {conversation.last_message || "-"}
                </div>
                <div style={styles.timestamp}>
                  {conversation.last_timestamp
                    ? new Date(conversation.last_timestamp).toLocaleString()
                    : "-"}
                </div>
              </div>
            ))}

            {(!dashboardData?.conversation_summaries || 
              dashboardData.conversation_summaries.length === 0) && (
              <div style={styles.emptyState}>
                <div style={styles.emptyIcon}>💬</div>
                <p style={styles.emptyText}>No conversations yet</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case "overview":
        return renderOverview();
      case "conversations":
        return <ConversationViewer token={token} role="admin" />;
      case "feedback":
        return <FeedbackAnalytics token={token} />;
      case "faq":
        return <FAQManagement token={token} />;
      default:
        return renderOverview();
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.tabNav}>
        <button
          style={{
            ...styles.tabButton,
            ...(activeTab === "overview" ? styles.tabButtonActive : {})
          }}
          onClick={() => setActiveTab("overview")}
        >
          <span style={styles.tabIcon}>📊</span>
          Overview
        </button>
        <button
          style={{
            ...styles.tabButton,
            ...(activeTab === "conversations" ? styles.tabButtonActive : {})
          }}
          onClick={() => setActiveTab("conversations")}
        >
          <span style={styles.tabIcon}>💬</span>
          Conversations
        </button>
        <button
          style={{
            ...styles.tabButton,
            ...(activeTab === "feedback" ? styles.tabButtonActive : {})
          }}
          onClick={() => setActiveTab("feedback")}
        >
          <span style={styles.tabIcon}>⭐</span>
          Feedback
        </button>
        <button
          style={{
            ...styles.tabButton,
            ...(activeTab === "faq" ? styles.tabButtonActive : {})
          }}
          onClick={() => setActiveTab("faq")}
        >
          <span style={styles.tabIcon}>❓</span>
          FAQ Management
        </button>
      </div>

      <div style={styles.content}>{renderContent()}</div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "calc(100vh - 150px)"
  },
  tabNav: {
    display: "flex",
    gap: "0.5rem",
    marginBottom: "2rem",
    background: "white",
    padding: "1rem",
    borderRadius: "12px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
  },
  tabButton: {
    background: "transparent",
    border: "none",
    padding: "0.75rem 1.5rem",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "0.95rem",
    fontWeight: "500",
    color: "#6c757d",
    transition: "all 0.2s",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem"
  },
  tabButtonActive: {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)"
  },
  tabIcon: {
    fontSize: "1.2rem"
  },
  content: {
    background: "white",
    borderRadius: "12px",
    padding: "2rem",
    boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
  },
  loadingContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "4rem",
    gap: "1rem"
  },
  spinner: {
    width: "50px",
    height: "50px",
    border: "4px solid #f3f4f6",
    borderTop: "4px solid #667eea",
    borderRadius: "50%",
    animation: "spin 1s linear infinite"
  },
  loadingText: {
    color: "#6c757d",
    fontSize: "1rem"
  },
  errorContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "3rem",
    gap: "1rem"
  },
  errorIcon: {
    fontSize: "3rem"
  },
  errorTitle: {
    color: "#dc3545",
    margin: 0
  },
  errorMessage: {
    color: "#6c757d",
    textAlign: "center"
  },
  retryButton: {
    padding: "0.75rem 2rem",
    background: "#667eea",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "500",
    transition: "all 0.2s"
  },
  overviewSection: {
    display: "flex",
    flexDirection: "column",
    gap: "2rem"
  },
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "1rem"
  },
  sectionTitle: {
    margin: 0,
    fontSize: "1.75rem",
    fontWeight: "600",
    color: "#2d3748"
  },
  sectionSubtitle: {
    margin: "0.5rem 0 0 0",
    color: "#6c757d",
    fontSize: "0.95rem"
  },
  refreshButton: {
    padding: "0.75rem 1.5rem",
    background: "white",
    border: "2px solid #e2e8f0",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: "500",
    color: "#667eea",
    transition: "all 0.2s"
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
    gap: "1.5rem"
  },
  statCard: {
    padding: "1.5rem",
    borderRadius: "12px",
    display: "flex",
    alignItems: "center",
    gap: "1rem",
    transition: "all 0.3s",
    cursor: "default"
  },
  statCardPurple: {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white"
  },
  statCardGreen: {
    background: "linear-gradient(135deg, #48bb78 0%, #38a169 100%)",
    color: "white"
  },
  statCardOrange: {
    background: "linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)",
    color: "white"
  },
  statCardBlue: {
    background: "linear-gradient(135deg, #4299e1 0%, #3182ce 100%)",
    color: "white"
  },
  statCardRed: {
    background: "linear-gradient(135deg, #fc8181 0%, #f56565 100%)",
    color: "white"
  },
  statCardTeal: {
    background: "linear-gradient(135deg, #38b2ac 0%, #319795 100%)",
    color: "white"
  },
  statIcon: {
    fontSize: "2.5rem",
    opacity: 0.9
  },
  statLabel: {
    margin: "0 0 0.5rem 0",
    fontSize: "0.875rem",
    fontWeight: "500",
    opacity: 0.9,
    textTransform: "uppercase",
    letterSpacing: "0.5px"
  },
  statNumber: {
    fontSize: "2rem",
    fontWeight: "700",
    margin: "0.25rem 0"
  },
  statSubtext: {
    margin: "0.25rem 0 0 0",
    fontSize: "0.8rem",
    opacity: 0.8
  },
  recentSection: {
    marginTop: "1rem"
  },
  sectionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "1.5rem"
  },
  recentTitle: {
    margin: 0,
    fontSize: "1.25rem",
    fontWeight: "600",
    color: "#2d3748"
  },
  viewAllButton: {
    padding: "0.5rem 1rem",
    background: "transparent",
    border: "none",
    color: "#667eea",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: "500",
    transition: "all 0.2s"
  },
  conversationsList: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(350px, 1fr))",
    gap: "1rem"
  },
  conversationCard: {
    padding: "1.25rem",
    background: "#f8f9fa",
    borderRadius: "12px",
    border: "1px solid #e9ecef",
    transition: "all 0.2s",
    cursor: "pointer"
  },
  conversationHeader: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    marginBottom: "0.75rem"
  },
  userAvatar: {
    width: "45px",
    height: "45px",
    borderRadius: "50%",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "white",
    fontWeight: "600",
    fontSize: "1.1rem",
    flexShrink: 0
  },
  conversationInfo: {
    flex: 1,
    minWidth: 0
  },
  userName: {
    fontWeight: "600",
    color: "#2d3748",
    fontSize: "0.95rem",
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis"
  },
  userEmail: {
    color: "#6c757d",
    fontSize: "0.8rem",
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis"
  },
  messageBadge: {
    padding: "0.25rem 0.75rem",
    background: "#667eea",
    color: "white",
    borderRadius: "12px",
    fontSize: "0.75rem",
    fontWeight: "600",
    flexShrink: 0
  },
  lastMessage: {
    color: "#495057",
    fontSize: "0.875rem",
    marginBottom: "0.5rem",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap"
  },
  timestamp: {
    color: "#6c757d",
    fontSize: "0.75rem"
  },
  emptyState: {
    gridColumn: "1 / -1",
    textAlign: "center",
    padding: "3rem",
    color: "#6c757d"
  },
  emptyIcon: {
    fontSize: "3rem",
    marginBottom: "1rem"
  },
  emptyText: {
    margin: 0,
    fontSize: "1rem"
  }
};

const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;
if (!document.querySelector('style[data-admin-animations]')) {
  styleSheet.setAttribute('data-admin-animations', 'true');
  document.head.appendChild(styleSheet);
}

export default AdminDashboard;