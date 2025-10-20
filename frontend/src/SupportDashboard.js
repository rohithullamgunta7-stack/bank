
import React, { useState, useEffect, useRef } from "react";

import API_BASE_URL from "./config";
import WS_BASE_URL from "./config";

function SupportDashboard({ token, userInfo }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const [pendingEscalations, setPendingEscalations] = useState([]);
  const [myEscalations, setMyEscalations] = useState([]);
  
  // --- FIX: Pt 1 - Rename state setter ---
  const [activeChat, _setActiveChat] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [wsConnected, setWsConnected] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);
  
  // --- FIX: Pt 2 - Create ref and new setter function ---
  const activeChatRef = useRef(activeChat);
  const setActiveChat = (data) => {
    _setActiveChat(data);
    activeChatRef.current = data;
  };

  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    fetchDashboardData();
    fetchEscalations();
    
    if (userInfo?.user_id) {
      connectWebSocket();
    }

    const interval = setInterval(() => {
      if (activeTab === "escalations" || activeTab === "overview") {
        fetchEscalations();
      }
    }, 10000);

    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [token, userInfo]);

  useEffect(() => {
    if (activeTab === "escalations") {
      fetchEscalations();
    }
  }, [activeTab]);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const connectWebSocket = () => {
    if (!userInfo?.user_id) {
      console.log("⚠️ Cannot connect WebSocket: userInfo.user_id is missing");
      return;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    const wsUrl = `${WS_BASE_URL}/escalation/ws/agent/${userInfo.user_id}`;
    console.log("🔌 Attempting to connect Agent WebSocket to:", wsUrl);

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setWsConnected(true);
      console.log("✅ Agent WebSocket connected");
      
      const pingInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "ping" }));
        } else {
          clearInterval(pingInterval);
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("📨 Agent WebSocket message received:", data);

        if (data.type === "pong") {
          return;
        }

        if (data.type === "new_escalation") {
          console.log("🚨 New escalation notification:", data.escalation);
          fetchEscalations();
          
          if (Notification.permission === "granted") {
            new Notification("New Escalation", {
              body: data.escalation.reason,
              icon: "/favicon.ico"
            });
          }
        } else if (data.type === "user_message") {
          console.log("💬 User message received:", data.message);
          
          // --- FIX: Pt 3 - Use ref to check active chat ---
          if (activeChatRef.current?.escalation_id === data.escalation_id) {
            const messageId = `${data.timestamp}-user`;
            setChatMessages((prev) => {
              // Avoid duplicates
              if (prev.some(m => m.id === messageId)) {
                return prev;
              }
              return [
                ...prev,
                {
                  sender: "user",
                  message: data.message,
                  timestamp: data.timestamp,
                  id: messageId
                },
              ];
            });
          }
          
          fetchEscalations();
        } else if (data.type === "ack") {
          console.log("✓ Message acknowledged:", data.message);
          setSendingMessage(false);
        } else if (data.type === "error") {
          console.error("❌ WebSocket error:", data.message);
          alert(`Error: ${data.message}`);
          setSendingMessage(false);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("❌ Agent WebSocket error:", error);
      setWsConnected(false);
    };

    ws.onclose = () => {
      setWsConnected(false);
      console.log("🔌 Agent WebSocket disconnected");
      
      reconnectTimeoutRef.current = setTimeout(() => {
        if (userInfo?.user_id) {
          console.log("🔄 Attempting to reconnect Agent WebSocket...");
          connectWebSocket();
        }
      }, 5000);
    };

    wsRef.current = ws;
  };

  const fetchDashboardData = async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);

      const response = await fetch(`${API_BASE_URL}/dashboard`, {
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

  const fetchEscalations = async () => {
    try {
      const pendingRes = await fetch(
        `${API_BASE_URL}/escalation/escalations/pending`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (pendingRes.ok) {
        const pendingData = await pendingRes.json();
        setPendingEscalations(pendingData.escalations || []);
      }

      const myRes = await fetch(
        `${API_BASE_URL}/escalation/escalations/assigned`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (myRes.ok) {
        const myData = await myRes.json();
        setMyEscalations(myData.escalations || []);
      }
    } catch (error) {
      console.error("Error fetching escalations:", error);
    }
  };

  const claimEscalation = async (escalationId) => {
    if (!window.confirm("Do you want to claim this escalation?")) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/escalation/${escalationId}/assign`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        alert(data.message || "Escalation claimed successfully!");
        fetchEscalations();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to claim escalation");
      }
    } catch (error) {
      console.error("Error claiming escalation:", error);
      alert("Connection error");
    }
  };

  const openChat = async (escalation) => {
    setActiveChat(escalation); // This now uses the new setter
    setChatMessages([]);

    try {
      const response = await fetch(
        `${API_BASE_URL}/escalation/messages/${escalation.escalation_id}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        const formattedMessages = data.messages.map((msg) => ({
          sender: msg.sender,
          message: msg.message,
          timestamp: msg.timestamp,
          id: `${msg.timestamp}-${msg.sender}`
        }));
        setChatMessages(formattedMessages);
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
    }
  };

  const sendMessage = async () => {
    if (!chatInput.trim() || !activeChat || sendingMessage) return;

    const messageText = chatInput.trim();
    const messageId = `agent-${Date.now()}-${Math.random()}`;
    setChatInput("");
    setSendingMessage(true);

    // Add message to UI immediately
    const newMessage = {
      sender: "agent",
      message: messageText,
      timestamp: new Date().toISOString(),
      id: messageId
    };
    
    setChatMessages((prev) => [...prev, newMessage]);

    try {
      // Try WebSocket first
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        console.log("📤 Sending via WebSocket:", messageText);
        wsRef.current.send(
          JSON.stringify({
            type: "message",
            escalation_id: activeChat.escalation_id,
            message: messageText,
          })
        );
        // setSendingMessage will be set to false when we receive 'ack'
      } else {
        // Fallback to REST API
        console.log("📤 WebSocket not connected, using REST API");
        const response = await fetch(
          `${API_BASE_URL}/escalation/${
            activeChat.escalation_id
          }/message?message=${encodeURIComponent(messageText)}`,
          {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        if (!response.ok) {
          alert("Failed to send message");
          // Remove the message from UI
          setChatMessages((prev) => prev.filter(m => m.id !== messageId));
        }
        setSendingMessage(false);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Connection error");
      // Remove the message from UI
      setChatMessages((prev) => prev.filter(m => m.id !== messageId));
      setSendingMessage(false);
    }
  };

  const permanentlyBlockCard = async () => {
    if (!activeChat) return;

    const context = activeChat.context;
    if (!context || !context.block_type || context.block_type !== "permanent") {
      alert("This escalation is not for permanent card blocking");
      return;
    }

    const reason = prompt(
      "Enter reason for permanent card cancellation (required for audit):"
    );
    if (!reason || reason.trim().length < 10) {
      alert("Please provide a detailed reason (minimum 10 characters)");
      return;
    }

    if (
      !window.confirm(
        `⚠️ PERMANENT CARD CANCELLATION\n\n` +
          `Card Type: ${context.card_type}\n` +
          `Account: ${context.account_number}\n\n` +
          `This action CANNOT be undone!\n` +
          `User will need to apply for a new card.\n\n` +
          `Continue?`
      )
    ) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/cards/block-permanent/${context.account_id}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ reason: reason.trim() }),
        }
      );

      if (response.ok) {
        const data = await response.json();

        const confirmMsg =
          `✅ CARD PERMANENTLY CANCELLED\n\n` +
          `Your ${context.card_type} has been permanently cancelled.\n\n` +
          `Account: ${context.account_number}\n` +
          `Cancelled by: ${data.cancelled_by}\n` +
          `Reason: ${reason}\n\n` +
          `📝 Next Steps:\n` +
          `1. Your card is now completely blocked\n` +
          `2. A new card application has been initiated\n` +
          `3. You'll receive your new card in 7-10 business days\n` +
          `4. New card will have a different number\n\n` +
          `Keep this Case ID for reference: ${activeChat.escalation_id.slice(
            0,
            12
          )}`;

        const messageId = `agent-${Date.now()}`;
        // Add to chat UI
        setChatMessages((prev) => [
          ...prev,
          {
            sender: "agent",
            message: confirmMsg,
            timestamp: new Date().toISOString(),
            id: messageId
          },
        ]);

        // Send via WebSocket or REST API
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: "message",
              escalation_id: activeChat.escalation_id,
              message: confirmMsg,
            })
          );
        } else {
          await fetch(
            `${API_BASE_URL}/escalation/${
              activeChat.escalation_id
            }/message?message=${encodeURIComponent(confirmMsg)}`,
            {
              method: "POST",
              headers: { Authorization: `Bearer ${token}` },
            }
          );
        }

        alert("✅ Card permanently blocked successfully!");
      } else {
        const error = await response.json();
        alert(`Failed to block card: ${error.detail || "Unknown error"}`);
      }
    } catch (error) {
      console.error("Error blocking card:", error);
      alert("Failed to block card. Please try again.");
    }
  };

  const resolveEscalation = async () => {
    if (!activeChat) return;

    const resolutionNotes = prompt("Enter resolution notes:");
    if (!resolutionNotes) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/escalation/${
          activeChat.escalation_id
        }/close?resolution=${encodeURIComponent(resolutionNotes)}`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        alert("Escalation resolved!");
        setActiveChat(null); // This now uses the new setter
        setChatMessages([]);
        fetchEscalations();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to resolve escalation");
      }
    } catch (error) {
      console.error("Error resolving escalation:", error);
      alert("Failed to resolve escalation");
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "critical":
        return "#f44336";
      case "high":
        return "#ff9800";
      case "medium":
        return "#2196f3";
      default:
        return "#9e9e9e";
    }
  };

  const renderEscalations = () => {
    return (
      <div style={styles.escalationsContainer}>
        <div style={styles.escalationsHeader}>
          <h2 style={styles.sectionTitle}>Escalation Management</h2>
          <div style={styles.connectionStatus}>
            <span
              style={{
                ...styles.statusDot,
                backgroundColor: wsConnected ? "#4caf50" : "#f44336",
              }}
            ></span>
            {wsConnected ? "Connected" : "Disconnected"}
          </div>
        </div>

        <div style={styles.escalationsLayout}>
          <div style={styles.escalationsList}>
            <div style={styles.section}>
              <h3 style={styles.sectionHeader}>
                Pending Escalations ({pendingEscalations.length})
              </h3>
              {pendingEscalations.length === 0 ? (
                <p style={styles.emptyText}>No pending escalations</p>
              ) : (
                pendingEscalations.map((esc) => (
                  <div key={esc.escalation_id} style={styles.escalationCard}>
                    <div style={styles.cardHeader}>
                      <span style={styles.caseId}>
                        #{esc.escalation_id.slice(0, 8)}
                      </span>
                      <span
                        style={{
                          ...styles.priorityBadge,
                          backgroundColor: getPriorityColor(esc.priority),
                        }}
                      >
                        {esc.priority?.toUpperCase() || "MEDIUM"}
                      </span>
                    </div>
                    <p style={styles.reason}>
                      <strong>Issue:</strong> {esc.reason}
                    </p>
                    <p style={styles.userInfo}>
                      <strong>Customer:</strong> {esc.context?.user_name || "N/A"}{" "}
                      ({esc.context?.user_email || "N/A"})
                    </p>
                    {esc.context?.card_type && (
                      <p style={styles.cardInfo}>
                        🔴 <strong>Card:</strong> {esc.context.card_type} -{" "}
                        {esc.context.account_number}
                      </p>
                    )}
                    <p style={styles.timestamp}>
                      Created: {new Date(esc.created_at).toLocaleString()}
                    </p>
                    <button
                      onClick={() => claimEscalation(esc.escalation_id)}
                      style={styles.claimBtn}
                    >
                      Claim This Case
                    </button>
                  </div>
                ))
              )}
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionHeader}>
                My Active Cases ({myEscalations.length})
              </h3>
              {myEscalations.length === 0 ? (
                <p style={styles.emptyText}>No active cases</p>
              ) : (
                myEscalations.map((esc) => (
                  <div
                    key={esc.escalation_id}
                    style={{
                      ...styles.escalationCard,
                      ...(activeChat?.escalation_id === esc.escalation_id
                        ? styles.activeCard
                        : {}),
                    }}
                    onClick={() => openChat(esc)}
                  >
                    <div style={styles.cardHeader}>
                      <span style={styles.caseId}>
                        #{esc.escalation_id.slice(0, 8)}
                      </span>
                      <span
                        style={{
                          ...styles.priorityBadge,
                          backgroundColor: getPriorityColor(esc.priority),
                        }}
                      >
                        {esc.priority?.toUpperCase() || "MEDIUM"}
                      </span>
                    </div>
                    <p style={styles.reason}>
                      <strong>Issue:</strong> {esc.reason}
                    </p>
                    <p style={styles.userInfo}>
                      <strong>Customer:</strong> {esc.context?.user_name || "N/A"}
                    </p>
                    {esc.context?.card_type && (
                      <p style={styles.cardInfo}>
                        🔴 <strong>Card:</strong> {esc.context.card_type}
                      </p>
                    )}
                    <button style={styles.chatBtn}>Open Chat</button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div style={styles.chatPanel}>
            {activeChat ? (
              <>
                <div style={styles.chatHeader}>
                  <div>
                    <h3 style={styles.chatTitle}>
                      Chat with {activeChat.context?.user_name || "Customer"}
                    </h3>
                    <p style={styles.chatSubtitle}>
                      Case #{activeChat.escalation_id.slice(0, 8)} -{" "}
                      {activeChat.reason}
                    </p>
                  </div>
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    {activeChat.context?.block_type === "permanent" && (
                      <button
                        onClick={permanentlyBlockCard}
                        style={styles.blockCardBtn}
                      >
                        🔴 Block Card Permanently
                      </button>
                    )}
                    <button
                      onClick={resolveEscalation}
                      style={styles.resolveBtn}
                    >
                      Resolve
                    </button>
                  </div>
                </div>

                {activeChat.context?.card_type && (
                  <div style={styles.contextPanel}>
                    <h4 style={styles.contextTitle}>
                      ⚠️ Card Blocking Request
                    </h4>

                    <div style={styles.sectionBox}>
                      <h5 style={styles.sectionBoxTitle}>
                        💳 Card Information
                      </h5>
                      <div style={styles.contextGrid}>
                        <div>
                          <strong>Card Type:</strong>{" "}
                          {activeChat.context.card_type}
                        </div>
                        <div>
                          <strong>Account Number:</strong>{" "}
                          {activeChat.context.account_number}
                        </div>
                        <div>
                          <strong>Account Type:</strong>{" "}
                          {activeChat.context.account_type}
                        </div>
                        <div>
                          <strong>Block Type:</strong>{" "}
                          <span
                            style={{ color: "#f44336", fontWeight: "bold" }}
                          >
                            {activeChat.context.block_type?.toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div style={styles.sectionBox}>
                      <h5 style={styles.sectionBoxTitle}>
                        👤 Customer Verification Details
                      </h5>
                      <div style={styles.verificationGrid}>
                        <div style={styles.verificationItem}>
                          <span style={styles.verificationLabel}>
                            Full Name:
                          </span>
                          <span style={styles.verificationValue}>
                            {activeChat.context.user_name || "N/A"}
                          </span>
                        </div>
                        <div style={styles.verificationItem}>
                          <span style={styles.verificationLabel}>Email:</span>
                          <span style={styles.verificationValue}>
                            {activeChat.context.user_email || "N/A"}
                          </span>
                        </div>
                        <div style={styles.verificationItem}>
                          <span style={styles.verificationLabel}>Phone:</span>
                          <span style={styles.verificationValue}>
                            {activeChat.context.phone_number ||
                              "Not Available"}
                          </span>
                        </div>
                        <div style={styles.verificationItem}>
                          <span style={styles.verificationLabel}>
                            Address:
                          </span>
                          <span style={styles.verificationValue}>
                            {activeChat.context.address || "Not Available"}
                          </span>
                        </div>
                        <div style={styles.verificationItem}>
                          <span style={styles.verificationLabel}>
                            Customer ID:
                          </span>
                          <span style={styles.verificationValue}>
                            {activeChat.context.customer_id || "N/A"}
                          </span>
                        </div>
                        <div style={styles.verificationItem}>
                          <span style={styles.verificationLabel}>
                            Account Opened:
                          </span>
                          <span style={styles.verificationValue}>
                            {activeChat.context.account_created_at || "N/A"}
                          </span>
                        </div>
                        {activeChat.context.kyc_status && (
                          <div style={styles.verificationItem}>
                            <span style={styles.verificationLabel}>
                              KYC Status:
                            </span>
                            <span
                              style={{
                                ...styles.verificationValue,
                                color:
                                  activeChat.context.kyc_status === "Verified"
                                    ? "#4caf50"
                                    : "#ff9800",
                                fontWeight: "600",
                              }}
                            >
                              {activeChat.context.kyc_status}
                            </span>
                          </div>
                        )}
                        {activeChat.context.customer_tier && (
                          <div style={styles.verificationItem}>
                            <span style={styles.verificationLabel}>
                              Customer Tier:
                            </span>
                            <span style={styles.verificationValue}>
                              {activeChat.context.customer_tier}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    {activeChat.context.requires_verification && (
                      <div style={styles.warningBox}>
                        ⚠️ <strong>VERIFICATION REQUIRED:</strong> Please verify
                        customer identity before blocking the card permanently.
                        <ul
                          style={{
                            marginTop: "0.5rem",
                            paddingLeft: "1.5rem",
                            fontSize: "0.85rem",
                          }}
                        >
                          <li>Verify full name matches records</li>
                          <li>Confirm last 4 digits of phone number</li>
                          <li>Ask for address details (city/postal code)</li>
                          <li>
                            Verify account opening date or recent transactions
                          </li>
                          <li>Check KYC status is Verified</li>
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                <div style={styles.messagesContainer}>
                  {chatMessages.length === 0 && (
                    <p style={styles.emptyChat}>
                      Start chatting with the customer...
                    </p>
                  )}
                  {chatMessages.map((msg, idx) => (
                    <div
                      key={msg.id || idx}
                      style={{
                        ...styles.messageRow,
                        justifyContent:
                          msg.sender === "agent" ? "flex-end" : "flex-start",
                      }}
                    >
                      <div
                        style={{
                          ...styles.messageBubble,
                          ...(msg.sender === "agent"
                            ? styles.agentMessage
                            : styles.userMessage),
                        }}
                      >
                        <div style={{ whiteSpace: "pre-wrap" }}>
                          {msg.message}
                        </div>
                        <div style={styles.messageTime}>
                          {new Date(msg.timestamp).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                <div style={styles.chatInput}>
                  <textarea
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                      }
                    }}
                    placeholder="Type your message..."
                    rows={2}
                    style={styles.textarea}
                    disabled={sendingMessage}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!chatInput.trim() || sendingMessage}
                    style={{
                      ...styles.sendBtn,
                      ...((!chatInput.trim() || sendingMessage) && styles.sendBtnDisabled),
                    }}
                  >
                    {sendingMessage ? "Sending..." : "Send"}
                  </button>
                </div>
              </>
            ) : (
              <div style={styles.noChatSelected}>
                <p>Select an escalation to start chatting</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderOverview = () => {
    if (loading) {
      return (
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>Loading support dashboard...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div style={styles.errorContainer}>
          <div style={styles.errorIcon}>⚠️</div>
          <h3 style={styles.errorTitle}>Error Loading Dashboard</h3>
          <p style={styles.errorMessage}>{error}</p>
          <button
            onClick={() => fetchDashboardData()}
            style={styles.retryButton}
          >
            Try Again
          </button>
        </div>
      );
    }

    return (
      <div style={styles.overviewSection}>
        <div style={styles.headerRow}>
          <div>
            <h2 style={styles.sectionTitle}>Support Agent Dashboard</h2>
            <p style={styles.sectionSubtitle}>
              Monitor and assist customers efficiently
            </p>
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
          <div style={{ ...styles.statCard, ...styles.statCardBlue }}>
            <div style={styles.statIcon}>💬</div>
            <div>
              <h3 style={styles.statLabel}>Active Conversations</h3>
              <div style={styles.statNumber}>
                {dashboardData?.active_conversations || 0}
              </div>
              <p style={styles.statSubtext}>Current customer chats</p>
            </div>
          </div>

          <div style={{ ...styles.statCard, ...styles.statCardOrange }}>
            <div style={styles.statIcon}>🚨</div>
            <div>
              <h3 style={styles.statLabel}>My Active Cases</h3>
              <div style={styles.statNumber}>{myEscalations.length}</div>
              <p style={styles.statSubtext}>Assigned to you</p>
            </div>
          </div>

          <div style={{ ...styles.statCard, ...styles.statCardRed }}>
            <div style={styles.statIcon}>⏰</div>
            <div>
              <h3 style={styles.statLabel}>Pending Escalations</h3>
              <div style={styles.statNumber}>{pendingEscalations.length}</div>
              <p style={styles.statSubtext}>Need attention</p>
            </div>
          </div>

          <div style={{ ...styles.statCard, ...styles.statCardGreen }}>
            <div style={styles.statIcon}>✔️</div>
            <div>
              <h3 style={styles.statLabel}>Total Conversations</h3>
              <div style={styles.statNumber}>
                {dashboardData?.conversation_summaries?.length || 0}
              </div>
              <p style={styles.statSubtext}>All time</p>
            </div>
          </div>
        </div>

        {pendingEscalations.length > 0 && (
          <div style={styles.alertBanner}>
            <span>
              ⚠️ Alert: {pendingEscalations.length} pending escalation(s) need
              attention!
            </span>
            <button
              onClick={() => setActiveTab("escalations")}
              style={styles.alertBtn}
            >
              View Now
            </button>
          </div>
        )}

        <div style={styles.guidelinesSection}>
          <h3 style={styles.guidelinesTitle}>Customer Service Guidelines</h3>
          <div style={styles.guidelinesGrid}>
            <div style={styles.guidelineCard}>
              <div style={styles.guidelineIcon}>😊</div>
              <h4 style={styles.guidelineCardTitle}>
                Be Polite & Respectful
              </h4>
              <p style={styles.guidelineText}>
                Always greet customers warmly and maintain a professional,
                courteous tone throughout the conversation.
              </p>
            </div>

            <div style={styles.guidelineCard}>
              <div style={styles.guidelineIcon}>⚡</div>
              <h4 style={styles.guidelineCardTitle}>Respond Quickly</h4>
              <p style={styles.guidelineText}>
                Acknowledge customer messages within 1-2 minutes. Quick
                responses show we value their time.
              </p>
            </div>

            <div style={styles.guidelineCard}>
              <div style={styles.guidelineIcon}>👂</div>
              <h4 style={styles.guidelineCardTitle}>Listen Actively</h4>
              <p style={styles.guidelineText}>
                Read carefully and understand the customer's issue before
                responding. Ask clarifying questions if needed.
              </p>
            </div>

            <div style={styles.guidelineCard}>
              <div style={styles.guidelineIcon}>💡</div>
              <h4 style={styles.guidelineCardTitle}>Provide Clear Solutions</h4>
              <p style={styles.guidelineText}>
                Offer specific, actionable solutions. Explain steps clearly and
                ensure the customer understands.
              </p>
            </div>

            <div style={styles.guidelineCard}>
              <div style={styles.guidelineIcon}>🤝</div>
              <h4 style={styles.guidelineCardTitle}>Show Empathy</h4>
              <p style={styles.guidelineText}>
                Acknowledge frustrations and apologize when appropriate. Put
                yourself in the customer's shoes.
              </p>
            </div>

            <div style={styles.guidelineCard}>
              <div style={styles.guidelineIcon}>✅</div>
              <h4 style={styles.guidelineCardTitle}>Follow Through</h4>
              <p style={styles.guidelineText}>
                Ensure issues are fully resolved before closing. Confirm
                customer satisfaction and offer additional help.
              </p>
            </div>
          </div>

          <div style={styles.quickTips}>
            <strong>Quick Tips:</strong> Use the customer's name when possible •
            Avoid using negative language • Take ownership of issues • Never
            blame other departments • End conversations positively
          </div>
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (activeTab) {
      case "overview":
        return renderOverview();
      case "escalations":
        return renderEscalations();
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
            ...(activeTab === "overview" ? styles.tabButtonActive : {}),
          }}
          onClick={() => setActiveTab("overview")}
        >
          <span style={styles.tabIcon}>📊</span> Overview
        </button>

        <button
          style={{
            ...styles.tabButton,
            ...(activeTab === "escalations" ? styles.tabButtonActive : {}),
          }}
          onClick={() => setActiveTab("escalations")}
        >
          <span style={styles.tabIcon}>🚨</span> Escalations
          {pendingEscalations.length > 0 && (
            <span style={styles.badge}>{pendingEscalations.length}</span>
          )}
        </button>
      </div>

      <div style={styles.content}>{renderContent()}</div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg);}
          100% { transform: rotate(360deg);}
        }
      `}</style>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "calc(100vh - 150px)",
    padding: "1rem",
    background: "#f5f7fa",
    fontFamily: "'Inter', sans-serif",
  },
  tabNav: {
    display: "flex",
    gap: "0.5rem",
    marginBottom: "2rem",
    background: "white",
    padding: "1rem",
    borderRadius: "12px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
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
    gap: "0.5rem",
    position: "relative",
  },
  tabButtonActive: {
    background: "linear-gradient(135deg, #48bb78 0%, #38a169 100%)",
    color: "white",
    boxShadow: "0 4px 12px rgba(72, 187, 120, 0.3)",
  },
  tabIcon: { fontSize: "1.2rem" },
  badge: {
    background: "#f44336",
    color: "white",
    borderRadius: "50%",
    padding: "0.2rem 0.5rem",
    fontSize: "0.75rem",
    fontWeight: "600",
    minWidth: "20px",
    textAlign: "center",
  },
  content: {
    background: "white",
    borderRadius: "12px",
    padding: "2rem",
    boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
  },
  loadingContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "3rem",
  },
  spinner: {
    width: "50px",
    height: "50px",
    border: "6px solid #f3f3f3",
    borderTop: "6px solid #48bb78",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
    marginBottom: "1rem",
  },
  loadingText: { fontSize: "1rem", color: "#555" },
  errorContainer: { textAlign: "center", padding: "2rem" },
  errorIcon: { fontSize: "2.5rem", marginBottom: "1rem" },
  errorTitle: {
    fontSize: "1.3rem",
    marginBottom: "0.5rem",
    color: "#e53e3e",
  },
  errorMessage: { fontSize: "1rem", marginBottom: "1rem", color: "#555" },
  retryButton: {
    padding: "0.5rem 1rem",
    background: "#48bb78",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
  overviewSection: { display: "flex", flexDirection: "column", gap: "2rem" },
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  sectionTitle: { margin: 0, fontSize: "1.6rem" },
  sectionSubtitle: { margin: 0, fontSize: "0.95rem", color: "#555" },
  refreshButton: {
    padding: "0.5rem 1rem",
    background: "#38a169",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "1rem",
  },
  statCard: {
    display: "flex",
    alignItems: "center",
    gap: "1rem",
    padding: "1rem",
    borderRadius: "12px",
    color: "white",
  },
  statCardBlue: { background: "#4299e1" },
  statCardOrange: { background: "#ed8936" },
  statCardRed: { background: "#f56565" },
  statCardGreen: { background: "#48bb78" },
  statIcon: { fontSize: "2rem" },
  statLabel: { margin: 0, fontSize: "1rem" },
  statNumber: { fontSize: "1.5rem", fontWeight: "600" },
  statSubtext: { fontSize: "0.8rem" },
  alertBanner: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "1rem",
    background: "#fff3cd",
    border: "1px solid #ffc107",
    borderRadius: "8px",
    color: "#856404",
  },
  alertBtn: {
    padding: "0.5rem 1rem",
    background: "#ffc107",
    color: "#856404",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "600",
  },
  escalationsContainer: {},
  escalationsHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "2rem",
  },
  connectionStatus: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    fontSize: "0.9rem",
    color: "#666",
  },
  statusDot: {
    width: "10px",
    height: "10px",
    borderRadius: "50%",
  },
  escalationsLayout: {
    display: "grid",
    gridTemplateColumns: "400px 1fr",
    gap: "1.5rem",
    minHeight: "600px",
  },
  escalationsList: {
    display: "flex",
    flexDirection: "column",
    gap: "1.5rem",
    overflowY: "auto",
    maxHeight: "700px",
  },
  section: {},
  sectionHeader: {
    fontSize: "1.1rem",
    marginBottom: "1rem",
    color: "#333",
  },
  emptyText: {
    textAlign: "center",
    color: "#999",
    padding: "2rem",
    fontSize: "0.9rem",
  },
  escalationCard: {
    padding: "1rem",
    border: "2px solid #e0e0e0",
    borderRadius: "8px",
    marginBottom: "0.75rem",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  activeCard: {
    borderColor: "#48bb78",
    background: "#f0fff4",
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "0.5rem",
  },
  caseId: {
    fontWeight: "600",
    color: "#333",
    fontSize: "0.9rem",
  },
  priorityBadge: {
    padding: "0.25rem 0.75rem",
    borderRadius: "12px",
    fontSize: "0.7rem",
    fontWeight: "600",
    color: "white",
  },
  reason: {
    margin: "0.5rem 0",
    fontSize: "0.9rem",
    color: "#333",
  },
  userInfo: {
    margin: "0.5rem 0",
    fontSize: "0.85rem",
    color: "#666",
  },
  cardInfo: {
    margin: "0.5rem 0",
    fontSize: "0.85rem",
    color: "#f44336",
    fontWeight: "500",
  },
  timestamp: {
    fontSize: "0.75rem",
    color: "#999",
    marginBottom: "0.75rem",
  },
  claimBtn: {
    width: "100%",
    padding: "0.5rem",
    background: "#48bb78",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "500",
    fontSize: "0.9rem",
  },
  chatBtn: {
    width: "100%",
    padding: "0.5rem",
    background: "#4299e1",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "500",
    fontSize: "0.9rem",
  },
  chatPanel: {
    border: "1px solid #e0e0e0",
    borderRadius: "8px",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
  chatHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "1rem",
    background: "#48bb78",
    color: "white",
  },
  chatTitle: {
    margin: 0,
    fontSize: "1.1rem",
  },
  chatSubtitle: {
    margin: "0.25rem 0 0 0",
    fontSize: "0.85rem",
    opacity: 0.9,
  },
  blockCardBtn: {
    padding: "0.5rem 1rem",
    background: "#f44336",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "0.9rem",
  },
  resolveBtn: {
    padding: "0.5rem 1rem",
    background: "#2f855a",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "0.9rem",
  },
  contextPanel: {
    padding: "1rem",
    borderBottom: "1px solid #e0e0e0",
    background: "#fff9e6",
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
  contextTitle: {
    margin: 0,
    marginBottom: "0.5rem",
    fontWeight: "600",
    fontSize: "1.1rem",
    color: "#856404",
  },
  sectionBox: {
    background: "white",
    padding: "1rem",
    borderRadius: "8px",
    border: "1px solid #e0e0e0",
  },
  sectionBoxTitle: {
    margin: "0 0 0.75rem 0",
    fontSize: "0.95rem",
    fontWeight: "600",
    color: "#333",
  },
  contextGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "0.75rem",
    fontSize: "0.9rem",
    color: "#333",
  },
  verificationGrid: {
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem",
  },
  verificationItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0.5rem",
    background: "#f8f9fa",
    borderRadius: "6px",
    fontSize: "0.85rem",
  },
  verificationLabel: {
    fontWeight: "600",
    color: "#666",
  },
  verificationValue: {
    color: "#333",
    fontWeight: "500",
    textAlign: "right",
    maxWidth: "60%",
    wordBreak: "break-word",
  },
  warningBox: {
    marginTop: "0.75rem",
    padding: "0.75rem",
    background: "#f8d7da",
    color: "#721c24",
    border: "1px solid #f5c6cb",
    borderRadius: "6px",
    fontSize: "0.9rem",
    fontWeight: "500",
  },
  messagesContainer: {
    flex: 1,
    padding: "1rem",
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem",
    overflowY: "auto",
    background: "#f5f7fa",
    minHeight: "300px",
    maxHeight: "400px",
  },
  emptyChat: {
    textAlign: "center",
    color: "#999",
    fontSize: "0.9rem",
    marginTop: "2rem",
  },
  messageRow: {
    display: "flex",
    width: "100%",
  },
  messageBubble: {
    padding: "0.5rem 0.75rem",
    borderRadius: "12px",
    maxWidth: "70%",
    wordBreak: "break-word",
  },
  agentMessage: {
    background: "#48bb78",
    color: "white",
    borderTopRightRadius: "0",
  },
  userMessage: {
    background: "#e0e0e0",
    color: "#333",
    borderTopLeftRadius: "0",
  },
  messageTime: {
    fontSize: "0.65rem",
    color: "rgba(0, 0, 0, 0.5)",
    textAlign: "right",
    marginTop: "0.25rem",
  },
  chatInput: {
    display: "flex",
    gap: "0.5rem",
    padding: "1rem",
    borderTop: "1px solid #e0e0e0",
    background: "white",
  },
  textarea: {
    flex: 1,
    padding: "0.5rem",
    borderRadius: "8px",
    border: "1px solid #ccc",
    resize: "none",
    fontFamily: "'Inter', sans-serif",
    fontSize: "0.9rem",
  },
  sendBtn: {
    padding: "0.5rem 1rem",
    background: "#48bb78",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "600",
  },
  sendBtnDisabled: {
    background: "#a0a0a0",
    cursor: "not-allowed",
  },
  noChatSelected: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flex: 1,
    color: "#999",
    fontSize: "1rem",
    minHeight: "400px",
  },
  guidelinesSection: {
    marginTop: "2rem",
    padding: "1.5rem",
    background: "#f8f9fa",
    borderRadius: "12px",
    border: "1px solid #e9ecef",
  },
  guidelinesTitle: {
    margin: "0 0 1.5rem 0",
    fontSize: "1.3rem",
    fontWeight: "600",
    color: "#2d3748",
    textAlign: "center",
  },
  guidelinesGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "1rem",
    marginBottom: "1.5rem",
  },
  guidelineCard: {
    padding: "1.25rem",
    background: "white",
    borderRadius: "10px",
    border: "2px solid #e9ecef",
    transition: "all 0.2s",
    textAlign: "center",
  },
  guidelineIcon: {
    fontSize: "2.5rem",
    marginBottom: "0.75rem",
  },
  guidelineCardTitle: {
    margin: "0 0 0.5rem 0",
    fontSize: "1rem",
    fontWeight: "600",
    color: "#2d3748",
  },
  guidelineText: {
    margin: 0,
    fontSize: "0.875rem",
    color: "#6c757d",
    lineHeight: "1.5",
  },
  quickTips: {
    padding: "1rem",
    background: "white",
    borderRadius: "8px",
    border: "2px solid #48bb78",
    fontSize: "0.9rem",
    color: "#2d3748",
    lineHeight: "1.6",
    textAlign: "center",
  },
};

export default SupportDashboard;