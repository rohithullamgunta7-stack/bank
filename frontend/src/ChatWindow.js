

// // // import React, { useState, useEffect, useRef } from "react";
// // // import EscalationButton from './EscalationButton';
// // // import FeedbackModal from './FeedbackModal';

// // // function ChatWindow({ token, onLogout }) {
// // //   const [messages, setMessages] = useState([]);
// // //   const [input, setInput] = useState("");
// // //   const [loading, setLoading] = useState(false);
// // //   const [escalationId, setEscalationId] = useState(null);
// // //   const [wsConnected, setWsConnected] = useState(false);
// // //   const [userInfo, setUserInfo] = useState(null);
// // //   const [showFeedbackModal, setShowFeedbackModal] = useState(false);
// // //   const [currentSessionId, setCurrentSessionId] = useState(null);
// // //   const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
// // //   const [isLoggingOut, setIsLoggingOut] = useState(false);

// // //   const wsRef = useRef(null);
// // //   const messagesEndRef = useRef(null);
// // //   const escalationIdRef = useRef(null);
// // //   const heartbeatIntervalRef = useRef(null);
// // //   const feedbackCheckTimeoutRef = useRef(null);

// // //   useEffect(() => {
// // //     escalationIdRef.current = escalationId;
// // //   }, [escalationId]);

// // //   useEffect(() => {
// // //     fetchUserInfo();
// // //     checkForExistingEscalation();

// // //     return () => {
// // //       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// // //       if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
// // //       if (wsRef.current) wsRef.current.close();
// // //     };
// // //   }, [token]);

// // //   useEffect(() => scrollToBottom(), [messages]);

// // //   useEffect(() => {
// // //     if (userInfo?.user_id && !wsConnected && !wsRef.current) {
// // //       connectWebSocket(userInfo.user_id);
// // //     }
// // //   }, [userInfo]);

// // //   // FIXED: Only check feedback when bot sends a goodbye message
// // //   useEffect(() => {
// // //     if (messages.length > 0 && !escalationId && !feedbackSubmitted && !isLoggingOut) {
// // //       const lastMsg = messages[messages.length - 1];
      
// // //       // Only trigger on specific bot goodbye messages
// // //       if (lastMsg.sender === "bot") {
// // //         const botText = lastMsg.text.toLowerCase();
        
// // //         // Check if bot is ending the conversation
// // //         const goodbyePatterns = [
// // //           "welcome", "have a great day", "have a good day", 
// // //           "glad to help", "happy to help", "pleasure helping",
// // //           "if you need anything", "feel free to reach out"
// // //         ];
        
// // //         const isGoodbyeMessage = goodbyePatterns.some(pattern => botText.includes(pattern));
        
// // //         if (isGoodbyeMessage) {
// // //           console.log("✅ Bot sent goodbye, checking feedback in 2 seconds...");
          
// // //           // Clear any existing timeout
// // //           if (feedbackCheckTimeoutRef.current) {
// // //             clearTimeout(feedbackCheckTimeoutRef.current);
// // //           }
          
// // //           // Set new timeout
// // //           feedbackCheckTimeoutRef.current = setTimeout(() => {
// // //             checkFeedbackPrompt();
// // //           }, 2000);
// // //         }
// // //       }
// // //     }
    
// // //     // Cleanup on unmount
// // //     return () => {
// // //       if (feedbackCheckTimeoutRef.current) {
// // //         clearTimeout(feedbackCheckTimeoutRef.current);
// // //       }
// // //     };
// // //   }, [messages, escalationId, feedbackSubmitted, isLoggingOut]);

// // //   const fetchUserInfo = async () => {
// // //     try {
// // //       const response = await fetch("http://127.0.0.1:8000/auth/me", {
// // //         headers: { Authorization: `Bearer ${token}` },
// // //       });
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         console.log("✅ User info loaded:", data);
// // //         setUserInfo(data);
// // //       }
// // //     } catch (error) {
// // //       console.error("❌ Error fetching user info:", error);
// // //     }
// // //   };

// // //   const checkForExistingEscalation = async () => {
// // //     try {
// // //       const response = await fetch("http://127.0.0.1:8000/escalation/escalations/my", {
// // //         headers: { Authorization: `Bearer ${token}` },
// // //       });
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         const activeEscalation = data.escalations?.find(
// // //           esc => esc.status !== 'resolved' && esc.status !== 'closed'
// // //         );
// // //         if (activeEscalation) {
// // //           setEscalationId(activeEscalation.escalation_id);
// // //           escalationIdRef.current = activeEscalation.escalation_id;
// // //           await loadEscalationHistory(activeEscalation.escalation_id);
// // //           setMessages(prev => [...prev, {
// // //             sender: "system",
// // //             text: `Resuming your support session (Case #${activeEscalation.escalation_id.slice(0, 8)})`,
// // //             timestamp: new Date().toISOString()
// // //           }]);
// // //         }
// // //       }
// // //     } catch (error) {
// // //       console.error("Error checking for existing escalations:", error);
// // //     }
// // //   };

// // //   const loadEscalationHistory = async (escId) => {
// // //     try {
// // //       const response = await fetch(
// // //         `http://127.0.0.1:8000/escalation/messages/${escId}`,
// // //         { headers: { Authorization: `Bearer ${token}` } }
// // //       );
      
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         const formattedMessages = data.messages.map(msg => ({
// // //           sender: msg.sender === 'user' ? 'user' : 'bot',
// // //           text: msg.message,
// // //           timestamp: msg.timestamp,
// // //           isAgent: msg.sender === 'agent'
// // //         }));
// // //         setMessages(formattedMessages);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error loading escalation history:", error);
// // //     }
// // //   };

// // //   const checkFeedbackPrompt = async () => {
// // //     if (!userInfo?.user_id || feedbackSubmitted || escalationId || isLoggingOut) {
// // //       console.log("⏭️ Feedback check skipped:", { 
// // //         hasUser: !!userInfo?.user_id, 
// // //         feedbackSubmitted, 
// // //         escalationId,
// // //         isLoggingOut
// // //       });
// // //       return;
// // //     }
    
// // //     console.log("🔍 Checking for feedback prompt for user:", userInfo.user_id);
    
// // //     try {
// // //       const response = await fetch(
// // //         `http://127.0.0.1:8000/feedback/check-prompt/${userInfo.user_id}`,
// // //         { headers: { Authorization: `Bearer ${token}` } }
// // //       );
      
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         console.log("📋 Feedback prompt response:", data);
        
// // //         if (data.should_ask && data.session_id && !isLoggingOut) {
// // //           console.log("✅ Showing feedback modal!");
// // //           setCurrentSessionId(data.session_id);
// // //           setShowFeedbackModal(true);
// // //         } else {
// // //           console.log("⏳ Not time for feedback yet");
// // //         }
// // //       } else {
// // //         console.error("❌ Feedback check failed with status:", response.status);
// // //       }
// // //     } catch (error) {
// // //       console.error("❌ Error checking feedback prompt:", error);
// // //     }
// // //   };

// // //   const handleFeedbackSubmit = async (feedbackData) => {
// // //     try {
// // //       const response = await fetch("http://127.0.0.1:8000/feedback/submit", {
// // //         method: "POST",
// // //         headers: {
// // //           "Content-Type": "application/json",
// // //           Authorization: `Bearer ${token}`
// // //         },
// // //         body: JSON.stringify(feedbackData)
// // //       });
      
// // //       if (response.ok) {
// // //         console.log("✅ Feedback submitted successfully!");
// // //         setShowFeedbackModal(false);
// // //         setFeedbackSubmitted(true);
// // //         setMessages(prev => [...prev, {
// // //           sender: "system",
// // //           text: "Thank you for your feedback! We appreciate your input.",
// // //           timestamp: new Date().toISOString()
// // //         }]);
// // //       } else {
// // //         alert("Failed to submit feedback. Please try again.");
// // //       }
// // //     } catch (error) {
// // //       console.error("Error submitting feedback:", error);
// // //       alert("Connection error. Please try again.");
// // //     }
// // //   };

// // //   const handleFeedbackClose = () => {
// // //     console.log("🚪 Feedback modal closed");
// // //     setShowFeedbackModal(false);
    
// // //     // If user was trying to logout, proceed with logout
// // //     if (isLoggingOut) {
// // //       console.log("🔄 Proceeding with logout after feedback close");
// // //       proceedWithLogout();
// // //     }
// // //   };

// // //   const handleLogoutClick = () => {
// // //     console.log("🚪 Logout clicked");
    
// // //     // If feedback modal is open, just set logging out flag
// // //     if (showFeedbackModal) {
// // //       console.log("⚠️ Feedback modal is open, setting logout flag");
// // //       setIsLoggingOut(true);
// // //       setShowFeedbackModal(false); // Close feedback modal
// // //       return;
// // //     }
    
// // //     // Otherwise logout directly
// // //     proceedWithLogout();
// // //   };

// // //   const proceedWithLogout = () => {
// // //     console.log("✅ Proceeding with logout");
    
// // //     // Clear all timeouts
// // //     if (feedbackCheckTimeoutRef.current) {
// // //       clearTimeout(feedbackCheckTimeoutRef.current);
// // //     }
// // //     if (heartbeatIntervalRef.current) {
// // //       clearInterval(heartbeatIntervalRef.current);
// // //     }
    
// // //     // Close WebSocket
// // //     if (wsRef.current) {
// // //       wsRef.current.close();
// // //     }
    
// // //     // Call parent logout
// // //     if (onLogout) {
// // //       onLogout();
// // //     }
// // //   };

// // //   const connectWebSocket = (userId) => {
// // //     if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) return;
// // //     if (wsRef.current) wsRef.current.close();

// // //     const ws = new WebSocket(`ws://127.0.0.1:8000/escalation/ws/user/${userId}`);

// // //     ws.onopen = () => {
// // //       setWsConnected(true);
// // //       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// // //       heartbeatIntervalRef.current = setInterval(() => {
// // //         if (ws.readyState === WebSocket.OPEN) {
// // //           ws.send(JSON.stringify({ type: 'ping' }));
// // //         }
// // //       }, 30000);
// // //     };

// // //     ws.onmessage = (event) => {
// // //       try {
// // //         const data = JSON.parse(event.data);
// // //         if (data.type === 'ping') {
// // //           ws.send(JSON.stringify({ type: 'pong' }));
// // //           return;
// // //         }
// // //         if (data.type === 'agent_message') {
// // //           setMessages(prev => [...prev, {
// // //             sender: "bot",
// // //             text: data.message,
// // //             timestamp: data.timestamp,
// // //             isAgent: true
// // //           }]);
// // //         } else if (data.type === 'error') {
// // //           setMessages(prev => [...prev, {
// // //             sender: "system",
// // //             text: `Error: ${data.message}`,
// // //             timestamp: new Date().toISOString()
// // //           }]);
// // //         }
// // //       } catch (error) {
// // //         console.error("Error parsing WebSocket message:", error);
// // //       }
// // //     };

// // //     ws.onerror = () => setWsConnected(false);

// // //     ws.onclose = (event) => {
// // //       setWsConnected(false);
// // //       wsRef.current = null;
// // //       if (heartbeatIntervalRef.current) {
// // //         clearInterval(heartbeatIntervalRef.current);
// // //         heartbeatIntervalRef.current = null;
// // //       }
// // //       if (event.code !== 1000 && userInfo?.user_id && !isLoggingOut) {
// // //         setTimeout(() => connectWebSocket(userInfo.user_id), 3000);
// // //       }
// // //     };

// // //     wsRef.current = ws;
// // //   };

// // //   const handleEscalationCreated = async (escId) => {
// // //     if (escalationIdRef.current && escalationIdRef.current !== escId) {
// // //       alert("You already have an active support session. Continue chatting here.");
// // //       return;
// // //     }
// // //     setEscalationId(escId);
// // //     escalationIdRef.current = escId;
// // //     if (userInfo?.user_id && !wsConnected) connectWebSocket(userInfo.user_id);
// // //     if (!escalationId) {
// // //       setMessages(prev => [...prev, {
// // //         sender: "system",
// // //         text: "You've been connected to a live support agent. They will assist you shortly.",
// // //         timestamp: new Date().toISOString()
// // //       }]);
// // //     }
// // //   };

// // //   const handleOrderClick = async (orderId) => {
// // //     setMessages(prev => [...prev, { 
// // //       sender: "user", 
// // //       text: orderId, 
// // //       timestamp: new Date().toISOString() 
// // //     }]);

// // //     setLoading(true);
// // //     try {
// // //       const res = await fetch("http://127.0.0.1:8000/chat", {
// // //         method: "POST",
// // //         headers: { 
// // //           "Content-Type": "application/json", 
// // //           Authorization: `Bearer ${token}` 
// // //         },
// // //         body: JSON.stringify({ message: orderId }),
// // //       });
      
// // //       if (res.ok) {
// // //         const data = await res.json();
// // //         setMessages(prev => [...prev, { 
// // //           sender: "bot", 
// // //           text: data.reply, 
// // //           timestamp: new Date().toISOString() 
// // //         }]);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error fetching order details:", error);
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   const sendMessage = async () => {
// // //     if (!input.trim()) return;
    
// // //     const userMessage = input.trim();
// // //     setInput("");
// // //     setMessages(prev => [...prev, { 
// // //       sender: "user", 
// // //       text: userMessage, 
// // //       timestamp: new Date().toISOString() 
// // //     }]);

// // //     const currentEscalationId = escalationIdRef.current;

// // //     if (currentEscalationId) {
// // //       if (wsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
// // //         wsRef.current.send(JSON.stringify({ 
// // //           type: "message", 
// // //           escalation_id: currentEscalationId, 
// // //           message: userMessage 
// // //         }));
// // //       } else {
// // //         if (userInfo?.user_id) connectWebSocket(userInfo.user_id);
// // //         setMessages(prev => [...prev, {
// // //           sender: "system",
// // //           text: "Connecting to support agent...",
// // //           timestamp: new Date().toISOString()
// // //         }]);
// // //       }
// // //       return;
// // //     }

// // //     setLoading(true);
// // //     try {
// // //       const res = await fetch("http://127.0.0.1:8000/chat", {
// // //         method: "POST",
// // //         headers: { 
// // //           "Content-Type": "application/json", 
// // //           Authorization: `Bearer ${token}` 
// // //         },
// // //         body: JSON.stringify({ message: userMessage }),
// // //       });
      
// // //       if (res.ok) {
// // //         const data = await res.json();
        
// // //         if (data.reply === "ORDER_LIST" && data.orders && Array.isArray(data.orders)) {
// // //           setMessages(prev => [...prev, { 
// // //             sender: "bot", 
// // //             text: "Here are your recent orders:",
// // //             orders: data.orders,
// // //             timestamp: new Date().toISOString() 
// // //           }]);
// // //         } else {
// // //           setMessages(prev => [...prev, { 
// // //             sender: "bot", 
// // //             text: data.reply, 
// // //             timestamp: new Date().toISOString() 
// // //           }]);

// // //           const escMatch = data.reply.match(/ESC_\d+/);
// // //           if (escMatch) {
// // //             const foundEscId = escMatch[0];
// // //             setEscalationId(foundEscId);
// // //             escalationIdRef.current = foundEscId;
// // //             if (userInfo?.user_id && (!wsConnected || wsRef.current.readyState !== WebSocket.OPEN)) {
// // //               connectWebSocket(userInfo.user_id);
// // //             }
// // //             setMessages(prev => [...prev, {
// // //               sender: "system",
// // //               text: "You are now connected to live support.",
// // //               timestamp: new Date().toISOString()
// // //             }]);
// // //           }
// // //         }
// // //       } else {
// // //         setMessages(prev => [...prev, { 
// // //           sender: "bot", 
// // //           text: "Sorry, an error occurred. Please try again.", 
// // //           timestamp: new Date().toISOString() 
// // //         }]);
// // //       }
// // //     } catch (error) {
// // //       console.error("Send message error:", error);
// // //       setMessages(prev => [...prev, { 
// // //         sender: "bot", 
// // //         text: "Connection error. Check your internet.", 
// // //         timestamp: new Date().toISOString() 
// // //       }]);
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   const scrollToBottom = () => {
// // //     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
// // //   };

// // //   const getStatusColor = (status) => {
// // //     const s = status.toLowerCase();
// // //     if (s.includes('delivered')) return '#4caf50';
// // //     if (s.includes('delivery')) return '#2196f3';
// // //     if (s.includes('preparing') || s.includes('processing')) return '#ff9800';
// // //     if (s.includes('cancelled')) return '#f44336';
// // //     return '#757575';
// // //   };

// // //   const getStatusEmoji = (status) => {
// // //     const s = status.toLowerCase();
// // //     if (s.includes('delivered')) return '✓';
// // //     if (s.includes('delivery')) return '🚚';
// // //     if (s.includes('preparing') || s.includes('processing')) return '🍳';
// // //     if (s.includes('ready')) return '✅';
// // //     if (s.includes('cancelled')) return '✗';
// // //     return '📦';
// // //   };

// // //   return (
// // //     <div style={styles.container}>
// // //       <div style={styles.header}>
// // //         <div>
// // //           <h2 style={styles.title}>
// // //             {escalationId ? "Live Agent Support" : "AI Support Assistant"}
// // //           </h2>
// // //           {escalationId && (
// // //             <p style={styles.modeIndicator}>
// // //               You are now chatting with a human support agent
// // //             </p>
// // //           )}
// // //         </div>
// // //         <div style={styles.statusContainer}>
// // //           {wsConnected && escalationId && (
// // //             <span style={styles.statusIndicator}>
// // //               <span style={styles.greenDot}>●</span> Agent Online
// // //             </span>
// // //           )}
// // //           {wsConnected && !escalationId && (
// // //             <span style={styles.statusIndicatorGray}>
// // //               <span style={styles.grayDot}>●</span> Ready
// // //             </span>
// // //           )}
// // //           {!wsConnected && userInfo && (
// // //             <span style={styles.statusIndicatorOff}>
// // //               <span style={styles.yellowDot}>●</span> Connecting...
// // //             </span>
// // //           )}
// // //         </div>
// // //       </div>

// // //       <EscalationButton token={token} onEscalationCreated={handleEscalationCreated} />

// // //       <div style={styles.chatBox}>
// // //         {messages.length === 0 && (
// // //           <div style={styles.emptyState}>
// // //             <p>Hello! How can I help you today?</p>
// // //             <p style={styles.emptyHint}>
// // //               Ask about orders, deliveries, refunds, or any issues you're experiencing.
// // //             </p>
// // //           </div>
// // //         )}
        
// // //         {messages.map((msg, i) => (
// // //           <div key={i}>
// // //             <div 
// // //               style={{
// // //                 ...styles.message,
// // //                 ...(msg.sender === "user" 
// // //                   ? styles.userMessage 
// // //                   : msg.sender === "system" 
// // //                   ? styles.systemMessage 
// // //                   : styles.botMessage)
// // //               }}
// // //             >
// // //               {msg.isAgent && <span style={styles.agentBadge}>Agent</span>}
// // //               <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
// // //               {msg.timestamp && (
// // //                 <div style={styles.timestamp}>
// // //                   {new Date(msg.timestamp).toLocaleTimeString()}
// // //                 </div>
// // //               )}
// // //             </div>

// // //             {msg.orders && msg.orders.length > 0 && (
// // //               <div style={styles.orderCardsContainer}>
// // //                 {msg.orders.map((order, idx) => (
// // //                   <div 
// // //                     key={idx} 
// // //                     style={styles.orderCard}
// // //                     onClick={() => handleOrderClick(order.order_id)}
// // //                     onMouseEnter={(e) => {
// // //                       e.currentTarget.style.transform = 'translateY(-2px)';
// // //                       e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.15)';
// // //                       e.currentTarget.style.borderColor = '#667eea';
// // //                     }}
// // //                     onMouseLeave={(e) => {
// // //                       e.currentTarget.style.transform = 'translateY(0)';
// // //                       e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
// // //                       e.currentTarget.style.borderColor = '#e0e0e0';
// // //                     }}
// // //                   >
// // //                     <div style={styles.orderHeader}>
// // //                       <div style={styles.orderRestaurant}>
// // //                         🍽️ {order.restaurant}
// // //                       </div>
// // //                       <div 
// // //                         style={{
// // //                           ...styles.orderStatus,
// // //                           backgroundColor: getStatusColor(order.status)
// // //                         }}
// // //                       >
// // //                         {getStatusEmoji(order.status)} {order.status}
// // //                       </div>
// // //                     </div>

// // //                     <div style={styles.orderItems}>
// // //                       <strong>Items:</strong> {order.items.slice(0, 3).join(', ')}
// // //                       {order.items.length > 3 && ` +${order.items.length - 3} more`}
// // //                     </div>

// // //                     <div style={styles.orderDetails}>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span>📅 {order.order_date}</span>
// // //                       </div>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span>📍 {order.delivery_address}</span>
// // //                       </div>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span style={styles.orderTotal}>💵 ${order.total_amount}</span>
// // //                       </div>
// // //                     </div>

// // //                     <div style={styles.orderFooter}>
// // //                       Order ID: {order.order_id.slice(0, 8)}...
// // //                     </div>

// // //                     <div style={styles.clickHint}>
// // //                       Click to view full details
// // //                     </div>
// // //                   </div>
// // //                 ))}
// // //               </div>
// // //             )}
// // //           </div>
// // //         ))}
        
// // //         {loading && (
// // //           <div style={styles.loadingMessage}>
// // //             <div style={styles.typingDots}>
// // //               <span>.</span><span>.</span><span>.</span>
// // //             </div>
// // //           </div>
// // //         )}
        
// // //         <div ref={messagesEndRef} />
// // //       </div>

// // //       <div style={styles.inputArea}>
// // //         <input
// // //           type="text"
// // //           value={input}
// // //           onChange={e => setInput(e.target.value)}
// // //           onKeyDown={e => e.key === "Enter" && !loading && sendMessage()}
// // //           placeholder={
// // //             escalationId && wsConnected 
// // //               ? "Message the agent..." 
// // //               : escalationId && !wsConnected 
// // //               ? "Connecting to agent..." 
// // //               : "Type your message..."
// // //           }
// // //           disabled={loading || (escalationId && !wsConnected)}
// // //           style={styles.input}
// // //         />
// // //         <button 
// // //           onClick={sendMessage} 
// // //           disabled={loading || !input.trim() || (escalationId && !wsConnected)} 
// // //           style={{
// // //             ...styles.sendButton,
// // //             ...(loading || !input.trim() || (escalationId && !wsConnected) 
// // //               ? styles.sendButtonDisabled 
// // //               : {})
// // //           }}
// // //         >
// // //           {loading ? "..." : "Send"}
// // //         </button>
// // //       </div>

// // //       <FeedbackModal
// // //         show={showFeedbackModal}
// // //         onClose={handleFeedbackClose}
// // //         onSubmit={handleFeedbackSubmit}
// // //         sessionId={currentSessionId}
// // //       />
// // //     </div>
// // //   );
// // // }

// // // const styles = {
// // //   container: { 
// // //     maxWidth: "1200px", 
// // //     margin: "0 auto", 
// // //     padding: "20px", 
// // //     fontFamily: "'Inter', sans-serif",
// // //     height: "calc(100vh - 40px)",
// // //     display: "flex",
// // //     flexDirection: "column"
// // //   },
// // //   header: { 
// // //     display: "flex", 
// // //     justifyContent: "space-between", 
// // //     alignItems: "center", 
// // //     marginBottom: "15px",
// // //     paddingBottom: "15px",
// // //     borderBottom: "2px solid #e0e0e0"
// // //   },
// // //   title: { 
// // //     margin: 0, 
// // //     fontSize: "1.5rem", 
// // //     color: "#333" 
// // //   },
// // //   modeIndicator: { 
// // //     margin: "4px 0 0 0", 
// // //     fontSize: "0.85rem", 
// // //     color: "#4caf50", 
// // //     fontWeight: "500" 
// // //   },
// // //   statusContainer: { 
// // //     display: "flex", 
// // //     gap: "0.5rem" 
// // //   },
// // //   statusIndicator: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#e8f5e9", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px", 
// // //     fontWeight: "500" 
// // //   },
// // //   statusIndicatorGray: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#f5f5f5", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px" 
// // //   },
// // //   statusIndicatorOff: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#fff3e0", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px" 
// // //   },
// // //   greenDot: { 
// // //     color: "#4caf50", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   grayDot: { 
// // //     color: "#999", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   yellowDot: { 
// // //     color: "#ff9800", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   chatBox: { 
// // //     border: "1px solid #ddd", 
// // //     borderRadius: "12px", 
// // //     flex: 1,
// // //     overflowY: "auto", 
// // //     padding: "24px", 
// // //     marginBottom: "15px", 
// // //     backgroundColor: "#fafafa",
// // //     minHeight: 0
// // //   },
// // //   emptyState: { 
// // //     textAlign: "center", 
// // //     padding: "4rem 2rem", 
// // //     color: "#666" 
// // //   },
// // //   emptyHint: { 
// // //     fontSize: "0.9rem", 
// // //     color: "#999", 
// // //     marginTop: "0.5rem" 
// // //   },
// // //   message: { 
// // //     padding: "14px 18px", 
// // //     marginBottom: "14px", 
// // //     borderRadius: "12px", 
// // //     maxWidth: "85%", 
// // //     wordWrap: "break-word", 
// // //     lineHeight: "1.6",
// // //     fontSize: "0.95rem",
// // //     minWidth: "300px"
// // //   },
// // //   userMessage: { 
// // //     backgroundColor: "#667eea", 
// // //     color: "white", 
// // //     marginLeft: "auto", 
// // //     borderBottomRightRadius: "4px",
// // //     maxWidth: "70%"
// // //   },
// // //   botMessage: { 
// // //     backgroundColor: "white", 
// // //     color: "#333", 
// // //     border: "1px solid #e0e0e0", 
// // //     borderBottomLeftRadius: "4px",
// // //     maxWidth: "85%"
// // //   },
// // //   systemMessage: { 
// // //     backgroundColor: "#fff3cd", 
// // //     color: "#856404", 
// // //     border: "1px solid #ffc107", 
// // //     textAlign: "center", 
// // //     margin: "1rem auto", 
// // //     maxWidth: "85%",
// // //     fontSize: "0.9rem"
// // //   },
// // //   agentBadge: { 
// // //     display: "inline-block", 
// // //     background: "#4caf50", 
// // //     color: "white", 
// // //     padding: "3px 10px", 
// // //     borderRadius: "12px", 
// // //     fontSize: "0.75rem", 
// // //     fontWeight: "600", 
// // //     marginBottom: "6px" 
// // //   },
// // //   timestamp: { 
// // //     fontSize: "0.7rem", 
// // //     color: "#999", 
// // //     marginTop: "6px" 
// // //   },
// // //   loadingMessage: { 
// // //     backgroundColor: "white", 
// // //     color: "#666", 
// // //     padding: "12px 16px", 
// // //     borderRadius: "12px", 
// // //     maxWidth: "75px", 
// // //     border: "1px solid #e0e0e0" 
// // //   },
// // //   typingDots: { 
// // //     display: "flex", 
// // //     gap: "4px", 
// // //     fontSize: "1.5rem" 
// // //   },
// // //   inputArea: { 
// // //     display: "flex", 
// // //     gap: "12px",
// // //     padding: "8px 0"
// // //   },
// // //   input: { 
// // //     flex: 1, 
// // //     padding: "14px 18px", 
// // //     border: "2px solid #ddd", 
// // //     borderRadius: "10px", 
// // //     fontSize: "1rem", 
// // //     outline: "none", 
// // //     transition: "border-color 0.2s",
// // //     fontFamily: "'Inter', sans-serif"
// // //   },
// // //   sendButton: { 
// // //     padding: "14px 40px", 
// // //     backgroundColor: "#667eea", 
// // //     color: "white", 
// // //     border: "none", 
// // //     borderRadius: "10px", 
// // //     cursor: "pointer", 
// // //     fontSize: "1rem", 
// // //     fontWeight: "600", 
// // //     transition: "all 0.2s",
// // //     minWidth: "120px"
// // //   },
// // //   sendButtonDisabled: { 
// // //     backgroundColor: "#ccc", 
// // //     cursor: "not-allowed" 
// // //   },
// // //   orderCardsContainer: {
// // //     display: "grid",
// // //     gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
// // //     gap: "1.25rem",
// // //     marginTop: "0.75rem",
// // //     marginBottom: "1rem",
// // //     width: "100%"
// // //   },
// // //   orderCard: {
// // //     backgroundColor: "white",
// // //     border: "2px solid #e0e0e0",
// // //     borderRadius: "12px",
// // //     padding: "1.25rem",
// // //     cursor: "pointer",
// // //     transition: "all 0.3s ease",
// // //     boxShadow: "0 2px 6px rgba(0,0,0,0.08)"
// // //   },
// // //   orderHeader: {
// // //     display: "flex",
// // //     justifyContent: "space-between",
// // //     alignItems: "flex-start",
// // //     marginBottom: "0.875rem"
// // //   },
// // //   orderRestaurant: {
// // //     fontWeight: "600",
// // //     fontSize: "1.05rem",
// // //     color: "#333",
// // //     flex: 1
// // //   },
// // //   orderStatus: {
// // //     padding: "0.35rem 0.65rem",
// // //     borderRadius: "6px",
// // //     fontSize: "0.8rem",
// // //     fontWeight: "600",
// // //     color: "white",
// // //     whiteSpace: "nowrap",
// // //     marginLeft: "0.75rem"
// // //   },
// // //   orderItems: {
// // //     fontSize: "0.9rem",
// // //     color: "#666",
// // //     marginBottom: "0.875rem",
// // //     lineHeight: "1.5"
// // //   },
// // //   orderDetails: {
// // //     display: "flex",
// // //     flexDirection: "column",
// // //     gap: "0.35rem",
// // //     marginBottom: "0.875rem",
// // //     fontSize: "0.85rem",
// // //     color: "#555"
// // //   },
// // //   orderDetailRow: {
// // //     display: "flex",
// // //     alignItems: "center"
// // //   },
// // //   orderTotal: {
// // //     fontWeight: "700",
// // //     fontSize: "0.95rem",
// // //     color: "#333"
// // //   },
// // //   orderFooter: {
// // //     fontSize: "0.8rem",
// // //     color: "#999",
// // //     borderTop: "1px solid #f0f0f0",
// // //     paddingTop: "0.65rem",
// // //     marginTop: "0.65rem"
// // //   },
// // //   clickHint: {
// // //     fontSize: "0.75rem",
// // //     color: "#667eea",
// // //     textAlign: "center",
// // //     marginTop: "0.65rem",
// // //     fontStyle: "italic"
// // //   }
// // // };

// // // export default ChatWindow

// // // import React, { useState, useEffect, useRef } from "react";
// // // import EscalationButton from './EscalationButton';
// // // import FeedbackModal from './FeedbackModal';
// // // import API_BASE_URL, { WS_BASE_URL } from "./config"; // ADDED IMPORTS

// // // function ChatWindow({ token, onLogout }) {
// // //   const [messages, setMessages] = useState([]);
// // //   const [input, setInput] = useState("");
// // //   const [loading, setLoading] = useState(false);
// // //   const [escalationId, setEscalationId] = useState(null);
// // //   const [wsConnected, setWsConnected] = useState(false);
// // //   const [userInfo, setUserInfo] = useState(null);
// // //   const [showFeedbackModal, setShowFeedbackModal] = useState(false);
// // //   const [currentSessionId, setCurrentSessionId] = useState(null);
// // //   const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
// // //   const [isLoggingOut, setIsLoggingOut] = useState(false);

// // //   const wsRef = useRef(null);
// // //   const messagesEndRef = useRef(null);
// // //   const escalationIdRef = useRef(null);
// // //   const heartbeatIntervalRef = useRef(null);
// // //   const feedbackCheckTimeoutRef = useRef(null);

// // //   useEffect(() => {
// // //     escalationIdRef.current = escalationId;
// // //   }, [escalationId]);

// // //   useEffect(() => {
// // //     fetchUserInfo();
// // //     checkForExistingEscalation();

// // //     return () => {
// // //       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// // //       if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
// // //       if (wsRef.current) wsRef.current.close();
// // //     };
// // //   }, [token]);

// // //   useEffect(() => scrollToBottom(), [messages]);

// // //   useEffect(() => {
// // //     if (userInfo?.user_id && !wsConnected && !wsRef.current) {
// // //       connectWebSocket(userInfo.user_id);
// // //     }
// // //   }, [userInfo]);

// // //   // FIXED: Only check feedback when bot sends a goodbye message
// // //   useEffect(() => {
// // //     if (messages.length > 0 && !escalationId && !feedbackSubmitted && !isLoggingOut) {
// // //       const lastMsg = messages[messages.length - 1];
      
// // //       // Only trigger on specific bot goodbye messages
// // //       if (lastMsg.sender === "bot") {
// // //         const botText = lastMsg.text.toLowerCase();
        
// // //         // Check if bot is ending the conversation
// // //         const goodbyePatterns = [
// // //           "welcome", "have a great day", "have a good day", 
// // //           "glad to help", "happy to help", "pleasure helping",
// // //           "if you need anything", "feel free to reach out"
// // //         ];
        
// // //         const isGoodbyeMessage = goodbyePatterns.some(pattern => botText.includes(pattern));
        
// // //         if (isGoodbyeMessage) {
// // //           console.log("✅ Bot sent goodbye, checking feedback in 2 seconds...");
          
// // //           // Clear any existing timeout
// // //           if (feedbackCheckTimeoutRef.current) {
// // //             clearTimeout(feedbackCheckTimeoutRef.current);
// // //           }
          
// // //           // Set new timeout
// // //           feedbackCheckTimeoutRef.current = setTimeout(() => {
// // //             checkFeedbackPrompt();
// // //           }, 2000);
// // //         }
// // //       }
// // //     }
    
// // //     // Cleanup on unmount
// // //     return () => {
// // //       if (feedbackCheckTimeoutRef.current) {
// // //         clearTimeout(feedbackCheckTimeoutRef.current);
// // //       }
// // //     };
// // //   }, [messages, escalationId, feedbackSubmitted, isLoggingOut]);

// // //   const fetchUserInfo = async () => {
// // //     try {
// // //       const response = await fetch(`${API_BASE_URL}/auth/me`, { // REPLACED URL
// // //         headers: { Authorization: `Bearer ${token}` },
// // //       });
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         console.log("✅ User info loaded:", data);
// // //         setUserInfo(data);
// // //       }
// // //     } catch (error) {
// // //       console.error("❌ Error fetching user info:", error);
// // //     }
// // //   };

// // //   const checkForExistingEscalation = async () => {
// // //     try {
// // //       const response = await fetch(`${API_BASE_URL}/escalation/escalations/my`, { // REPLACED URL
// // //         headers: { Authorization: `Bearer ${token}` },
// // //       });
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         const activeEscalation = data.escalations?.find(
// // //           esc => esc.status !== 'resolved' && esc.status !== 'closed'
// // //         );
// // //         if (activeEscalation) {
// // //           setEscalationId(activeEscalation.escalation_id);
// // //           escalationIdRef.current = activeEscalation.escalation_id;
// // //           await loadEscalationHistory(activeEscalation.escalation_id);
// // //           setMessages(prev => [...prev, {
// // //             sender: "system",
// // //             text: `Resuming your support session (Case #${activeEscalation.escalation_id.slice(0, 8)})`,
// // //             timestamp: new Date().toISOString()
// // //           }]);
// // //         }
// // //       }
// // //     } catch (error) {
// // //       console.error("Error checking for existing escalations:", error);
// // //     }
// // //   };

// // //   const loadEscalationHistory = async (escId) => {
// // //     try {
// // //       const response = await fetch(
// // //         `${API_BASE_URL}/escalation/messages/${escId}`, // REPLACED URL
// // //         { headers: { Authorization: `Bearer ${token}` } }
// // //       );
      
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         const formattedMessages = data.messages.map(msg => ({
// // //           sender: msg.sender === 'user' ? 'user' : 'bot',
// // //           text: msg.message,
// // //           timestamp: msg.timestamp,
// // //           isAgent: msg.sender === 'agent'
// // //         }));
// // //         setMessages(formattedMessages);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error loading escalation history:", error);
// // //     }
// // //   };

// // //   const checkFeedbackPrompt = async () => {
// // //     if (!userInfo?.user_id || feedbackSubmitted || escalationId || isLoggingOut) {
// // //       console.log("⏭️ Feedback check skipped:", { 
// // //         hasUser: !!userInfo?.user_id, 
// // //         feedbackSubmitted, 
// // //         escalationId,
// // //         isLoggingOut
// // //       });
// // //       return;
// // //     }
    
// // //     console.log("🔍 Checking for feedback prompt for user:", userInfo.user_id);
    
// // //     try {
// // //       const response = await fetch(
// // //         `${API_BASE_URL}/feedback/check-prompt/${userInfo.user_id}`, // REPLACED URL
// // //         { headers: { Authorization: `Bearer ${token}` } }
// // //       );
      
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         console.log("📋 Feedback prompt response:", data);
        
// // //         if (data.should_ask && data.session_id && !isLoggingOut) {
// // //           console.log("✅ Showing feedback modal!");
// // //           setCurrentSessionId(data.session_id);
// // //           setShowFeedbackModal(true);
// // //         } else {
// // //           console.log("⏳ Not time for feedback yet");
// // //         }
// // //       } else {
// // //         console.error("❌ Feedback check failed with status:", response.status);
// // //       }
// // //     } catch (error) {
// // //       console.error("❌ Error checking feedback prompt:", error);
// // //     }
// // //   };

// // //   const handleFeedbackSubmit = async (feedbackData) => {
// // //     try {
// // //       const response = await fetch(`${API_BASE_URL}/feedback/submit`, { // REPLACED URL
// // //         method: "POST",
// // //         headers: {
// // //           "Content-Type": "application/json",
// // //           Authorization: `Bearer ${token}`
// // //         },
// // //         body: JSON.stringify(feedbackData)
// // //       });
      
// // //       if (response.ok) {
// // //         console.log("✅ Feedback submitted successfully!");
// // //         setShowFeedbackModal(false);
// // //         setFeedbackSubmitted(true);
// // //         setMessages(prev => [...prev, {
// // //           sender: "system",
// // //           text: "Thank you for your feedback! We appreciate your input.",
// // //           timestamp: new Date().toISOString()
// // //         }]);
// // //       } else {
// // //         alert("Failed to submit feedback. Please try again.");
// // //       }
// // //     } catch (error) {
// // //       console.error("Error submitting feedback:", error);
// // //       alert("Connection error. Please try again.");
// // //     }
// // //   };

// // //   const handleFeedbackClose = () => {
// // //     console.log("🚪 Feedback modal closed");
// // //     setShowFeedbackModal(false);
    
// // //     // If user was trying to logout, proceed with logout
// // //     if (isLoggingOut) {
// // //       console.log("🔄 Proceeding with logout after feedback close");
// // //       proceedWithLogout();
// // //     }
// // //   };

// // //   const handleLogoutClick = () => {
// // //     console.log("🚪 Logout clicked");
    
// // //     // If feedback modal is open, just set logging out flag
// // //     if (showFeedbackModal) {
// // //       console.log("⚠️ Feedback modal is open, setting logout flag");
// // //       setIsLoggingOut(true);
// // //       setShowFeedbackModal(false); // Close feedback modal
// // //       return;
// // //     }
    
// // //     // Otherwise logout directly
// // //     proceedWithLogout();
// // //   };

// // //   const proceedWithLogout = () => {
// // //     console.log("✅ Proceeding with logout");
    
// // //     // Clear all timeouts
// // //     if (feedbackCheckTimeoutRef.current) {
// // //       clearTimeout(feedbackCheckTimeoutRef.current);
// // //     }
// // //     if (heartbeatIntervalRef.current) {
// // //       clearInterval(heartbeatIntervalRef.current);
// // //     }
    
// // //     // Close WebSocket
// // //     if (wsRef.current) {
// // //       wsRef.current.close();
// // //     }
    
// // //     // Call parent logout
// // //     if (onLogout) {
// // //       onLogout();
// // //     }
// // //   };

// // //   const connectWebSocket = (userId) => {
// // //     if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) return;
// // //     if (wsRef.current) wsRef.current.close();

// // //     const ws = new WebSocket(`${WS_BASE_URL}/escalation/ws/user/${userId}`); // REPLACED URL with WS_BASE_URL

// // //     ws.onopen = () => {
// // //       setWsConnected(true);
// // //       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// // //       heartbeatIntervalRef.current = setInterval(() => {
// // //         if (ws.readyState === WebSocket.OPEN) {
// // //           ws.send(JSON.stringify({ type: 'ping' }));
// // //         }
// // //       }, 30000);
// // //     };

// // //     ws.onmessage = (event) => {
// // //       try {
// // //         const data = JSON.parse(event.data);
// // //         if (data.type === 'ping') {
// // //           ws.send(JSON.stringify({ type: 'pong' }));
// // //           return;
// // //         }
// // //         if (data.type === 'agent_message') {
// // //           setMessages(prev => [...prev, {
// // //             sender: "bot",
// // //             text: data.message,
// // //             timestamp: data.timestamp,
// // //             isAgent: true
// // //           }]);
// // //         } else if (data.type === 'error') {
// // //           setMessages(prev => [...prev, {
// // //             sender: "system",
// // //             text: `Error: ${data.message}`,
// // //             timestamp: new Date().toISOString()
// // //           }]);
// // //         }
// // //       } catch (error) {
// // //         console.error("Error parsing WebSocket message:", error);
// // //       }
// // //     };

// // //     ws.onerror = () => setWsConnected(false);

// // //     ws.onclose = (event) => {
// // //       setWsConnected(false);
// // //       wsRef.current = null;
// // //       if (heartbeatIntervalRef.current) {
// // //         clearInterval(heartbeatIntervalRef.current);
// // //         heartbeatIntervalRef.current = null;
// // //       }
// // //       if (event.code !== 1000 && userInfo?.user_id && !isLoggingOut) {
// // //         setTimeout(() => connectWebSocket(userInfo.user_id), 3000);
// // //       }
// // //     };

// // //     wsRef.current = ws;
// // //   };

// // //   const handleEscalationCreated = async (escId) => {
// // //     if (escalationIdRef.current && escalationIdRef.current !== escId) {
// // //       alert("You already have an active support session. Continue chatting here.");
// // //       return;
// // //     }
// // //     setEscalationId(escId);
// // //     escalationIdRef.current = escId;
// // //     if (userInfo?.user_id && !wsConnected) connectWebSocket(userInfo.user_id);
// // //     if (!escalationId) {
// // //       setMessages(prev => [...prev, {
// // //         sender: "system",
// // //         text: "You've been connected to a live support agent. They will assist you shortly.",
// // //         timestamp: new Date().toISOString()
// // //       }]);
// // //     }
// // //   };

// // //   const handleOrderClick = async (orderId) => {
// // //     setMessages(prev => [...prev, { 
// // //       sender: "user", 
// // //       text: orderId, 
// // //       timestamp: new Date().toISOString() 
// // //     }]);

// // //     setLoading(true);
// // //     try {
// // //       const res = await fetch(`${API_BASE_URL}/chat`, { // REPLACED URL
// // //         method: "POST",
// // //         headers: { 
// // //           "Content-Type": "application/json", 
// // //           Authorization: `Bearer ${token}` 
// // //         },
// // //         body: JSON.stringify({ message: orderId }),
// // //       });
      
// // //       if (res.ok) {
// // //         const data = await res.json();
// // //         setMessages(prev => [...prev, { 
// // //           sender: "bot", 
// // //           text: data.reply, 
// // //           timestamp: new Date().toISOString() 
// // //         }]);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error fetching order details:", error);
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   const sendMessage = async () => {
// // //     if (!input.trim()) return;
    
// // //     const userMessage = input.trim();
// // //     setInput("");
// // //     setMessages(prev => [...prev, { 
// // //       sender: "user", 
// // //       text: userMessage, 
// // //       timestamp: new Date().toISOString() 
// // //     }]);

// // //     const currentEscalationId = escalationIdRef.current;

// // //     if (currentEscalationId) {
// // //       if (wsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
// // //         wsRef.current.send(JSON.stringify({ 
// // //           type: "message", 
// // //           escalation_id: currentEscalationId, 
// // //           message: userMessage 
// // //         }));
// // //       } else {
// // //         if (userInfo?.user_id) connectWebSocket(userInfo.user_id);
// // //         setMessages(prev => [...prev, {
// // //           sender: "system",
// // //           text: "Connecting to support agent...",
// // //           timestamp: new Date().toISOString()
// // //         }]);
// // //       }
// // //       return;
// // //     }

// // //     setLoading(true);
// // //     try {
// // //       const res = await fetch(`${API_BASE_URL}/chat`, { // REPLACED URL
// // //         method: "POST",
// // //         headers: { 
// // //           "Content-Type": "application/json", 
// // //           Authorization: `Bearer ${token}` 
// // //         },
// // //         body: JSON.stringify({ message: userMessage }),
// // //       });
      
// // //       if (res.ok) {
// // //         const data = await res.json();
        
// // //         if (data.reply === "ORDER_LIST" && data.orders && Array.isArray(data.orders)) {
// // //           setMessages(prev => [...prev, { 
// // //             sender: "bot", 
// // //             text: "Here are your recent orders:",
// // //             orders: data.orders,
// // //             timestamp: new Date().toISOString() 
// // //           }]);
// // //         } else {
// // //           setMessages(prev => [...prev, { 
// // //             sender: "bot", 
// // //             text: data.reply, 
// // //             timestamp: new Date().toISOString() 
// // //           }]);

// // //           const escMatch = data.reply.match(/ESC_\d+/);
// // //           if (escMatch) {
// // //             const foundEscId = escMatch[0];
// // //             setEscalationId(foundEscId);
// // //             escalationIdRef.current = foundEscId;
// // //             if (userInfo?.user_id && (!wsConnected || wsRef.current.readyState !== WebSocket.OPEN)) {
// // //               connectWebSocket(userInfo.user_id);
// // //             }
// // //             setMessages(prev => [...prev, {
// // //               sender: "system",
// // //               text: "You are now connected to live support.",
// // //               timestamp: new Date().toISOString()
// // //             }]);
// // //           }
// // //         }
// // //       } else {
// // //         setMessages(prev => [...prev, { 
// // //           sender: "bot", 
// // //           text: "Sorry, an error occurred. Please try again.", 
// // //           timestamp: new Date().toISOString() 
// // //         }]);
// // //       }
// // //     } catch (error) {
// // //       console.error("Send message error:", error);
// // //       setMessages(prev => [...prev, { 
// // //         sender: "bot", 
// // //         text: "Connection error. Check your internet.", 
// // //         timestamp: new Date().toISOString() 
// // //       }]);
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   const scrollToBottom = () => {
// // //     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
// // //   };

// // //   const getStatusColor = (status) => {
// // //     const s = status.toLowerCase();
// // //     if (s.includes('delivered')) return '#4caf50';
// // //     if (s.includes('delivery')) return '#2196f3';
// // //     if (s.includes('preparing') || s.includes('processing')) return '#ff9800';
// // //     if (s.includes('cancelled')) return '#f44336';
// // //     return '#757575';
// // //   };

// // //   const getStatusEmoji = (status) => {
// // //     const s = status.toLowerCase();
// // //     if (s.includes('delivered')) return '✓';
// // //     if (s.includes('delivery')) return '🚚';
// // //     if (s.includes('preparing') || s.includes('processing')) return '🍳';
// // //     if (s.includes('ready')) return '✅';
// // //     if (s.includes('cancelled')) return '✗';
// // //     return '📦';
// // //   };

// // //   return (
// // //     <div style={styles.container}>
// // //       <div style={styles.header}>
// // //         <div>
// // //           <h2 style={styles.title}>
// // //             {escalationId ? "Live Agent Support" : "AI Support Assistant"}
// // //           </h2>
// // //           {escalationId && (
// // //             <p style={styles.modeIndicator}>
// // //               You are now chatting with a human support agent
// // //             </p>
// // //           )}
// // //         </div>
// // //         <div style={styles.statusContainer}>
// // //           {wsConnected && escalationId && (
// // //             <span style={styles.statusIndicator}>
// // //               <span style={styles.greenDot}>●</span> Agent Online
// // //             </span>
// // //           )}
// // //           {wsConnected && !escalationId && (
// // //             <span style={styles.statusIndicatorGray}>
// // //               <span style={styles.grayDot}>●</span> Ready
// // //             </span>
// // //           )}
// // //           {!wsConnected && userInfo && (
// // //             <span style={styles.statusIndicatorOff}>
// // //               <span style={styles.yellowDot}>●</span> Connecting...
// // //             </span>
// // //           )}
// // //         </div>
// // //       </div>

// // //       <EscalationButton token={token} onEscalationCreated={handleEscalationCreated} />

// // //       <div style={styles.chatBox}>
// // //         {messages.length === 0 && (
// // //           <div style={styles.emptyState}>
// // //             <p>Hello! How can I help you today?</p>
// // //             <p style={styles.emptyHint}>
// // //               Ask about orders, deliveries, refunds, or any issues you're experiencing.
// // //             </p>
// // //           </div>
// // //         )}
        
// // //         {messages.map((msg, i) => (
// // //           <div key={i}>
// // //             <div 
// // //               style={{
// // //                 ...styles.message,
// // //                 ...(msg.sender === "user" 
// // //                   ? styles.userMessage 
// // //                   : msg.sender === "system" 
// // //                   ? styles.systemMessage 
// // //                   : styles.botMessage)
// // //               }}
// // //             >
// // //               {msg.isAgent && <span style={styles.agentBadge}>Agent</span>}
// // //               <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
// // //               {msg.timestamp && (
// // //                 <div style={styles.timestamp}>
// // //                   {new Date(msg.timestamp).toLocaleTimeString()}
// // //                 </div>
// // //               )}
// // //             </div>

// // //             {msg.orders && msg.orders.length > 0 && (
// // //               <div style={styles.orderCardsContainer}>
// // //                 {msg.orders.map((order, idx) => (
// // //                   <div 
// // //                     key={idx} 
// // //                     style={styles.orderCard}
// // //                     onClick={() => handleOrderClick(order.order_id)}
// // //                     onMouseEnter={(e) => {
// // //                       e.currentTarget.style.transform = 'translateY(-2px)';
// // //                       e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.15)';
// // //                       e.currentTarget.style.borderColor = '#667eea';
// // //                     }}
// // //                     onMouseLeave={(e) => {
// // //                       e.currentTarget.style.transform = 'translateY(0)';
// // //                       e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
// // //                       e.currentTarget.style.borderColor = '#e0e0e0';
// // //                     }}
// // //                   >
// // //                     <div style={styles.orderHeader}>
// // //                       <div style={styles.orderRestaurant}>
// // //                         🍽️ {order.restaurant}
// // //                       </div>
// // //                       <div 
// // //                         style={{
// // //                           ...styles.orderStatus,
// // //                           backgroundColor: getStatusColor(order.status)
// // //                         }}
// // //                       >
// // //                         {getStatusEmoji(order.status)} {order.status}
// // //                       </div>
// // //                     </div>

// // //                     <div style={styles.orderItems}>
// // //                       <strong>Items:</strong> {order.items.slice(0, 3).join(', ')}
// // //                       {order.items.length > 3 && ` +${order.items.length - 3} more`}
// // //                     </div>

// // //                     <div style={styles.orderDetails}>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span>📅 {order.order_date}</span>
// // //                       </div>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span>📍 {order.delivery_address}</span>
// // //                       </div>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span style={styles.orderTotal}>💵 ${order.total_amount}</span>
// // //                       </div>
// // //                     </div>

// // //                     <div style={styles.orderFooter}>
// // //                       Order ID: {order.order_id.slice(0, 8)}...
// // //                     </div>

// // //                     <div style={styles.clickHint}>
// // //                       Click to view full details
// // //                     </div>
// // //                   </div>
// // //                 ))}
// // //               </div>
// // //             )}
// // //           </div>
// // //         ))}
        
// // //         {loading && (
// // //           <div style={styles.loadingMessage}>
// // //             <div style={styles.typingDots}>
// // //               <span>.</span><span>.</span><span>.</span>
// // //             </div>
// // //           </div>
// // //         )}
        
// // //         <div ref={messagesEndRef} />
// // //       </div>

// // //       <div style={styles.inputArea}>
// // //         <input
// // //           type="text"
// // //           value={input}
// // //           onChange={e => setInput(e.target.value)}
// // //           onKeyDown={e => e.key === "Enter" && !loading && sendMessage()}
// // //           placeholder={
// // //             escalationId && wsConnected 
// // //               ? "Message the agent..." 
// // //               : escalationId && !wsConnected 
// // //               ? "Connecting to agent..." 
// // //               : "Type your message..."
// // //           }
// // //           disabled={loading || (escalationId && !wsConnected)}
// // //           style={styles.input}
// // //         />
// // //         <button 
// // //           onClick={sendMessage} 
// // //           disabled={loading || !input.trim() || (escalationId && !wsConnected)} 
// // //           style={{
// // //             ...styles.sendButton,
// // //             ...(loading || !input.trim() || (escalationId && !wsConnected) 
// // //               ? styles.sendButtonDisabled 
// // //               : {})
// // //           }}
// // //         >
// // //           {loading ? "..." : "Send"}
// // //         </button>
// // //       </div>

// // //       <FeedbackModal
// // //         show={showFeedbackModal}
// // //         onClose={handleFeedbackClose}
// // //         onSubmit={handleFeedbackSubmit}
// // //         sessionId={currentSessionId}
// // //       />
// // //     </div>
// // //   );
// // // }

// // // const styles = {
// // //   container: { 
// // //     maxWidth: "1200px", 
// // //     margin: "0 auto", 
// // //     padding: "20px", 
// // //     fontFamily: "'Inter', sans-serif",
// // //     height: "calc(100vh - 40px)",
// // //     display: "flex",
// // //     flexDirection: "column"
// // //   },
// // //   header: { 
// // //     display: "flex", 
// // //     justifyContent: "space-between", 
// // //     alignItems: "center", 
// // //     marginBottom: "15px",
// // //     paddingBottom: "15px",
// // //     borderBottom: "2px solid #e0e0e0"
// // //   },
// // //   title: { 
// // //     margin: 0, 
// // //     fontSize: "1.5rem", 
// // //     color: "#333" 
// // //   },
// // //   modeIndicator: { 
// // //     margin: "4px 0 0 0", 
// // //     fontSize: "0.85rem", 
// // //     color: "#4caf50", 
// // //     fontWeight: "500" 
// // //   },
// // //   statusContainer: { 
// // //     display: "flex", 
// // //     gap: "0.5rem" 
// // //   },
// // //   statusIndicator: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#e8f5e9", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px", 
// // //     fontWeight: "500" 
// // //   },
// // //   statusIndicatorGray: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#f5f5f5", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px" 
// // //   },
// // //   statusIndicatorOff: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#fff3e0", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px" 
// // //   },
// // //   greenDot: { 
// // //     color: "#4caf50", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   grayDot: { 
// // //     color: "#999", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   yellowDot: { 
// // //     color: "#ff9800", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   chatBox: { 
// // //     border: "1px solid #ddd", 
// // //     borderRadius: "12px", 
// // //     flex: 1,
// // //     overflowY: "auto", 
// // //     padding: "24px", 
// // //     marginBottom: "15px", 
// // //     backgroundColor: "#fafafa",
// // //     minHeight: 0
// // //   },
// // //   emptyState: { 
// // //     textAlign: "center", 
// // //     padding: "4rem 2rem", 
// // //     color: "#666" 
// // //   },
// // //   emptyHint: { 
// // //     fontSize: "0.9rem", 
// // //     color: "#999", 
// // //     marginTop: "0.5rem" 
// // //   },
// // //   message: { 
// // //     padding: "14px 18px", 
// // //     marginBottom: "14px", 
// // //     borderRadius: "12px", 
// // //     maxWidth: "85%", 
// // //     wordWrap: "break-word", 
// // //     lineHeight: "1.6",
// // //     fontSize: "0.95rem",
// // //     minWidth: "300px"
// // //   },
// // //   userMessage: { 
// // //     backgroundColor: "#667eea", 
// // //     color: "white", 
// // //     marginLeft: "auto", 
// // //     borderBottomRightRadius: "4px",
// // //     maxWidth: "70%"
// // //   },
// // //   botMessage: { 
// // //     backgroundColor: "white", 
// // //     color: "#333", 
// // //     border: "1px solid #e0e0e0", 
// // //     borderBottomLeftRadius: "4px",
// // //     maxWidth: "85%"
// // //   },
// // //   systemMessage: { 
// // //     backgroundColor: "#fff3cd", 
// // //     color: "#856404", 
// // //     border: "1px solid #ffc107", 
// // //     textAlign: "center", 
// // //     margin: "1rem auto", 
// // //     maxWidth: "85%",
// // //     fontSize: "0.9rem"
// // //   },
// // //   agentBadge: { 
// // //     display: "inline-block", 
// // //     background: "#4caf50", 
// // //     color: "white", 
// // //     padding: "3px 10px", 
// // //     borderRadius: "12px", 
// // //     fontSize: "0.75rem", 
// // //     fontWeight: "600", 
// // //     marginBottom: "6px" 
// // //   },
// // //   timestamp: { 
// // //     fontSize: "0.7rem", 
// // //     color: "#999", 
// // //     marginTop: "6px" 
// // //   },
// // //   loadingMessage: { 
// // //     backgroundColor: "white", 
// // //     color: "#666", 
// // //     padding: "12px 16px", 
// // //     borderRadius: "12px", 
// // //     maxWidth: "75px", 
// // //     border: "1px solid #e0e0e0" 
// // //   },
// // //   typingDots: { 
// // //     display: "flex", 
// // //     gap: "4px", 
// // //     fontSize: "1.5rem" 
// // //   },
// // //   inputArea: { 
// // //     display: "flex", 
// // //     gap: "12px",
// // //     padding: "8px 0"
// // //   },
// // //   input: { 
// // //     flex: 1, 
// // //     padding: "14px 18px", 
// // //     border: "2px solid #ddd", 
// // //     borderRadius: "10px", 
// // //     fontSize: "1rem", 
// // //     outline: "none", 
// // //     transition: "border-color 0.2s",
// // //     fontFamily: "'Inter', sans-serif"
// // //   },
// // //   sendButton: { 
// // //     padding: "14px 40px", 
// // //     backgroundColor: "#667eea", 
// // //     color: "white", 
// // //     border: "none", 
// // //     borderRadius: "10px", 
// // //     cursor: "pointer", 
// // //     fontSize: "1rem", 
// // //     fontWeight: "600", 
// // //     transition: "all 0.2s",
// // //     minWidth: "120px"
// // //   },
// // //   sendButtonDisabled: { 
// // //     backgroundColor: "#ccc", 
// // //     cursor: "not-allowed" 
// // //   },
// // //   orderCardsContainer: {
// // //     display: "grid",
// // //     gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
// // //     gap: "1.25rem",
// // //     marginTop: "0.75rem",
// // //     marginBottom: "1rem",
// // //     width: "100%"
// // //   },
// // //   orderCard: {
// // //     backgroundColor: "white",
// // //     border: "2px solid #e0e0e0",
// // //     borderRadius: "12px",
// // //     padding: "1.25rem",
// // //     cursor: "pointer",
// // //     transition: "all 0.3s ease",
// // //     boxShadow: "0 2px 6px rgba(0,0,0,0.08)"
// // //   },
// // //   orderHeader: {
// // //     display: "flex",
// // //     justifyContent: "space-between",
// // //     alignItems: "flex-start",
// // //     marginBottom: "0.875rem"
// // //   },
// // //   orderRestaurant: {
// // //     fontWeight: "600",
// // //     fontSize: "1.05rem",
// // //     color: "#333",
// // //     flex: 1
// // //   },
// // //   orderStatus: {
// // //     padding: "0.35rem 0.65rem",
// // //     borderRadius: "6px",
// // //     fontSize: "0.8rem",
// // //     fontWeight: "600",
// // //     color: "white",
// // //     whiteSpace: "nowrap",
// // //     marginLeft: "0.75rem"
// // //   },
// // //   orderItems: {
// // //     fontSize: "0.9rem",
// // //     color: "#666",
// // //     marginBottom: "0.875rem",
// // //     lineHeight: "1.5"
// // //   },
// // //   orderDetails: {
// // //     display: "flex",
// // //     flexDirection: "column",
// // //     gap: "0.35rem",
// // //     marginBottom: "0.875rem",
// // //     fontSize: "0.85rem",
// // //     color: "#555"
// // //   },
// // //   orderDetailRow: {
// // //     display: "flex",
// // //     alignItems: "center"
// // //   },
// // //   orderTotal: {
// // //     fontWeight: "700",
// // //     fontSize: "0.95rem",
// // //     color: "#333"
// // //   },
// // //   orderFooter: {
// // //     fontSize: "0.8rem",
// // //     color: "#999",
// // //     borderTop: "1px solid #f0f0f0",
// // //     paddingTop: "0.65rem",
// // //     marginTop: "0.65rem"
// // //   },
// // //   clickHint: {
// // //     fontSize: "0.75rem",
// // //     color: "#667eea",
// // //     textAlign: "center",
// // //     marginTop: "0.65rem",
// // //     fontStyle: "italic"
// // //   }
// // // };

// // // export default ChatWindow


// // // import React, { useState, useEffect, useRef } from "react";
// // // import EscalationButton from './EscalationButton';
// // // import FeedbackModal from './FeedbackModal';
// // // import API_BASE_URL, { WS_BASE_URL } from "./config";

// // // function ChatWindow({ token, onLogout }) {
// // //   const [messages, setMessages] = useState([]);
// // //   const [input, setInput] = useState("");
// // //   const [loading, setLoading] = useState(false);
// // //   const [escalationId, setEscalationId] = useState(null);
// // //   const [wsConnected, setWsConnected] = useState(false);
// // //   const [userInfo, setUserInfo] = useState(null);
// // //   const [showFeedbackModal, setShowFeedbackModal] = useState(false);
// // //   const [currentSessionId, setCurrentSessionId] = useState(null);
// // //   const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
// // //   const [isLoggingOut, setIsLoggingOut] = useState(false);

// // //   const wsRef = useRef(null);
// // //   const messagesEndRef = useRef(null);
// // //   const escalationIdRef = useRef(null);
// // //   const heartbeatIntervalRef = useRef(null);
// // //   const feedbackCheckTimeoutRef = useRef(null);

// // //   useEffect(() => {
// // //     escalationIdRef.current = escalationId;
// // //   }, [escalationId]);

// // //   useEffect(() => {
// // //     fetchUserInfo();
// // //     checkForExistingEscalation();

// // //     return () => {
// // //       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// // //       if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
// // //       if (wsRef.current) wsRef.current.close();
// // //     };
// // //   }, [token]);

// // //   useEffect(() => scrollToBottom(), [messages]);

// // //   useEffect(() => {
// // //     if (userInfo?.user_id && !wsRef.current) {
// // //       connectWebSocket(userInfo.user_id);
// // //     }
// // //   }, [userInfo]);

// // //   useEffect(() => {
// // //     if (messages.length > 0 && !escalationId && !feedbackSubmitted && !isLoggingOut) {
// // //       const lastMsg = messages[messages.length - 1];
// // //       if (lastMsg.sender === "bot") {
// // //         const botText = lastMsg.text.toLowerCase();
// // //         const goodbyePatterns = [
// // //           "welcome", "have a great day", "have a good day", 
// // //           "glad to help", "happy to help", "pleasure helping",
// // //           "if you need anything", "feel free to reach out"
// // //         ];
// // //         const isGoodbyeMessage = goodbyePatterns.some(pattern => botText.includes(pattern));
// // //         if (isGoodbyeMessage) {
// // //           if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
// // //           feedbackCheckTimeoutRef.current = setTimeout(() => {
// // //             checkFeedbackPrompt();
// // //           }, 2000);
// // //         }
// // //       }
// // //     }
// // //     return () => {
// // //       if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
// // //     };
// // //   }, [messages, escalationId, feedbackSubmitted, isLoggingOut]);

// // //   const fetchUserInfo = async () => {
// // //     try {
// // //       const response = await fetch(`${API_BASE_URL}/auth/me`, {
// // //         headers: { Authorization: `Bearer ${token}` },
// // //       });
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         setUserInfo(data);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error fetching user info:", error);
// // //     }
// // //   };

// // //   const checkForExistingEscalation = async () => {
// // //     try {
// // //       const response = await fetch(`${API_BASE_URL}/escalation/escalations/my`, {
// // //         headers: { Authorization: `Bearer ${token}` },
// // //       });
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         const activeEscalation = data.escalations?.find(
// // //           esc => esc.status !== 'resolved' && esc.status !== 'closed'
// // //         );
// // //         if (activeEscalation) {
// // //           setEscalationId(activeEscalation.escalation_id);
// // //           await loadEscalationHistory(activeEscalation.escalation_id);
// // //           setMessages(prev => [...prev, {
// // //             sender: "system",
// // //             text: `Resuming your support session (Case #${activeEscalation.escalation_id.slice(0, 8)})`,
// // //             timestamp: new Date().toISOString()
// // //           }]);
// // //         }
// // //       }
// // //     } catch (error) {
// // //       console.error("Error checking for existing escalations:", error);
// // //     }
// // //   };

// // //   const loadEscalationHistory = async (escId) => {
// // //     try {
// // //       const response = await fetch(
// // //         `${API_BASE_URL}/escalation/messages/${escId}`,
// // //         { headers: { Authorization: `Bearer ${token}` } }
// // //       );
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         const formattedMessages = data.messages.map(msg => ({
// // //           sender: msg.sender === 'user' ? 'user' : 'bot',
// // //           text: msg.message,
// // //           timestamp: msg.timestamp,
// // //           isAgent: msg.sender === 'agent'
// // //         }));
// // //         setMessages(formattedMessages);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error loading escalation history:", error);
// // //     }
// // //   };

// // //   const checkFeedbackPrompt = async () => {
// // //     if (!userInfo?.user_id || feedbackSubmitted || escalationId || isLoggingOut) {
// // //       return;
// // //     }
// // //     try {
// // //       const response = await fetch(
// // //         `${API_BASE_URL}/feedback/check-prompt/${userInfo.user_id}`,
// // //         { headers: { Authorization: `Bearer ${token}` } }
// // //       );
// // //       if (response.ok) {
// // //         const data = await response.json();
// // //         if (data.should_ask && data.session_id && !isLoggingOut) {
// // //           setCurrentSessionId(data.session_id);
// // //           setShowFeedbackModal(true);
// // //         }
// // //       }
// // //     } catch (error) {
// // //       console.error("Error checking feedback prompt:", error);
// // //     }
// // //   };

// // //   const handleFeedbackSubmit = async (feedbackData) => {
// // //     try {
// // //       const response = await fetch(`${API_BASE_URL}/feedback/submit`, {
// // //         method: "POST",
// // //         headers: {
// // //           "Content-Type": "application/json",
// // //           Authorization: `Bearer ${token}`
// // //         },
// // //         body: JSON.stringify(feedbackData)
// // //       });
// // //       if (response.ok) {
// // //         setShowFeedbackModal(false);
// // //         setFeedbackSubmitted(true);
// // //         setMessages(prev => [...prev, {
// // //           sender: "system",
// // //           text: "Thank you for your feedback!",
// // //           timestamp: new Date().toISOString()
// // //         }]);
// // //       } else {
// // //         alert("Failed to submit feedback.");
// // //       }
// // //     } catch (error) {
// // //       alert("Connection error.");
// // //     }
// // //   };

// // //   const handleFeedbackClose = () => {
// // //     setShowFeedbackModal(false);
// // //     if (isLoggingOut) {
// // //       proceedWithLogout();
// // //     }
// // //   };

// // //   const handleLogoutClick = () => {
// // //     if (showFeedbackModal) {
// // //       setIsLoggingOut(true);
// // //       setShowFeedbackModal(false);
// // //       return;
// // //     }
// // //     proceedWithLogout();
// // //   };

// // //   const proceedWithLogout = () => {
// // //     if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
// // //     if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// // //     if (wsRef.current) wsRef.current.close();
// // //     if (onLogout) onLogout();
// // //   };

// // //   const connectWebSocket = (userId) => {
// // //     if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;
// // //     if (wsRef.current) wsRef.current.close();

// // //     const wsUrl = `${WS_BASE_URL}/escalation/ws/user/${userId}`;
// // //     console.log("Attempting to connect User WebSocket to:", wsUrl);
// // //     const ws = new WebSocket(wsUrl);

// // //     ws.onopen = () => {
// // //       setWsConnected(true);
// // //       console.log("User WebSocket connected");
// // //       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// // //       heartbeatIntervalRef.current = setInterval(() => {
// // //         if (ws.readyState === WebSocket.OPEN) {
// // //           ws.send(JSON.stringify({ type: 'ping' }));
// // //         }
// // //       }, 30000);
// // //     };

// // //     ws.onmessage = (event) => {
// // //       try {
// // //         const data = JSON.parse(event.data);
// // //         if (data.type === 'ping') {
// // //           ws.send(JSON.stringify({ type: 'pong' }));
// // //           return;
// // //         }
// // //         if (data.type === 'agent_message') {
// // //           setMessages(prev => [...prev, {
// // //             sender: "bot",
// // //             text: data.message,
// // //             timestamp: data.timestamp,
// // //             isAgent: true
// // //           }]);
// // //         } else if (data.type === 'error') {
// // //           setMessages(prev => [...prev, {
// // //             sender: "system",
// // //             text: `Error: ${data.message}`,
// // //             timestamp: new Date().toISOString()
// // //           }]);
// // //         }
// // //       } catch (error) {
// // //         console.error("Error parsing WebSocket message:", error);
// // //       }
// // //     };

// // //     ws.onclose = (event) => {
// // //       setWsConnected(false);
// // //       wsRef.current = null;
// // //       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// // //       if (event.code !== 1000 && userInfo?.user_id && !isLoggingOut) {
// // //         console.log("User WebSocket disconnected, reconnecting in 5s...");
// // //         setTimeout(() => connectWebSocket(userInfo.user_id), 5000);
// // //       }
// // //     };

// // //     ws.onerror = (error) => {
// // //       console.error("User WebSocket error:", error);
// // //       ws.close();
// // //     };

// // //     wsRef.current = ws;
// // //   };

// // //   const handleEscalationCreated = (escId) => {
// // //     if (escalationIdRef.current) {
// // //       alert("You already have an active support session.");
// // //       return;
// // //     }
// // //     setEscalationId(escId);
// // //     if (userInfo?.user_id && !wsConnected) connectWebSocket(userInfo.user_id);
// // //     setMessages(prev => [...prev, {
// // //       sender: "system",
// // //       text: "You've been connected to a live support agent. They will assist you shortly.",
// // //       timestamp: new Date().toISOString()
// // //     }]);
// // //   };

// // //   const handleOrderClick = async (orderId) => {
// // //     setMessages(prev => [...prev, { 
// // //       sender: "user", 
// // //       text: orderId, 
// // //       timestamp: new Date().toISOString() 
// // //     }]);
// // //     setLoading(true);
// // //     try {
// // //       const res = await fetch(`${API_BASE_URL}/chat`, {
// // //         method: "POST",
// // //         headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
// // //         body: JSON.stringify({ message: orderId }),
// // //       });
// // //       const data = await res.json();
// // //       if (res.ok) {
// // //         setMessages(prev => [...prev, { 
// // //           sender: "bot", 
// // //           text: data.reply, 
// // //           timestamp: new Date().toISOString() 
// // //         }]);
// // //       } else {
// // //         setMessages(prev => [...prev, { 
// // //           sender: "bot", 
// // //           text: data.detail || "Error fetching order details.", 
// // //           timestamp: new Date().toISOString() 
// // //         }]);
// // //       }
// // //     } catch (error) {
// // //       console.error("Error fetching order details:", error);
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   const sendMessage = async () => {
// // //     if (!input.trim()) return;
// // //     const userMessage = input.trim();
// // //     setInput("");
// // //     setMessages(prev => [...prev, { 
// // //       sender: "user", 
// // //       text: userMessage, 
// // //       timestamp: new Date().toISOString() 
// // //     }]);

// // //     if (escalationIdRef.current) {
// // //       if (wsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
// // //         wsRef.current.send(JSON.stringify({ 
// // //           type: "message", 
// // //           escalation_id: escalationIdRef.current, 
// // //           message: userMessage 
// // //         }));
// // //       } else {
// // //         if (userInfo?.user_id) connectWebSocket(userInfo.user_id);
// // //         setMessages(prev => [...prev, {
// // //           sender: "system",
// // //           text: "Reconnecting to support agent...",
// // //           timestamp: new Date().toISOString()
// // //         }]);
// // //       }
// // //       return;
// // //     }

// // //     setLoading(true);
// // //     try {
// // //       const res = await fetch(`${API_BASE_URL}/chat`, {
// // //         method: "POST",
// // //         headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
// // //         body: JSON.stringify({ message: userMessage }),
// // //       });
// // //       const data = await res.json();
// // //       if (res.ok) {
// // //         if (data.reply === "ORDER_LIST" && data.orders) {
// // //           setMessages(prev => [...prev, { 
// // //             sender: "bot", 
// // //             text: "Here are your recent orders:",
// // //             orders: data.orders,
// // //             timestamp: new Date().toISOString() 
// // //           }]);
// // //         } else {
// // //           setMessages(prev => [...prev, { 
// // //             sender: "bot", 
// // //             text: data.reply, 
// // //             timestamp: new Date().toISOString() 
// // //           }]);
// // //         }
// // //       } else {
// // //         setMessages(prev => [...prev, { 
// // //           sender: "bot", 
// // //           text: data.detail || "Sorry, an error occurred.", 
// // //           timestamp: new Date().toISOString() 
// // //         }]);
// // //       }
// // //     } catch (error) {
// // //       setMessages(prev => [...prev, { 
// // //         sender: "bot", 
// // //         text: "Connection error. Please check your internet.", 
// // //         timestamp: new Date().toISOString() 
// // //       }]);
// // //     } finally {
// // //       setLoading(false);
// // //     }
// // //   };

// // //   const scrollToBottom = () => {
// // //     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
// // //   };

// // //   const getStatusColor = (status) => {
// // //     const s = status.toLowerCase();
// // //     if (s.includes('delivered')) return '#4caf50';
// // //     if (s.includes('delivery')) return '#2196f3';
// // //     if (s.includes('preparing') || s.includes('processing')) return '#ff9800';
// // //     if (s.includes('cancelled')) return '#f44336';
// // //     return '#757575';
// // //   };

// // //   const getStatusEmoji = (status) => {
// // //     const s = status.toLowerCase();
// // //     if (s.includes('delivered')) return '✓';
// // //     if (s.includes('delivery')) return '🚚';
// // //     if (s.includes('preparing') || s.includes('processing')) return '🍳';
// // //     if (s.includes('ready')) return '✅';
// // //     if (s.includes('cancelled')) return '✗';
// // //     return '📦';
// // //   };

// // //   return (
// // //     <div style={styles.container}>
// // //       <div style={styles.header}>
// // //         <div>
// // //           <h2 style={styles.title}>
// // //             {escalationId ? "Live Agent Support" : "AI Support Assistant"}
// // //           </h2>
// // //           {escalationId && (
// // //             <p style={styles.modeIndicator}>
// // //               You are now chatting with a human support agent
// // //             </p>
// // //           )}
// // //         </div>
// // //         <div style={styles.statusContainer}>
// // //           {wsConnected && escalationId && (
// // //             <span style={styles.statusIndicator}>
// // //               <span style={styles.greenDot}>●</span> Agent Online
// // //             </span>
// // //           )}
// // //           {wsConnected && !escalationId && (
// // //             <span style={styles.statusIndicatorGray}>
// // //               <span style={styles.grayDot}>●</span> Ready
// // //             </span>
// // //           )}
// // //           {!wsConnected && userInfo && (
// // //             <span style={styles.statusIndicatorOff}>
// // //               <span style={styles.yellowDot}>●</span> Connecting...
// // //             </span>
// // //           )}
// // //         </div>
// // //       </div>

// // //       <EscalationButton token={token} onEscalationCreated={handleEscalationCreated} />

// // //       <div style={styles.chatBox}>
// // //         {messages.length === 0 && (
// // //           <div style={styles.emptyState}>
// // //             <p>Hello! How can I help you today?</p>
// // //             <p style={styles.emptyHint}>
// // //               Ask about orders, deliveries, refunds, or any issues you're experiencing.
// // //             </p>
// // //           </div>
// // //         )}
        
// // //         {messages.map((msg, i) => (
// // //           <div key={i}>
// // //             <div 
// // //               style={{
// // //                 ...styles.message,
// // //                 ...(msg.sender === "user" 
// // //                   ? styles.userMessage 
// // //                   : msg.sender === "system" 
// // //                   ? styles.systemMessage 
// // //                   : styles.botMessage)
// // //               }}
// // //             >
// // //               {msg.isAgent && <span style={styles.agentBadge}>Agent</span>}
// // //               <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
// // //               {msg.timestamp && (
// // //                 <div style={styles.timestamp}>
// // //                   {new Date(msg.timestamp).toLocaleTimeString()}
// // //                 </div>
// // //               )}
// // //             </div>

// // //             {msg.orders && msg.orders.length > 0 && (
// // //               <div style={styles.orderCardsContainer}>
// // //                 {msg.orders.map((order, idx) => (
// // //                   <div 
// // //                     key={idx} 
// // //                     style={styles.orderCard}
// // //                     onClick={() => handleOrderClick(order.order_id)}
// // //                     onMouseEnter={(e) => {
// // //                       e.currentTarget.style.transform = 'translateY(-2px)';
// // //                       e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.15)';
// // //                       e.currentTarget.style.borderColor = '#667eea';
// // //                     }}
// // //                     onMouseLeave={(e) => {
// // //                       e.currentTarget.style.transform = 'translateY(0)';
// // //                       e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
// // //                       e.currentTarget.style.borderColor = '#e0e0e0';
// // //                     }}
// // //                   >
// // //                     <div style={styles.orderHeader}>
// // //                       <div style={styles.orderRestaurant}>
// // //                         🍽️ {order.restaurant}
// // //                       </div>
// // //                       <div 
// // //                         style={{
// // //                           ...styles.orderStatus,
// // //                           backgroundColor: getStatusColor(order.status)
// // //                         }}
// // //                       >
// // //                         {getStatusEmoji(order.status)} {order.status}
// // //                       </div>
// // //                     </div>

// // //                     <div style={styles.orderItems}>
// // //                       <strong>Items:</strong> {order.items.slice(0, 3).join(', ')}
// // //                       {order.items.length > 3 && ` +${order.items.length - 3} more`}
// // //                     </div>

// // //                     <div style={styles.orderDetails}>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span>📅 {order.order_date}</span>
// // //                       </div>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span>📍 {order.delivery_address}</span>
// // //                       </div>
// // //                       <div style={styles.orderDetailRow}>
// // //                         <span style={styles.orderTotal}>💵 ${order.total_amount}</span>
// // //                       </div>
// // //                     </div>

// // //                     <div style={styles.orderFooter}>
// // //                       Order ID: {order.order_id.slice(0, 8)}...
// // //                     </div>

// // //                     <div style={styles.clickHint}>
// // //                       Click to view full details
// // //                     </div>
// // //                   </div>
// // //                 ))}
// // //               </div>
// // //             )}
// // //           </div>
// // //         ))}
        
// // //         {loading && (
// // //           <div style={styles.loadingMessage}>
// // //             <div style={styles.typingDots}>
// // //               <span>.</span><span>.</span><span>.</span>
// // //             </div>
// // //           </div>
// // //         )}
        
// // //         <div ref={messagesEndRef} />
// // //       </div>

// // //       <div style={styles.inputArea}>
// // //         <input
// // //           type="text"
// // //           value={input}
// // //           onChange={e => setInput(e.target.value)}
// // //           onKeyDown={e => e.key === "Enter" && !loading && sendMessage()}
// // //           placeholder={
// // //             escalationId && wsConnected 
// // //               ? "Message the agent..." 
// // //               : escalationId && !wsConnected 
// // //               ? "Connecting to agent..." 
// // //               : "Type your message..."
// // //           }
// // //           disabled={loading || (escalationId && !wsConnected)}
// // //           style={styles.input}
// // //         />
// // //         <button 
// // //           onClick={sendMessage} 
// // //           disabled={loading || !input.trim() || (escalationId && !wsConnected)} 
// // //           style={{
// // //             ...styles.sendButton,
// // //             ...(loading || !input.trim() || (escalationId && !wsConnected) 
// // //               ? styles.sendButtonDisabled 
// // //               : {})
// // //           }}
// // //         >
// // //           {loading ? "..." : "Send"}
// // //         </button>
// // //       </div>

// // //       <FeedbackModal
// // //         show={showFeedbackModal}
// // //         onClose={handleFeedbackClose}
// // //         onSubmit={handleFeedbackSubmit}
// // //         sessionId={currentSessionId}
// // //       />
// // //     </div>
// // //   );
// // // }

// // // const styles = {
// // //   container: { 
// // //     maxWidth: "1200px", 
// // //     margin: "0 auto", 
// // //     padding: "20px", 
// // //     fontFamily: "'Inter', sans-serif",
// // //     height: "calc(100vh - 40px)",
// // //     display: "flex",
// // //     flexDirection: "column"
// // //   },
// // //   header: { 
// // //     display: "flex", 
// // //     justifyContent: "space-between", 
// // //     alignItems: "center", 
// // //     marginBottom: "15px",
// // //     paddingBottom: "15px",
// // //     borderBottom: "2px solid #e0e0e0"
// // //   },
// // //   title: { 
// // //     margin: 0, 
// // //     fontSize: "1.5rem", 
// // //     color: "#333" 
// // //   },
// // //   modeIndicator: { 
// // //     margin: "4px 0 0 0", 
// // //     fontSize: "0.85rem", 
// // //     color: "#4caf50", 
// // //     fontWeight: "500" 
// // //   },
// // //   statusContainer: { 
// // //     display: "flex", 
// // //     gap: "0.5rem" 
// // //   },
// // //   statusIndicator: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#e8f5e9", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px", 
// // //     fontWeight: "500" 
// // //   },
// // //   statusIndicatorGray: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#f5f5f5", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px" 
// // //   },
// // //   statusIndicatorOff: { 
// // //     display: "flex", 
// // //     alignItems: "center", 
// // //     gap: "0.5rem", 
// // //     fontSize: "0.9rem", 
// // //     color: "#666", 
// // //     background: "#fff3e0", 
// // //     padding: "0.5rem 1rem", 
// // //     borderRadius: "20px" 
// // //   },
// // //   greenDot: { 
// // //     color: "#4caf50", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   grayDot: { 
// // //     color: "#999", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   yellowDot: { 
// // //     color: "#ff9800", 
// // //     fontSize: "1.2rem" 
// // //   },
// // //   chatBox: { 
// // //     border: "1px solid #ddd", 
// // //     borderRadius: "12px", 
// // //     flex: 1,
// // //     overflowY: "auto", 
// // //     padding: "24px", 
// // //     marginBottom: "15px", 
// // //     backgroundColor: "#fafafa",
// // //     minHeight: 0
// // //   },
// // //   emptyState: { 
// // //     textAlign: "center", 
// // //     padding: "4rem 2rem", 
// // //     color: "#666" 
// // //   },
// // //   emptyHint: { 
// // //     fontSize: "0.9rem", 
// // //     color: "#999", 
// // //     marginTop: "0.5rem" 
// // //   },
// // //   message: { 
// // //     padding: "14px 18px", 
// // //     marginBottom: "14px", 
// // //     borderRadius: "12px", 
// // //     maxWidth: "85%", 
// // //     wordWrap: "break-word", 
// // //     lineHeight: "1.6",
// // //     fontSize: "0.95rem",
// // //     minWidth: "300px"
// // //   },
// // //   userMessage: { 
// // //     backgroundColor: "#667eea", 
// // //     color: "white", 
// // //     marginLeft: "auto", 
// // //     borderBottomRightRadius: "4px",
// // //     maxWidth: "70%"
// // //   },
// // //   botMessage: { 
// // //     backgroundColor: "white", 
// // //     color: "#333", 
// // //     border: "1px solid #e0e0e0", 
// // //     borderBottomLeftRadius: "4px",
// // //     maxWidth: "85%"
// // //   },
// // //   systemMessage: { 
// // //     backgroundColor: "#fff3cd", 
// // //     color: "#856404", 
// // //     border: "1px solid #ffc107", 
// // //     textAlign: "center", 
// // //     margin: "1rem auto", 
// // //     maxWidth: "85%",
// // //     fontSize: "0.9rem"
// // //   },
// // //   agentBadge: { 
// // //     display: "inline-block", 
// // //     background: "#4caf50", 
// // //     color: "white", 
// // //     padding: "3px 10px", 
// // //     borderRadius: "12px", 
// // //     fontSize: "0.75rem", 
// // //     fontWeight: "600", 
// // //     marginBottom: "6px" 
// // //   },
// // //   timestamp: { 
// // //     fontSize: "0.7rem", 
// // //     color: "#999", 
// // //     marginTop: "6px" 
// // //   },
// // //   loadingMessage: { 
// // //     backgroundColor: "white", 
// // //     color: "#666", 
// // //     padding: "12px 16px", 
// // //     borderRadius: "12px", 
// // //     maxWidth: "75px", 
// // //     border: "1px solid #e0e0e0" 
// // //   },
// // //   typingDots: { 
// // //     display: "flex", 
// // //     gap: "4px", 
// // //     fontSize: "1.5rem" 
// // //   },
// // //   inputArea: { 
// // //     display: "flex", 
// // //     gap: "12px",
// // //     padding: "8px 0"
// // //   },
// // //   input: { 
// // //     flex: 1, 
// // //     padding: "14px 18px", 
// // //     border: "2px solid #ddd", 
// // //     borderRadius: "10px", 
// // //     fontSize: "1rem", 
// // //     outline: "none", 
// // //     transition: "border-color 0.2s",
// // //     fontFamily: "'Inter', sans-serif"
// // //   },
// // //   sendButton: { 
// // //     padding: "14px 40px", 
// // //     backgroundColor: "#667eea", 
// // //     color: "white", 
// // //     border: "none", 
// // //     borderRadius: "10px", 
// // //     cursor: "pointer", 
// // //     fontSize: "1rem", 
// // //     fontWeight: "600", 
// // //     transition: "all 0.2s",
// // //     minWidth: "120px"
// // //   },
// // //   sendButtonDisabled: { 
// // //     backgroundColor: "#ccc", 
// // //     cursor: "not-allowed" 
// // //   },
// // //   orderCardsContainer: {
// // //     display: "grid",
// // //     gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
// // //     gap: "1.25rem",
// // //     marginTop: "0.75rem",
// // //     marginBottom: "1rem",
// // //     width: "100%"
// // //   },
// // //   orderCard: {
// // //     backgroundColor: "white",
// // //     border: "2px solid #e0e0e0",
// // //     borderRadius: "12px",
// // //     padding: "1.25rem",
// // //     cursor: "pointer",
// // //     transition: "all 0.3s ease",
// // //     boxShadow: "0 2px 6px rgba(0,0,0,0.08)"
// // //   },
// // //   orderHeader: {
// // //     display: "flex",
// // //     justifyContent: "space-between",
// // //     alignItems: "flex-start",
// // //     marginBottom: "0.875rem"
// // //   },
// // //   orderRestaurant: {
// // //     fontWeight: "600",
// // //     fontSize: "1.05rem",
// // //     color: "#333",
// // //     flex: 1
// // //   },
// // //   orderStatus: {
// // //     padding: "0.35rem 0.65rem",
// // //     borderRadius: "6px",
// // //     fontSize: "0.8rem",
// // //     fontWeight: "600",
// // //     color: "white",
// // //     whiteSpace: "nowrap",
// // //     marginLeft: "0.75rem"
// // //   },
// // //   orderItems: {
// // //     fontSize: "0.9rem",
// // //     color: "#666",
// // //     marginBottom: "0.875rem",
// // //     lineHeight: "1.5"
// // //   },
// // //   orderDetails: {
// // //     display: "flex",
// // //     flexDirection: "column",
// // //     gap: "0.35rem",
// // //     marginBottom: "0.875rem",
// // //     fontSize: "0.85rem",
// // //     color: "#555"
// // //   },
// // //   orderDetailRow: {
// // //     display: "flex",
// // //     alignItems: "center"
// // //   },
// // //   orderTotal: {
// // //     fontWeight: "700",
// // //     fontSize: "0.95rem",
// // //     color: "#333"
// // //   },
// // //   orderFooter: {
// // //     fontSize: "0.8rem",
// // //     color: "#999",
// // //     borderTop: "1px solid #f0f0f0",
// // //     paddingTop: "0.65rem",
// // //     marginTop: "0.65rem"
// // //   },
// // //   clickHint: {
// // //     fontSize: "0.75rem",
// // //     color: "#667eea",
// // //     textAlign: "center",
// // //     marginTop: "0.65rem",
// // //     fontStyle: "italic"
// // //   }
// // // };

// // // export default ChatWindow;






// // import React, { useState, useEffect, useRef } from "react";
// // import EscalationButton from './EscalationButton';
// // import FeedbackModal from './FeedbackModal';
// // import API_BASE_URL, { WS_BASE_URL } from "./config";

// // function ChatWindow({ token, onLogout }) {
// //   const [messages, setMessages] = useState([]);
// //   const [input, setInput] = useState("");
// //   const [loading, setLoading] = useState(false);
// //   const [escalationId, setEscalationId] = useState(null);
// //   const [wsConnected, setWsConnected] = useState(false);
// //   const [userInfo, setUserInfo] = useState(null);
// //   const [showFeedbackModal, setShowFeedbackModal] = useState(false);
// //   const [currentSessionId, setCurrentSessionId] = useState(null);
// //   const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
// //   const [isLoggingOut, setIsLoggingOut] = useState(false);

// //   const wsRef = useRef(null);
// //   const messagesEndRef = useRef(null);
// //   const escalationIdRef = useRef(null);
// //   const heartbeatIntervalRef = useRef(null);
// //   const feedbackCheckTimeoutRef = useRef(null);

// //   useEffect(() => {
// //     escalationIdRef.current = escalationId;
// //   }, [escalationId]);

// //   useEffect(() => {
// //     fetchUserInfo();
// //     checkForExistingEscalation();
// //     return () => {
// //       if (wsRef.current) wsRef.current.close();
// //       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
// //       if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
// //     };
// //   }, [token]);

// //   useEffect(() => scrollToBottom(), [messages]);

// //   useEffect(() => {
// //     if (userInfo?.user_id && !wsRef.current) {
// //       connectWebSocket(userInfo.user_id);
// //     }
// //   }, [userInfo]);

// //   const fetchUserInfo = async () => {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/auth/me`, {
// //         headers: { Authorization: `Bearer ${token}` },
// //       });
// //       if (response.ok) setUserInfo(await response.json());
// //     } catch (error) {
// //       console.error("Error fetching user info:", error);
// //     }
// //   };

// //   const checkForExistingEscalation = async () => {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/escalation/escalations/my`, {
// //         headers: { Authorization: `Bearer ${token}` },
// //       });
// //       if (response.ok) {
// //         const data = await response.json();
// //         const activeEscalation = data.escalations?.find(
// //           esc => esc.status !== 'resolved' && esc.status !== 'closed'
// //         );
// //         if (activeEscalation) {
// //           setEscalationId(activeEscalation.escalation_id);
// //           await loadEscalationHistory(activeEscalation.escalation_id);
// //           setMessages(prev => [...prev, {
// //             sender: "system",
// //             text: `Resuming your support session (Case #${activeEscalation.escalation_id.slice(0, 8)})`,
// //             timestamp: new Date().toISOString()
// //           }]);
// //         }
// //       }
// //     } catch (error) {
// //       console.error("Error checking for existing escalations:", error);
// //     }
// //   };

// //   const loadEscalationHistory = async (escId) => {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/escalation/messages/${escId}`, {
// //         headers: { Authorization: `Bearer ${token}` },
// //       });
// //       if (response.ok) {
// //         const data = await response.json();
// //         const formattedMessages = data.messages.map(msg => ({
// //           sender: msg.sender === 'agent' ? 'bot' : 'user', // Treat agent messages as 'bot' for styling
// //           text: msg.message,
// //           timestamp: msg.timestamp,
// //           isAgent: msg.sender === 'agent',
// //         }));
// //         setMessages(formattedMessages);
// //       }
// //     } catch (error) {
// //       console.error("Error loading escalation history:", error);
// //     }
// //   };

// //   const connectWebSocket = (userId) => {
// //     if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

// //     const wsUrl = `${WS_BASE_URL}/escalation/ws/user/${userId}`;
// //     console.log("Connecting user WebSocket to:", wsUrl);
// //     const ws = new WebSocket(wsUrl);

// //     ws.onopen = () => {
// //       setWsConnected(true);
// //       console.log("User WebSocket connected");
// //     };

// //     ws.onmessage = (event) => {
// //       const data = JSON.parse(event.data);
// //       if (data.type === 'agent_message') {
// //         setMessages(prev => [...prev, {
// //           sender: "bot", // Display agent message as a "bot" message for styling
// //           text: data.message,
// //           timestamp: data.timestamp,
// //           isAgent: true
// //         }]);
// //       }
// //     };

// //     ws.onclose = (event) => {
// //       setWsConnected(false);
// //       wsRef.current = null;
// //       if (event.code !== 1000 && !isLoggingOut) {
// //         setTimeout(() => connectWebSocket(userId), 5000);
// //       }
// //     };

// //     ws.onerror = (error) => {
// //       console.error("User WebSocket error:", error);
// //       ws.close();
// //     };

// //     wsRef.current = ws;
// //   };

// //   const handleEscalationCreated = (escId) => {
// //     if (escalationIdRef.current) return;
// //     setEscalationId(escId);
// //     setMessages(prev => [...prev, {
// //       sender: "system",
// //       text: "You've been connected to a live support agent. They will assist you shortly.",
// //       timestamp: new Date().toISOString()
// //     }]);
// //   };
  
// //   const sendMessage = async () => {
// //     if (!input.trim()) return;

// //     const userMessage = input.trim();
// //     setInput("");
// //     setMessages(prev => [...prev, { sender: "user", text: userMessage, timestamp: new Date().toISOString() }]);

// //     // --- THIS IS THE CORRECTED LOGIC ---
// //     // If an escalation ID exists, send the message via WebSocket and STOP.
// //     if (escalationIdRef.current) {
// //       if (wsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
// //         wsRef.current.send(JSON.stringify({ 
// //           type: "message", 
// //           escalation_id: escalationIdRef.current, 
// //           message: userMessage 
// //         }));
// //       } else {
// //         // If disconnected, show a reconnecting message
// //         setMessages(prev => [...prev, {
// //           sender: "system", text: "Reconnecting to support agent...", timestamp: new Date().toISOString()
// //         }]);
// //       }
// //       return; // This 'return' is critical. It stops the function here.
// //     }

// //     // If no escalation ID, proceed to send the message to the AI bot.
// //     setLoading(true);
// //     try {
// //       const res = await fetch(`${API_BASE_URL}/chat`, {
// //         method: "POST",
// //         headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
// //         body: JSON.stringify({ message: userMessage }),
// //       });
      
// //       const data = await res.json();
// //       const botReply = { sender: "bot", text: data.reply, timestamp: new Date().toISOString() };

// //       if (res.ok && data.reply === "ORDER_LIST" && data.orders) {
// //         botReply.orders = data.orders;
// //         botReply.text = "Here are your recent orders:";
// //       }
      
// //       setMessages(prev => [...prev, botReply]);

// //       // Check if the bot's reply created an escalation
// //       const escMatch = data.reply.match(/ESC_\d+/);
// //       if (escMatch) {
// //         handleEscalationCreated(escMatch[0]);
// //       }
      
// //     } catch (error) {
// //       setMessages(prev => [...prev, { 
// //         sender: "bot", text: "Connection error. Please try again.", timestamp: new Date().toISOString() 
// //       }]);
// //     } finally {
// //       setLoading(false);
// //     }
// //   };
  
// //   const scrollToBottom = () => {
// //     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
// //   };
  
// //   return (
// //     <div style={styles.container}>
// //       <div style={styles.header}>
// //         <div>
// //           <h2 style={styles.title}>
// //             {escalationId ? "Live Agent Support" : "AI Support Assistant"}
// //           </h2>
// //           {escalationId && (
// //             <p style={styles.modeIndicator}>
// //               You are now chatting with a human support agent
// //             </p>
// //           )}
// //         </div>
// //         <div style={styles.statusContainer}>
// //           {wsConnected && escalationId && (
// //             <span style={styles.statusIndicator}>
// //               <span style={styles.greenDot}>●</span> Agent Online
// //             </span>
// //           )}
// //           {wsConnected && !escalationId && (
// //             <span style={styles.statusIndicatorGray}>
// //               <span style={styles.grayDot}>●</span> Ready
// //             </span>
// //           )}
// //           {!wsConnected && userInfo && (
// //             <span style={styles.statusIndicatorOff}>
// //               <span style={styles.yellowDot}>●</span> Connecting...
// //             </span>
// //           )}
// //         </div>
// //       </div>

// //       <EscalationButton token={token} onEscalationCreated={handleEscalationCreated} />

// //       <div style={styles.chatBox}>
// //         {messages.length === 0 && (
// //           <div style={styles.emptyState}>
// //             <p>Hello! How can I help you today?</p>
// //             <p style={styles.emptyHint}>
// //               Ask about orders, deliveries, refunds, or any issues you're experiencing.
// //             </p>
// //           </div>
// //         )}
        
// //         {messages.map((msg, i) => (
// //           <div key={i}>
// //             <div 
// //               style={{
// //                 ...styles.message,
// //                 ...(msg.sender === "user" 
// //                   ? styles.userMessage 
// //                   : msg.sender === "system" 
// //                   ? styles.systemMessage 
// //                   : styles.botMessage)
// //               }}
// //             >
// //               {msg.isAgent && <span style={styles.agentBadge}>Agent</span>}
// //               <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
// //               {msg.timestamp && (
// //                 <div style={styles.timestamp}>
// //                   {new Date(msg.timestamp).toLocaleTimeString()}
// //                 </div>
// //               )}
// //             </div>
// //           </div>
// //         ))}
        
// //         {loading && (
// //           <div style={styles.loadingMessage}>
// //             <div style={styles.typingDots}>
// //               <span>.</span><span>.</span><span>.</span>
// //             </div>
// //           </div>
// //         )}
        
// //         <div ref={messagesEndRef} />
// //       </div>

// //       <div style={styles.inputArea}>
// //         <input
// //           type="text"
// //           value={input}
// //           onChange={e => setInput(e.target.value)}
// //           onKeyDown={e => e.key === "Enter" && !loading && sendMessage()}
// //           placeholder={
// //             escalationId && wsConnected 
// //               ? "Message the agent..." 
// //               : escalationId && !wsConnected 
// //               ? "Connecting to agent..." 
// //               : "Type your message..."
// //           }
// //           disabled={loading || (escalationId && !wsConnected)}
// //           style={styles.input}
// //         />
// //         <button 
// //           onClick={sendMessage} 
// //           disabled={loading || !input.trim() || (escalationId && !wsConnected)} 
// //           style={{
// //             ...styles.sendButton,
// //             ...((loading || !input.trim() || (escalationId && !wsConnected)) 
// //               ? styles.sendButtonDisabled 
// //               : {})
// //           }}
// //         >
// //           {loading ? "..." : "Send"}
// //         </button>
// //       </div>

// //       <FeedbackModal
// //         show={showFeedbackModal}
// //         onClose={() => setShowFeedbackModal(false)}
// //         onSubmit={() => {}}
// //         sessionId={currentSessionId}
// //       />
// //     </div>
// //   );
// // }

// // const styles = {
// //   container: { 
// //     maxWidth: "1200px", 
// //     margin: "0 auto", 
// //     padding: "20px", 
// //     fontFamily: "'Inter', sans-serif",
// //     height: "calc(100vh - 40px)",
// //     display: "flex",
// //     flexDirection: "column"
// //   },
// //   header: { 
// //     display: "flex", 
// //     justifyContent: "space-between", 
// //     alignItems: "center", 
// //     marginBottom: "15px",
// //     paddingBottom: "15px",
// //     borderBottom: "2px solid #e0e0e0"
// //   },
// //   title: { 
// //     margin: 0, 
// //     fontSize: "1.5rem", 
// //     color: "#333" 
// //   },
// //   modeIndicator: { 
// //     margin: "4px 0 0 0", 
// //     fontSize: "0.85rem", 
// //     color: "#4caf50", 
// //     fontWeight: "500" 
// //   },
// //   statusContainer: { 
// //     display: "flex", 
// //     gap: "0.5rem" 
// //   },
// //   statusIndicator: { 
// //     display: "flex", 
// //     alignItems: "center", 
// //     gap: "0.5rem", 
// //     fontSize: "0.9rem", 
// //     color: "#666", 
// //     background: "#e8f5e9", 
// //     padding: "0.5rem 1rem", 
// //     borderRadius: "20px", 
// //     fontWeight: "500" 
// //   },
// //   statusIndicatorGray: { 
// //     display: "flex", 
// //     alignItems: "center", 
// //     gap: "0.5rem", 
// //     fontSize: "0.9rem", 
// //     color: "#666", 
// //     background: "#f5f5f5", 
// //     padding: "0.5rem 1rem", 
// //     borderRadius: "20px" 
// //   },
// //   statusIndicatorOff: { 
// //     display: "flex", 
// //     alignItems: "center", 
// //     gap: "0.5rem", 
// //     fontSize: "0.9rem", 
// //     color: "#666", 
// //     background: "#fff3e0", 
// //     padding: "0.5rem 1rem", 
// //     borderRadius: "20px" 
// //   },
// //   greenDot: { 
// //     color: "#4caf50", 
// //     fontSize: "1.2rem" 
// //   },
// //   grayDot: { 
// //     color: "#999", 
// //     fontSize: "1.2rem" 
// //   },
// //   yellowDot: { 
// //     color: "#ff9800", 
// //     fontSize: "1.2rem" 
// //   },
// //   chatBox: { 
// //     border: "1px solid #ddd", 
// //     borderRadius: "12px", 
// //     flex: 1,
// //     overflowY: "auto", 
// //     padding: "24px", 
// //     marginBottom: "15px", 
// //     backgroundColor: "#fafafa",
// //     minHeight: 0
// //   },
// //   emptyState: { 
// //     textAlign: "center", 
// //     padding: "4rem 2rem", 
// //     color: "#666" 
// //   },
// //   emptyHint: { 
// //     fontSize: "0.9rem", 
// //     color: "#999", 
// //     marginTop: "0.5rem" 
// //   },
// //   message: { 
// //     padding: "14px 18px", 
// //     marginBottom: "14px", 
// //     borderRadius: "12px", 
// //     maxWidth: "85%", 
// //     wordWrap: "break-word", 
// //     lineHeight: "1.6",
// //     fontSize: "0.95rem",
// //   },
// //   userMessage: { 
// //     backgroundColor: "#667eea", 
// //     color: "white", 
// //     marginLeft: "auto", 
// //     borderBottomRightRadius: "4px",
// //     maxWidth: "70%"
// //   },
// //   botMessage: { 
// //     backgroundColor: "white", 
// //     color: "#333", 
// //     border: "1px solid #e0e0e0", 
// //     borderBottomLeftRadius: "4px",
// //     maxWidth: "85%"
// //   },
// //   systemMessage: { 
// //     backgroundColor: "#fff3cd", 
// //     color: "#856404", 
// //     border: "1px solid #ffc107", 
// //     textAlign: "center", 
// //     margin: "1rem auto", 
// //     maxWidth: "85%",
// //     fontSize: "0.9rem"
// //   },
// //   agentBadge: { 
// //     display: "inline-block", 
// //     background: "#4caf50", 
// //     color: "white", 
// //     padding: "3px 10px", 
// //     borderRadius: "12px", 
// //     fontSize: "0.75rem", 
// //     fontWeight: "600", 
// //     marginBottom: "6px" 
// //   },
// //   timestamp: { 
// //     fontSize: "0.7rem", 
// //     color: "#999", 
// //     marginTop: "6px",
// //     textAlign: "right"
// //   },
// //   loadingMessage: { 
// //     backgroundColor: "white", 
// //     color: "#666", 
// //     padding: "12px 16px", 
// //     borderRadius: "12px", 
// //     maxWidth: "75px", 
// //     border: "1px solid #e0e0e0" 
// //   },
// //   typingDots: { 
// //     display: "flex", 
// //     gap: "4px", 
// //     fontSize: "1.5rem" 
// //   },
// //   inputArea: { 
// //     display: "flex", 
// //     gap: "12px",
// //     padding: "8px 0"
// //   },
// //   input: { 
// //     flex: 1, 
// //     padding: "14px 18px", 
// //     border: "2px solid #ddd", 
// //     borderRadius: "10px", 
// //     fontSize: "1rem", 
// //     outline: "none", 
// //     transition: "border-color 0.2s",
// //     fontFamily: "'Inter', sans-serif"
// //   },
// //   sendButton: { 
// //     padding: "14px 40px", 
// //     backgroundColor: "#667eea", 
// //     color: "white", 
// //     border: "none", 
// //     borderRadius: "10px", 
// //     cursor: "pointer", 
// //     fontSize: "1rem", 
// //     fontWeight: "600", 
// //     transition: "all 0.2s",
// //     minWidth: "120px"
// //   },
// //   sendButtonDisabled: { 
// //     backgroundColor: "#ccc", 
// //     cursor: "not-allowed" 
// //   }
// // };

// // export default ChatWindow;






// import React, { useState, useEffect, useRef } from "react";
// import EscalationButton from './EscalationButton';
// import FeedbackModal from './FeedbackModal';
// import API_BASE_URL, { WS_BASE_URL } from "./config";

// function ChatWindow({ token, onLogout }) {
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [escalationId, setEscalationId] = useState(null);
//   const [wsConnected, setWsConnected] = useState(false);
//   const [userInfo, setUserInfo] = useState(null);
//   const [showFeedbackModal, setShowFeedbackModal] = useState(false);
//   const [currentSessionId, setCurrentSessionId] = useState(null);
//   const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
//   const [isLoggingOut, setIsLoggingOut] = useState(false);

//   const wsRef = useRef(null);
//   const messagesEndRef = useRef(null);
//   const escalationIdRef = useRef(null);
//   const heartbeatIntervalRef = useRef(null);
//   const feedbackCheckTimeoutRef = useRef(null);

//   // Keep escalationIdRef in sync
//   useEffect(() => {
//     escalationIdRef.current = escalationId;
//     console.log("Escalation ID updated:", escalationId);
//   }, [escalationId]);

//   useEffect(() => {
//     fetchUserInfo();
//     checkForExistingEscalation();
//     return () => {
//       if (wsRef.current) wsRef.current.close();
//       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
//       if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
//     };
//   }, [token]);

//   useEffect(() => scrollToBottom(), [messages]);

//   useEffect(() => {
//     if (userInfo?.user_id && !wsRef.current) {
//       connectWebSocket(userInfo.user_id);
//     }
//   }, [userInfo]);

//   const fetchUserInfo = async () => {
//     try {
//       const response = await fetch(`${API_BASE_URL}/auth/me`, {
//         headers: { Authorization: `Bearer ${token}` },
//       });
//       if (response.ok) {
//         const data = await response.json();
//         setUserInfo(data);
//         console.log("User info loaded:", data);
//       }
//     } catch (error) {
//       console.error("Error fetching user info:", error);
//     }
//   };

//   const checkForExistingEscalation = async () => {
//     try {
//       const response = await fetch(`${API_BASE_URL}/escalation/escalations/my`, {
//         headers: { Authorization: `Bearer ${token}` },
//       });
//       if (response.ok) {
//         const data = await response.json();
//         const activeEscalation = data.escalations?.find(
//           esc => esc.status !== 'resolved' && esc.status !== 'closed'
//         );
//         if (activeEscalation) {
//           console.log("Found active escalation:", activeEscalation.escalation_id);
//           setEscalationId(activeEscalation.escalation_id);
//           escalationIdRef.current = activeEscalation.escalation_id;
//           await loadEscalationHistory(activeEscalation.escalation_id);
//           setMessages(prev => [...prev, {
//             sender: "system",
//             text: `Resuming your support session (Case #${activeEscalation.escalation_id.slice(0, 8)})`,
//             timestamp: new Date().toISOString()
//           }]);
//         }
//       }
//     } catch (error) {
//       console.error("Error checking for existing escalations:", error);
//     }
//   };

//   const loadEscalationHistory = async (escId) => {
//     try {
//       const response = await fetch(`${API_BASE_URL}/escalation/messages/${escId}`, {
//         headers: { Authorization: `Bearer ${token}` },
//       });
//       if (response.ok) {
//         const data = await response.json();
//         const formattedMessages = data.messages.map(msg => ({
//           sender: msg.sender === 'agent' ? 'bot' : 'user',
//           text: msg.message,
//           timestamp: msg.timestamp,
//           isAgent: msg.sender === 'agent',
//         }));
//         setMessages(formattedMessages);
//       }
//     } catch (error) {
//       console.error("Error loading escalation history:", error);
//     }
//   };

//   const connectWebSocket = (userId) => {
//     if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
//       console.log("WebSocket already connected");
//       return;
//     }

//     const wsUrl = `${WS_BASE_URL}/escalation/ws/user/${userId}`;
//     console.log("Connecting user WebSocket to:", wsUrl);
//     const ws = new WebSocket(wsUrl);

//     ws.onopen = () => {
//       setWsConnected(true);
//       console.log("✅ User WebSocket connected");
      
//       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
//       heartbeatIntervalRef.current = setInterval(() => {
//         if (ws.readyState === WebSocket.OPEN) {
//           ws.send(JSON.stringify({ type: 'ping' }));
//         }
//       }, 30000);
//     };

//     ws.onmessage = (event) => {
//       try {
//         const data = JSON.parse(event.data);
//         console.log("WebSocket message received:", data);
        
//         if (data.type === 'ping') {
//           ws.send(JSON.stringify({ type: 'pong' }));
//           return;
//         }
        
//         if (data.type === 'agent_message') {
//           console.log("📨 Agent message received:", data.message);
//           setMessages(prev => [...prev, {
//             sender: "bot",
//             text: data.message,
//             timestamp: data.timestamp,
//             isAgent: true
//           }]);
//         } else if (data.type === 'error') {
//           setMessages(prev => [...prev, {
//             sender: "system",
//             text: `Error: ${data.message}`,
//             timestamp: new Date().toISOString()
//           }]);
//         }
//       } catch (error) {
//         console.error("Error parsing WebSocket message:", error);
//       }
//     };

//     ws.onclose = (event) => {
//       setWsConnected(false);
//       wsRef.current = null;
//       console.log("❌ User WebSocket closed, code:", event.code);
      
//       if (heartbeatIntervalRef.current) {
//         clearInterval(heartbeatIntervalRef.current);
//         heartbeatIntervalRef.current = null;
//       }
      
//       if (event.code !== 1000 && !isLoggingOut) {
//         console.log("🔄 Reconnecting in 5 seconds...");
//         setTimeout(() => connectWebSocket(userId), 5000);
//       }
//     };

//     ws.onerror = (error) => {
//       console.error("❌ User WebSocket error:", error);
//     };

//     wsRef.current = ws;
//   };

//   const handleEscalationCreated = (escId) => {
//     if (escalationIdRef.current) {
//       console.warn("Already have active escalation:", escalationIdRef.current);
//       return;
//     }
    
//     console.log("✅ New escalation created:", escId);
//     setEscalationId(escId);
//     escalationIdRef.current = escId;
    
//     if (userInfo?.user_id && !wsConnected) {
//       connectWebSocket(userInfo.user_id);
//     }
    
//     setMessages(prev => [...prev, {
//       sender: "system",
//       text: "You've been connected to a live support agent. They will assist you shortly.",
//       timestamp: new Date().toISOString()
//     }]);
//   };
  
//   const sendMessage = async () => {
//     if (!input.trim()) return;

//     const userMessage = input.trim();
//     setInput("");
    
//     setMessages(prev => [...prev, { 
//       sender: "user", 
//       text: userMessage, 
//       timestamp: new Date().toISOString() 
//     }]);

//     // Check if escalation is active using ref (most current value)
//     const currentEscalationId = escalationIdRef.current;
//     console.log("📤 Sending message, escalation ID:", currentEscalationId);

//     // If escalation exists, send via WebSocket and STOP
//     if (currentEscalationId) {
//       console.log("🔄 Escalation active, sending via WebSocket");
      
//       if (wsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
//         console.log("✅ WebSocket ready, sending message");
//         wsRef.current.send(JSON.stringify({ 
//           type: "message", 
//           escalation_id: currentEscalationId, 
//           message: userMessage 
//         }));
//       } else {
//         console.log("⚠️ WebSocket not ready, attempting reconnection");
//         setMessages(prev => [...prev, {
//           sender: "system", 
//           text: "Reconnecting to support agent...", 
//           timestamp: new Date().toISOString()
//         }]);
        
//         if (userInfo?.user_id) {
//           connectWebSocket(userInfo.user_id);
//         }
//       }
//       return; // CRITICAL: Stop here, don't call bot API
//     }

//     // No escalation - send to AI bot
//     console.log("🤖 No escalation, sending to AI bot");
//     setLoading(true);
    
//     try {
//       const res = await fetch(`${API_BASE_URL}/chat`, {
//         method: "POST",
//         headers: { 
//           "Content-Type": "application/json", 
//           Authorization: `Bearer ${token}` 
//         },
//         body: JSON.stringify({ message: userMessage }),
//       });
      
//       const data = await res.json();
      
//       if (res.ok) {
//         if (data.reply === "ORDER_LIST" && data.orders) {
//           setMessages(prev => [...prev, { 
//             sender: "bot", 
//             text: "Here are your recent orders:",
//             orders: data.orders,
//             timestamp: new Date().toISOString() 
//           }]);
//         } else {
//           setMessages(prev => [...prev, { 
//             sender: "bot", 
//             text: data.reply, 
//             timestamp: new Date().toISOString() 
//           }]);

//           // Check if bot created an escalation
//           const escMatch = data.reply.match(/ESC_[a-zA-Z0-9]+/);
//           if (escMatch) {
//             const newEscalationId = escMatch[0];
//             console.log("🆕 Bot created escalation:", newEscalationId);
//             handleEscalationCreated(newEscalationId);
//           }
//         }
//       } else {
//         setMessages(prev => [...prev, { 
//           sender: "bot", 
//           text: data.detail || "Sorry, an error occurred.", 
//           timestamp: new Date().toISOString() 
//         }]);
//       }
//     } catch (error) {
//       console.error("Error sending message:", error);
//       setMessages(prev => [...prev, { 
//         sender: "bot", 
//         text: "Connection error. Please try again.", 
//         timestamp: new Date().toISOString() 
//       }]);
//     } finally {
//       setLoading(false);
//     }
//   };
  
//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   };
  
//   return (
//     <div style={styles.container}>
//       <div style={styles.header}>
//         <div>
//           <h2 style={styles.title}>
//             {escalationId ? "Live Agent Support" : "AI Support Assistant"}
//           </h2>
//           {escalationId && (
//             <p style={styles.modeIndicator}>
//               You are now chatting with a human support agent
//             </p>
//           )}
//         </div>
//         <div style={styles.statusContainer}>
//           {wsConnected && escalationId && (
//             <span style={styles.statusIndicator}>
//               <span style={styles.greenDot}>●</span> Agent Online
//             </span>
//           )}
//           {wsConnected && !escalationId && (
//             <span style={styles.statusIndicatorGray}>
//               <span style={styles.grayDot}>●</span> Ready
//             </span>
//           )}
//           {!wsConnected && userInfo && (
//             <span style={styles.statusIndicatorOff}>
//               <span style={styles.yellowDot}>●</span> Connecting...
//             </span>
//           )}
//         </div>
//       </div>

//       <EscalationButton token={token} onEscalationCreated={handleEscalationCreated} />

//       <div style={styles.chatBox}>
//         {messages.length === 0 && (
//           <div style={styles.emptyState}>
//             <p>Hello! How can I help you today?</p>
//             <p style={styles.emptyHint}>
//               Ask about orders, deliveries, refunds, or any issues you're experiencing.
//             </p>
//           </div>
//         )}
        
//         {messages.map((msg, i) => (
//           <div key={i}>
//             <div 
//               style={{
//                 ...styles.message,
//                 ...(msg.sender === "user" 
//                   ? styles.userMessage 
//                   : msg.sender === "system" 
//                   ? styles.systemMessage 
//                   : styles.botMessage)
//               }}
//             >
//               {msg.isAgent && <span style={styles.agentBadge}>Agent</span>}
//               <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
//               {msg.timestamp && (
//                 <div style={styles.timestamp}>
//                   {new Date(msg.timestamp).toLocaleTimeString()}
//                 </div>
//               )}
//             </div>
//           </div>
//         ))}
        
//         {loading && (
//           <div style={styles.loadingMessage}>
//             <div style={styles.typingDots}>
//               <span>.</span><span>.</span><span>.</span>
//             </div>
//           </div>
//         )}
        
//         <div ref={messagesEndRef} />
//       </div>

//       <div style={styles.inputArea}>
//         <input
//           type="text"
//           value={input}
//           onChange={e => setInput(e.target.value)}
//           onKeyDown={e => e.key === "Enter" && !loading && sendMessage()}
//           placeholder={
//             escalationId && wsConnected 
//               ? "Message the agent..." 
//               : escalationId && !wsConnected 
//               ? "Connecting to agent..." 
//               : "Type your message..."
//           }
//           disabled={loading || (escalationId && !wsConnected)}
//           style={styles.input}
//         />
//         <button 
//           onClick={sendMessage} 
//           disabled={loading || !input.trim() || (escalationId && !wsConnected)} 
//           style={{
//             ...styles.sendButton,
//             ...((loading || !input.trim() || (escalationId && !wsConnected)) 
//               ? styles.sendButtonDisabled 
//               : {})
//           }}
//         >
//           {loading ? "..." : "Send"}
//         </button>
//       </div>

//       <FeedbackModal
//         show={showFeedbackModal}
//         onClose={() => setShowFeedbackModal(false)}
//         onSubmit={() => {}}
//         sessionId={currentSessionId}
//       />
//     </div>
//   );
// }

// const styles = {
//   container: { 
//     maxWidth: "1200px", 
//     margin: "0 auto", 
//     padding: "20px", 
//     fontFamily: "'Inter', sans-serif",
//     height: "calc(100vh - 40px)",
//     display: "flex",
//     flexDirection: "column"
//   },
//   header: { 
//     display: "flex", 
//     justifyContent: "space-between", 
//     alignItems: "center", 
//     marginBottom: "15px",
//     paddingBottom: "15px",
//     borderBottom: "2px solid #e0e0e0"
//   },
//   title: { 
//     margin: 0, 
//     fontSize: "1.5rem", 
//     color: "#333" 
//   },
//   modeIndicator: { 
//     margin: "4px 0 0 0", 
//     fontSize: "0.85rem", 
//     color: "#4caf50", 
//     fontWeight: "500" 
//   },
//   statusContainer: { 
//     display: "flex", 
//     gap: "0.5rem" 
//   },
//   statusIndicator: { 
//     display: "flex", 
//     alignItems: "center", 
//     gap: "0.5rem", 
//     fontSize: "0.9rem", 
//     color: "#666", 
//     background: "#e8f5e9", 
//     padding: "0.5rem 1rem", 
//     borderRadius: "20px", 
//     fontWeight: "500" 
//   },
//   statusIndicatorGray: { 
//     display: "flex", 
//     alignItems: "center", 
//     gap: "0.5rem", 
//     fontSize: "0.9rem", 
//     color: "#666", 
//     background: "#f5f5f5", 
//     padding: "0.5rem 1rem", 
//     borderRadius: "20px" 
//   },
//   statusIndicatorOff: { 
//     display: "flex", 
//     alignItems: "center", 
//     gap: "0.5rem", 
//     fontSize: "0.9rem", 
//     color: "#666", 
//     background: "#fff3e0", 
//     padding: "0.5rem 1rem", 
//     borderRadius: "20px" 
//   },
//   greenDot: { 
//     color: "#4caf50", 
//     fontSize: "1.2rem" 
//   },
//   grayDot: { 
//     color: "#999", 
//     fontSize: "1.2rem" 
//   },
//   yellowDot: { 
//     color: "#ff9800", 
//     fontSize: "1.2rem" 
//   },
//   chatBox: { 
//     border: "1px solid #ddd", 
//     borderRadius: "12px", 
//     flex: 1,
//     overflowY: "auto", 
//     padding: "24px", 
//     marginBottom: "15px", 
//     backgroundColor: "#fafafa",
//     minHeight: 0
//   },
//   emptyState: { 
//     textAlign: "center", 
//     padding: "4rem 2rem", 
//     color: "#666" 
//   },
//   emptyHint: { 
//     fontSize: "0.9rem", 
//     color: "#999", 
//     marginTop: "0.5rem" 
//   },
//   message: { 
//     padding: "14px 18px", 
//     marginBottom: "14px", 
//     borderRadius: "12px", 
//     maxWidth: "85%", 
//     wordWrap: "break-word", 
//     lineHeight: "1.6",
//     fontSize: "0.95rem",
//   },
//   userMessage: { 
//     backgroundColor: "#667eea", 
//     color: "white", 
//     marginLeft: "auto", 
//     borderBottomRightRadius: "4px",
//     maxWidth: "70%"
//   },
//   botMessage: { 
//     backgroundColor: "white", 
//     color: "#333", 
//     border: "1px solid #e0e0e0", 
//     borderBottomLeftRadius: "4px",
//     maxWidth: "85%"
//   },
//   systemMessage: { 
//     backgroundColor: "#fff3cd", 
//     color: "#856404", 
//     border: "1px solid #ffc107", 
//     textAlign: "center", 
//     margin: "1rem auto", 
//     maxWidth: "85%",
//     fontSize: "0.9rem"
//   },
//   agentBadge: { 
//     display: "inline-block", 
//     background: "#4caf50", 
//     color: "white", 
//     padding: "3px 10px", 
//     borderRadius: "12px", 
//     fontSize: "0.75rem", 
//     fontWeight: "600", 
//     marginBottom: "6px" 
//   },
//   timestamp: { 
//     fontSize: "0.7rem", 
//     color: "#999", 
//     marginTop: "6px",
//     textAlign: "right"
//   },
//   loadingMessage: { 
//     backgroundColor: "white", 
//     color: "#666", 
//     padding: "12px 16px", 
//     borderRadius: "12px", 
//     maxWidth: "75px", 
//     border: "1px solid #e0e0e0" 
//   },
//   typingDots: { 
//     display: "flex", 
//     gap: "4px", 
//     fontSize: "1.5rem" 
//   },
//   inputArea: { 
//     display: "flex", 
//     gap: "12px",
//     padding: "8px 0"
//   },
//   input: { 
//     flex: 1, 
//     padding: "14px 18px", 
//     border: "2px solid #ddd", 
//     borderRadius: "10px", 
//     fontSize: "1rem", 
//     outline: "none", 
//     transition: "border-color 0.2s",
//     fontFamily: "'Inter', sans-serif"
//   },
//   sendButton: { 
//     padding: "14px 40px", 
//     backgroundColor: "#667eea", 
//     color: "white", 
//     border: "none", 
//     borderRadius: "10px", 
//     cursor: "pointer", 
//     fontSize: "1rem", 
//     fontWeight: "600", 
//     transition: "all 0.2s",
//     minWidth: "120px"
//   },
//   sendButtonDisabled: { 
//     backgroundColor: "#ccc", 
//     cursor: "not-allowed" 
//   }
// };

// export default ChatWindow;



import React, { useState, useEffect, useRef } from "react";
import EscalationButton from './EscalationButton';
import FeedbackModal from './FeedbackModal';
import API_BASE_URL, { WS_BASE_URL } from "./config";

function ChatWindow({ token, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [escalationId, setEscalationId] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const escalationIdRef = useRef(null);
  const heartbeatIntervalRef = useRef(null);
  const feedbackCheckTimeoutRef = useRef(null);

  useEffect(() => {
    escalationIdRef.current = escalationId;
  }, [escalationId]);

  useEffect(() => {
    fetchUserInfo();
    checkForExistingEscalation();
    return () => {
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
      if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [token]);

  useEffect(() => scrollToBottom(), [messages]);

  useEffect(() => {
    if (userInfo?.user_id && !wsConnected && !wsRef.current) {
      connectWebSocket(userInfo.user_id);
    }
  }, [userInfo]);

  useEffect(() => {
    if (messages.length > 0 && !escalationId && !feedbackSubmitted && !isLoggingOut) {
      const lastMsg = messages[messages.length - 1];
      if (lastMsg.sender === "bot") {
        const botText = lastMsg.text.toLowerCase();
        const goodbyePatterns = [
          "welcome", "have a great day", "have a good day", 
          "glad to help", "happy to help", "pleasure helping",
          "if you need anything", "feel free to reach out"
        ];
        const isGoodbyeMessage = goodbyePatterns.some(pattern => botText.includes(pattern));
        if (isGoodbyeMessage) {
          if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
          feedbackCheckTimeoutRef.current = setTimeout(() => {
            checkFeedbackPrompt();
          }, 2000);
        }
      }
    }
    return () => {
      if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
    };
  }, [messages, escalationId, feedbackSubmitted, isLoggingOut]);

  const fetchUserInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setUserInfo(data);
      }
    } catch (error) {
      console.error("Error fetching user info:", error);
    }
  };

  const checkForExistingEscalation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/escalation/escalations/my`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        const activeEscalation = data.escalations?.find(
          esc => esc.status !== 'resolved' && esc.status !== 'closed'
        );
        if (activeEscalation) {
          setEscalationId(activeEscalation.escalation_id);
          escalationIdRef.current = activeEscalation.escalation_id;
          await loadEscalationHistory(activeEscalation.escalation_id);
          setMessages(prev => [...prev, {
            sender: "system",
            text: `Resuming your support session (Case #${activeEscalation.escalation_id.slice(0, 8)})`,
            timestamp: new Date().toISOString()
          }]);
        }
      }
    } catch (error) {
      console.error("Error checking for existing escalations:", error);
    }
  };

  const loadEscalationHistory = async (escId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/escalation/messages/${escId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        const formattedMessages = data.messages.map(msg => ({
          sender: msg.sender === 'agent' ? 'bot' : 'user',
          text: msg.message,
          timestamp: msg.timestamp,
          isAgent: msg.sender === 'agent',
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error("Error loading escalation history:", error);
    }
  };

  const checkFeedbackPrompt = async () => {
    if (!userInfo?.user_id || feedbackSubmitted || escalationId || isLoggingOut) return;
    try {
      const response = await fetch(
        `${API_BASE_URL}/feedback/check-prompt/${userInfo.user_id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.ok) {
        const data = await response.json();
        if (data.should_ask && data.session_id && !isLoggingOut) {
          setCurrentSessionId(data.session_id);
          setShowFeedbackModal(true);
        }
      }
    } catch (error) {
      console.error("Error checking feedback prompt:", error);
    }
  };

  const handleFeedbackSubmit = async (feedbackData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/feedback/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(feedbackData)
      });
      if (response.ok) {
        setShowFeedbackModal(false);
        setFeedbackSubmitted(true);
        setMessages(prev => [...prev, {
          sender: "system",
          text: "Thank you for your feedback!",
          timestamp: new Date().toISOString()
        }]);
      } else {
        alert("Failed to submit feedback.");
      }
    } catch (error) {
      alert("Connection error.");
    }
  };

  const handleFeedbackClose = () => {
    setShowFeedbackModal(false);
    if (isLoggingOut) proceedWithLogout();
  };

  const handleLogoutClick = () => {
    if (showFeedbackModal) {
      setIsLoggingOut(true);
      setShowFeedbackModal(false);
      return;
    }
    proceedWithLogout();
  };

  const proceedWithLogout = () => {
    if (feedbackCheckTimeoutRef.current) clearTimeout(feedbackCheckTimeoutRef.current);
    if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
    if (wsRef.current) wsRef.current.close();
    if (onLogout) onLogout();
  };

  const connectWebSocket = (userId) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;
    if (wsRef.current) wsRef.current.close();

    const ws = new WebSocket(`${WS_BASE_URL}/escalation/ws/user/${userId}`);

    ws.onopen = () => {
      setWsConnected(true);
      if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'ping') {
          ws.send(JSON.stringify({ type: 'pong' }));
          return;
        }
        if (data.type === 'agent_message') {
          setMessages(prev => [...prev, {
            sender: "bot",
            text: data.message,
            timestamp: data.timestamp,
            isAgent: true
          }]);
        } else if (data.type === 'error') {
          setMessages(prev => [...prev, {
            sender: "system",
            text: `Error: ${data.message}`,
            timestamp: new Date().toISOString()
          }]);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = () => setWsConnected(false);

    ws.onclose = (event) => {
      setWsConnected(false);
      wsRef.current = null;
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }
      if (event.code !== 1000 && userInfo?.user_id && !isLoggingOut) {
        setTimeout(() => connectWebSocket(userInfo.user_id), 3000);
      }
    };

    wsRef.current = ws;
  };

  const handleEscalationCreated = (escId) => {
    if (escalationIdRef.current) {
      alert("You already have an active support session.");
      return;
    }
    setEscalationId(escId);
    escalationIdRef.current = escId;
    if (userInfo?.user_id && !wsConnected) connectWebSocket(userInfo.user_id);
    setMessages(prev => [...prev, {
      sender: "system",
      text: "You've been connected to a live support agent. They will assist you shortly.",
      timestamp: new Date().toISOString()
    }]);
  };

  const handleOrderClick = async (orderId) => {
    setMessages(prev => [...prev, { 
      sender: "user", 
      text: orderId, 
      timestamp: new Date().toISOString() 
    }]);

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json", 
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ message: orderId }),
      });
      
      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { 
          sender: "bot", 
          text: data.reply, 
          timestamp: new Date().toISOString() 
        }]);
      }
    } catch (error) {
      console.error("Error fetching order details:", error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { 
      sender: "user", 
      text: userMessage, 
      timestamp: new Date().toISOString() 
    }]);

    const currentEscalationId = escalationIdRef.current;

    if (currentEscalationId) {
      if (wsConnected && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ 
          type: "message", 
          escalation_id: currentEscalationId, 
          message: userMessage 
        }));
      } else {
        if (userInfo?.user_id) connectWebSocket(userInfo.user_id);
        setMessages(prev => [...prev, {
          sender: "system",
          text: "Connecting to support agent...",
          timestamp: new Date().toISOString()
        }]);
      }
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json", 
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ message: userMessage }),
      });
      
      if (res.ok) {
        const data = await res.json();
        console.log("Full API response:", data);
        
        if (data.reply === "ORDER_LIST" && data.orders && Array.isArray(data.orders)) {
          console.log("Displaying orders:", data.orders);
          setMessages(prev => [...prev, { 
            sender: "bot", 
            text: "Here are your recent orders:",
            orders: data.orders,
            timestamp: new Date().toISOString() 
          }]);
        } else {
          setMessages(prev => [...prev, { 
            sender: "bot", 
            text: data.reply, 
            timestamp: new Date().toISOString() 
          }]);

          const escMatch = data.reply.match(/ESC_\d+/);
          if (escMatch) {
            const foundEscId = escMatch[0];
            setEscalationId(foundEscId);
            escalationIdRef.current = foundEscId;
            if (userInfo?.user_id && (!wsConnected || wsRef.current.readyState !== WebSocket.OPEN)) {
              connectWebSocket(userInfo.user_id);
            }
            setMessages(prev => [...prev, {
              sender: "system",
              text: "You are now connected to live support.",
              timestamp: new Date().toISOString()
            }]);
          }
        }
      } else {
        setMessages(prev => [...prev, { 
          sender: "bot", 
          text: "Sorry, an error occurred. Please try again.", 
          timestamp: new Date().toISOString() 
        }]);
      }
    } catch (error) {
      console.error("Send message error:", error);
      setMessages(prev => [...prev, { 
        sender: "bot", 
        text: "Connection error. Check your internet.", 
        timestamp: new Date().toISOString() 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const getStatusColor = (status) => {
    const s = status.toLowerCase();
    if (s.includes('delivered')) return '#4caf50';
    if (s.includes('delivery')) return '#2196f3';
    if (s.includes('preparing') || s.includes('processing')) return '#ff9800';
    if (s.includes('cancelled')) return '#f44336';
    return '#757575';
  };

  const getStatusEmoji = (status) => {
    const s = status.toLowerCase();
    if (s.includes('delivered')) return '✓';
    if (s.includes('delivery')) return '🚚';
    if (s.includes('preparing') || s.includes('processing')) return '🍳';
    if (s.includes('ready')) return '✅';
    if (s.includes('cancelled')) return '✗';
    return '📦';
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>
            {escalationId ? "Live Agent Support" : "AI Support Assistant"}
          </h2>
          {escalationId && (
            <p style={styles.modeIndicator}>
              You are now chatting with a human support agent
            </p>
          )}
        </div>
        <div style={styles.statusContainer}>
          {wsConnected && escalationId && (
            <span style={styles.statusIndicator}>
              <span style={styles.greenDot}>●</span> Agent Online
            </span>
          )}
          {wsConnected && !escalationId && (
            <span style={styles.statusIndicatorGray}>
              <span style={styles.grayDot}>●</span> Ready
            </span>
          )}
          {!wsConnected && userInfo && (
            <span style={styles.statusIndicatorOff}>
              <span style={styles.yellowDot}>●</span> Connecting...
            </span>
          )}
        </div>
      </div>

      <EscalationButton token={token} onEscalationCreated={handleEscalationCreated} />

      <div style={styles.chatBox}>
        {messages.length === 0 && (
          <div style={styles.emptyState}>
            <p>Hello! How can I help you today?</p>
            <p style={styles.emptyHint}>
              Ask about orders, deliveries, refunds, or any issues you're experiencing.
            </p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div key={i}>
            <div 
              style={{
                ...styles.message,
                ...(msg.sender === "user" 
                  ? styles.userMessage 
                  : msg.sender === "system" 
                  ? styles.systemMessage 
                  : styles.botMessage)
              }}
            >
              {msg.isAgent && <span style={styles.agentBadge}>Agent</span>}
              <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
              {msg.timestamp && (
                <div style={styles.timestamp}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>

            {msg.orders && msg.orders.length > 0 && (
              <div style={styles.orderCardsContainer}>
                {msg.orders.map((order, idx) => (
                  <div 
                    key={idx} 
                    style={styles.orderCard}
                    onClick={() => handleOrderClick(order.order_id)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-2px)';
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.15)';
                      e.currentTarget.style.borderColor = '#667eea';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                      e.currentTarget.style.borderColor = '#e0e0e0';
                    }}
                  >
                    <div style={styles.orderHeader}>
                      <div style={styles.orderRestaurant}>
                        🍽️ {order.restaurant}
                      </div>
                      <div 
                        style={{
                          ...styles.orderStatus,
                          backgroundColor: getStatusColor(order.status)
                        }}
                      >
                        {getStatusEmoji(order.status)} {order.status}
                      </div>
                    </div>

                    <div style={styles.orderItems}>
                      <strong>Items:</strong> {order.items.slice(0, 3).join(', ')}
                      {order.items.length > 3 && ` +${order.items.length - 3} more`}
                    </div>

                    <div style={styles.orderDetails}>
                      <div style={styles.orderDetailRow}>
                        <span>📅 {order.order_date}</span>
                      </div>
                      <div style={styles.orderDetailRow}>
                        <span>📍 {order.delivery_address}</span>
                      </div>
                      <div style={styles.orderDetailRow}>
                        <span style={styles.orderTotal}>💵 ${order.total_amount}</span>
                      </div>
                    </div>

                    <div style={styles.orderFooter}>
                      Order ID: {order.order_id.slice(0, 8)}...
                    </div>

                    <div style={styles.clickHint}>
                      Click to view full details
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        
        {loading && (
          <div style={styles.loadingMessage}>
            <div style={styles.typingDots}>
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputArea}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !loading && sendMessage()}
          placeholder={
            escalationId && wsConnected 
              ? "Message the agent..." 
              : escalationId && !wsConnected 
              ? "Connecting to agent..." 
              : "Type your message..."
          }
          disabled={loading || (escalationId && !wsConnected)}
          style={styles.input}
        />
        <button 
          onClick={sendMessage} 
          disabled={loading || !input.trim() || (escalationId && !wsConnected)} 
          style={{
            ...styles.sendButton,
            ...(loading || !input.trim() || (escalationId && !wsConnected) 
              ? styles.sendButtonDisabled 
              : {})
          }}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>

      <FeedbackModal
        show={showFeedbackModal}
        onClose={handleFeedbackClose}
        onSubmit={handleFeedbackSubmit}
        sessionId={currentSessionId}
      />
    </div>
  );
}

const styles = {
  container: { 
    maxWidth: "1200px", 
    margin: "0 auto", 
    padding: "20px", 
    fontFamily: "'Inter', sans-serif",
    height: "calc(100vh - 40px)",
    display: "flex",
    flexDirection: "column"
  },
  header: { 
    display: "flex", 
    justifyContent: "space-between", 
    alignItems: "center", 
    marginBottom: "15px",
    paddingBottom: "15px",
    borderBottom: "2px solid #e0e0e0"
  },
  title: { 
    margin: 0, 
    fontSize: "1.5rem", 
    color: "#333" 
  },
  modeIndicator: { 
    margin: "4px 0 0 0", 
    fontSize: "0.85rem", 
    color: "#4caf50", 
    fontWeight: "500" 
  },
  statusContainer: { 
    display: "flex", 
    gap: "0.5rem" 
  },
  statusIndicator: { 
    display: "flex", 
    alignItems: "center", 
    gap: "0.5rem", 
    fontSize: "0.9rem", 
    color: "#666", 
    background: "#e8f5e9", 
    padding: "0.5rem 1rem", 
    borderRadius: "20px", 
    fontWeight: "500" 
  },
  statusIndicatorGray: { 
    display: "flex", 
    alignItems: "center", 
    gap: "0.5rem", 
    fontSize: "0.9rem", 
    color: "#666", 
    background: "#f5f5f5", 
    padding: "0.5rem 1rem", 
    borderRadius: "20px" 
  },
  statusIndicatorOff: { 
    display: "flex", 
    alignItems: "center", 
    gap: "0.5rem", 
    fontSize: "0.9rem", 
    color: "#666", 
    background: "#fff3e0", 
    padding: "0.5rem 1rem", 
    borderRadius: "20px" 
  },
  greenDot: { 
    color: "#4caf50", 
    fontSize: "1.2rem" 
  },
  grayDot: { 
    color: "#999", 
    fontSize: "1.2rem" 
  },
  yellowDot: { 
    color: "#ff9800", 
    fontSize: "1.2rem" 
  },
  chatBox: { 
    border: "1px solid #ddd", 
    borderRadius: "12px", 
    flex: 1,
    overflowY: "auto", 
    padding: "24px", 
    marginBottom: "15px", 
    backgroundColor: "#fafafa",
    minHeight: 0
  },
  emptyState: { 
    textAlign: "center", 
    padding: "4rem 2rem", 
    color: "#666" 
  },
  emptyHint: { 
    fontSize: "0.9rem", 
    color: "#999", 
    marginTop: "0.5rem" 
  },
  message: { 
    padding: "14px 18px", 
    marginBottom: "14px", 
    borderRadius: "12px", 
    maxWidth: "85%", 
    wordWrap: "break-word", 
    lineHeight: "1.6",
    fontSize: "0.95rem",
    minWidth: "300px"
  },
  userMessage: { 
    backgroundColor: "#667eea", 
    color: "white", 
    marginLeft: "auto", 
    borderBottomRightRadius: "4px",
    maxWidth: "70%"
  },
  botMessage: { 
    backgroundColor: "white", 
    color: "#333", 
    border: "1px solid #e0e0e0", 
    borderBottomLeftRadius: "4px",
    maxWidth: "85%"
  },
  systemMessage: { 
    backgroundColor: "#fff3cd", 
    color: "#856404", 
    border: "1px solid #ffc107", 
    textAlign: "center", 
    margin: "1rem auto", 
    maxWidth: "85%",
    fontSize: "0.9rem"
  },
  agentBadge: { 
    display: "inline-block", 
    background: "#4caf50", 
    color: "white", 
    padding: "3px 10px", 
    borderRadius: "12px", 
    fontSize: "0.75rem", 
    fontWeight: "600", 
    marginBottom: "6px" 
  },
  timestamp: { 
    fontSize: "0.7rem", 
    color: "#999", 
    marginTop: "6px" 
  },
  loadingMessage: { 
    backgroundColor: "white", 
    color: "#666", 
    padding: "12px 16px", 
    borderRadius: "12px", 
    maxWidth: "75px", 
    border: "1px solid #e0e0e0" 
  },
  typingDots: { 
    display: "flex", 
    gap: "4px", 
    fontSize: "1.5rem" 
  },
  inputArea: { 
    display: "flex", 
    gap: "12px",
    padding: "8px 0"
  },
  input: { 
    flex: 1, 
    padding: "14px 18px", 
    border: "2px solid #ddd", 
    borderRadius: "10px", 
    fontSize: "1rem", 
    outline: "none", 
    transition: "border-color 0.2s",
    fontFamily: "'Inter', sans-serif"
  },
  sendButton: { 
    padding: "14px 40px", 
    backgroundColor: "#667eea", 
    color: "white", 
    border: "none", 
    borderRadius: "10px", 
    cursor: "pointer", 
    fontSize: "1rem", 
    fontWeight: "600", 
    transition: "all 0.2s",
    minWidth: "120px"
  },
  sendButtonDisabled: { 
    backgroundColor: "#ccc", 
    cursor: "not-allowed" 
  },
  orderCardsContainer: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
    gap: "1.25rem",
    marginTop: "0.75rem",
    marginBottom: "1rem",
    width: "100%"
  },
  orderCard: {
    backgroundColor: "white",
    border: "2px solid #e0e0e0",
    borderRadius: "12px",
    padding: "1.25rem",
    cursor: "pointer",
    transition: "all 0.3s ease",
    boxShadow: "0 2px 6px rgba(0,0,0,0.08)"
  },
  orderHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "0.875rem"
  },
  orderRestaurant: {
    fontWeight: "600",
    fontSize: "1.05rem",
    color: "#333",
    flex: 1
  },
  orderStatus: {
    padding: "0.35rem 0.65rem",
    borderRadius: "6px",
    fontSize: "0.8rem",
    fontWeight: "600",
    color: "white",
    whiteSpace: "nowrap",
    marginLeft: "0.75rem"
  },
  orderItems: {
    fontSize: "0.9rem",
    color: "#666",
    marginBottom: "0.875rem",
    lineHeight: "1.5"
  },
  orderDetails: {
    display: "flex",
    flexDirection: "column",
    gap: "0.35rem",
    marginBottom: "0.875rem",
    fontSize: "0.85rem",
    color: "#555"
  },
  orderDetailRow: {
    display: "flex",
    alignItems: "center"
  },
  orderTotal: {
    fontWeight: "700",
    fontSize: "0.95rem",
    color: "#333"
  },
  orderFooter: {
    fontSize: "0.8rem",
    color: "#999",
    borderTop: "1px solid #f0f0f0",
    paddingTop: "0.65rem",
    marginTop: "0.65rem"
  },
  clickHint: {
    fontSize: "0.75rem",
    color: "#667eea",
    textAlign: "center",
    marginTop: "0.65rem",
    fontStyle: "italic"
  }
};

export default ChatWindow;