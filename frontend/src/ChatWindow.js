
import React, { useState, useEffect, useRef } from "react";
import API_BASE_URL from "./config";
import WS_BASE_URL from "./config";

function ChatWindow({ token, onLogout }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [escalationId, setEscalationId] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const [accountsList, setAccountsList] = useState([]);
  
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const pendingMessagesRef = useRef(new Set()); // Track pending messages

  useEffect(() => {
    console.log("🎬 Component mounted, fetching user info...");
    fetchUserInfo();
    checkForExistingEscalation();
    return () => {
      console.log("🔚 Component unmounting, cleaning up...");
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [token]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (userInfo?.user_id) {
      console.log("🔌 UserInfo available, connecting WebSocket for:", userInfo.user_id);
      connectWebSocket(userInfo.user_id);
    } else {
      console.log("⚠️ UserInfo not available yet");
    }
  }, [userInfo]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchUserInfo = async () => {
    try {
      console.log("📡 Fetching user info...");
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        console.log("✅ User info fetched:", data);
        setUserInfo(data);
      } else {
        console.error("❌ Failed to fetch user info:", response.status);
      }
    } catch (error) {
      console.error("Error fetching user info:", error);
    }
  };

  const checkForExistingEscalation = async () => {
    try {
      console.log("🔍 Checking for existing escalations...");
      const response = await fetch(`${API_BASE_URL}/escalation/escalations/my`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        console.log("📋 Escalations data:", data);
        const activeEscalation = data.escalations?.find(
          esc => esc.status !== 'resolved' && esc.status !== 'closed'
        );
        if (activeEscalation) {
          console.log("✅ Found active escalation:", activeEscalation.escalation_id);
          setEscalationId(activeEscalation.escalation_id);
          await loadEscalationHistory(activeEscalation.escalation_id);
          setMessages(prev => [...prev, {
            sender: "system",
            text: `Resuming your support session (Case #${activeEscalation.escalation_id.slice(0, 8)})`,
            timestamp: new Date().toISOString()
          }]);
        } else {
          console.log("ℹ️ No active escalation found");
        }
      }
    } catch (error) {
      console.error("❌ Error checking escalations:", error);
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
          id: `${msg.timestamp}-${msg.sender}` // Add unique ID
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error("Error loading escalation history:", error);
    }
  };

  const connectWebSocket = (userId) => {
    if (wsRef.current) {
      console.log("🔌 Closing existing WebSocket connection");
      wsRef.current.close();
      wsRef.current = null;
    }

    const wsUrl = `${WS_BASE_URL}/escalation/ws/user/${userId}`;
    console.log("🔌 Connecting WebSocket to:", wsUrl);
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log("✅ WebSocket connected for user:", userId);
      setWsConnected(true);
      
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
        console.log("📨 WebSocket message received:", data);
        
        if (data.type === "pong") {
          return;
        }
        
        if (data.type === "agent_message") {
          // Add agent message immediately
          const messageId = `${data.timestamp}-agent`;
          setMessages(prev => {
            // Check if message already exists
            if (prev.some(m => m.id === messageId)) {
              return prev;
            }
            return [...prev, {
              sender: "bot",
              text: data.message,
              timestamp: data.timestamp,
              isAgent: true,
              id: messageId
            }];
          });
        } else if (data.type === "escalation_assigned") {
          setMessages(prev => [...prev, {
            sender: "system",
            text: `${data.agent_name || 'A support agent'} has joined the chat and will assist you shortly.`,
            timestamp: new Date().toISOString(),
            id: `system-${Date.now()}`
          }]);
        } else if (data.type === "ack") {
          console.log("✓ Message acknowledged:", data.message);
          setLoading(false);
        } else if (data.type === "error") {
          console.error("WebSocket error:", data.message);
          setMessages(prev => [...prev, {
            sender: "system",
            text: `Error: ${data.message}`,
            timestamp: new Date().toISOString(),
            id: `error-${Date.now()}`
          }]);
          setLoading(false);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket disconnected");
      setWsConnected(false);
      
      reconnectTimeoutRef.current = setTimeout(() => {
        if (userInfo?.user_id) {
          console.log("🔄 Attempting to reconnect WebSocket...");
          connectWebSocket(userInfo.user_id);
        }
      }, 3000);
    };

    wsRef.current = ws;
  };

  const handleAccountSelection = async (accountIndex) => {
    const accountNumber = accountIndex + 1;
    setLoading(true);
    
    const messageId = `user-${Date.now()}`;
    setMessages(prev => [...prev, {
      sender: "user",
      text: `${accountNumber}`,
      timestamp: new Date().toISOString(),
      id: messageId
    }]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ message: `${accountNumber}` })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.escalated && data.escalation_id) {
          console.log("🚨 Escalation created:", data.escalation_id);
          setEscalationId(data.escalation_id);
          
          if (!wsConnected && userInfo?.user_id) {
            connectWebSocket(userInfo.user_id);
          }
        }
        
        const botMessageId = `bot-${Date.now()}`;
        setMessages(prev => [...prev, {
          sender: "bot",
          text: data.reply,
          timestamp: new Date().toISOString(),
          id: botMessageId
        }]);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, {
        sender: "system",
        text: "Error sending message. Please try again.",
        timestamp: new Date().toISOString(),
        id: `error-${Date.now()}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    const messageId = `user-${Date.now()}-${Math.random()}`;
    setInput("");
    setLoading(true);

    // Add user message to UI
    setMessages(prev => [...prev, {
      sender: "user",
      text: userMessage,
      timestamp: new Date().toISOString(),
      id: messageId
    }]);

    try {
      if (escalationId) {
        console.log("📤 Sending via WebSocket (escalated):", userMessage);
        
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: "message",
            escalation_id: escalationId,
            message: userMessage
          }));
          // Loading will be set to false when we receive 'ack'
        } else {
          console.error("❌ WebSocket not connected, attempting to reconnect...");
          setMessages(prev => [...prev, {
            sender: "system",
            text: "Connection lost. Reconnecting...",
            timestamp: new Date().toISOString(),
            id: `system-${Date.now()}`
          }]);
          
          if (userInfo?.user_id) {
            connectWebSocket(userInfo.user_id);
          }
          
          // Fallback to REST API
          const response = await fetch(`${API_BASE_URL}/escalation/${escalationId}/message?message=${encodeURIComponent(userMessage)}`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` }
          });

          if (!response.ok) {
            setMessages(prev => [...prev, {
              sender: "system",
              text: "Failed to send message. Please try again.",
              timestamp: new Date().toISOString(),
              id: `error-${Date.now()}`
            }]);
          }
          setLoading(false);
        }
        return;
      }

      // Normal bot chat (not escalated)
      console.log("📤 Sending to bot (normal chat):", userMessage);
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMessage })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.escalated && data.escalation_id) {
          console.log("🚨 Escalation created:", data.escalation_id);
          setEscalationId(data.escalation_id);
          
          if (!wsConnected && userInfo?.user_id) {
            connectWebSocket(userInfo.user_id);
          }
        }
        
        if (data.reply === "ACCOUNT_LIST" && data.accounts) {
          setAccountsList(data.accounts);
          const botMessageId = `bot-${Date.now()}`;
          setMessages(prev => [...prev, {
            sender: "bot",
            text: "Here are your accounts:",
            timestamp: new Date().toISOString(),
            accounts: data.accounts,
            id: botMessageId
          }]);
        } else {
          const botMessageId = `bot-${Date.now()}`;
          setMessages(prev => [...prev, {
            sender: "bot",
            text: data.reply,
            timestamp: new Date().toISOString(),
            id: botMessageId
          }]);
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages(prev => [...prev, {
        sender: "system",
        text: "Error sending message. Please try again.",
        timestamp: new Date().toISOString(),
        id: `error-${Date.now()}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleEscalate = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/escalation/escalate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEscalationId(data.escalation_id);
        
        if (!wsConnected && userInfo?.user_id) {
          connectWebSocket(userInfo.user_id);
        }
        
        setMessages(prev => [...prev, {
          sender: "system",
          text: `Your case has been escalated. Case ID: ${data.escalation_id.slice(0, 8)}. A support agent will assist you shortly.`,
          timestamp: new Date().toISOString(),
          id: `system-${Date.now()}`
        }]);
      }
    } catch (error) {
      console.error("Error escalating:", error);
    }
  };

  const AccountCard = ({ account, index }) => {
    const isLoan = account.account_type === "Home Loan";
    const isCreditCard = account.account_type === "Credit Card";

    return (
      <div onClick={() => handleAccountSelection(index)} style={styles.orderCard}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
          <div>
            <h4 style={{ fontWeight: 'bold', margin: 0 }}>
              {index + 1}. {account.account_type}
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#666', margin: '2px 0' }}>{account.account_number}</p>
          </div>
          <span style={{
            padding: '2px 8px', borderRadius: 6, fontSize: 12, height: 'fit-content',
            backgroundColor: account.status === 'Active' ? '#DFF2E1' : '#EEE',
            color: account.status === 'Active' ? '#4CAF50' : '#666'
          }}>
            {account.status}
          </span>
        </div>

        {isCreditCard ? (
          <div style={{ fontSize: '0.85rem', lineHeight: 1.6, marginTop: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Total Limit:</span>
              <span style={{ fontWeight: '500' }}>{account.currency} {account.total_limit?.toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Available:</span>
              <span style={{ color: '#4CAF50', fontWeight: '500' }}>{account.currency} {account.available_credit?.toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Outstanding:</span>
              <span style={{ color: '#F44336', fontWeight: '500' }}>{account.currency} {account.balance?.toLocaleString()}</span>
            </div>
          </div>
        ) : isLoan ? (
          <div style={{ fontSize: '0.85rem', lineHeight: 1.6, marginTop: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Principal:</span>
              <span style={{ fontWeight: '500' }}>{account.currency} {account.principal_amount?.toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Outstanding:</span>
              <span style={{ fontWeight: '500' }}>{account.currency} {account.balance?.toLocaleString()}</span>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'right', marginTop: 8 }}>
            <p style={{ fontSize: 12, color: '#666', margin: 0 }}>Balance</p>
            <p style={{ fontSize: 22, fontWeight: 'bold', color: '#667eea', margin: '4px 0 0 0' }}>
              {account.currency} {account.balance?.toLocaleString()}
            </p>
          </div>
        )}

        <div style={{ marginTop: 10, paddingTop: 8, borderTop: '1px solid #f0f0f0', fontSize: 11, color: '#999', display: 'flex', justifyContent: 'space-between' }}>
          <span>Opened: {account.created_at}</span>
          <span style={{ color: '#667eea', fontWeight: '500' }}>Click to view details →</span>
        </div>
      </div>
    );
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Banking Support</h1>
          <p style={styles.modeIndicator}>
            {escalationId ? (
              <span>
                🟢 Connected to Agent (Case #{escalationId.slice(0, 8)})
              </span>
            ) : (
              <span>
                Welcome, {userInfo?.name || 'Guest'}
              </span>
            )}
          </p>
        </div>
        <div style={styles.statusContainer}>
          {!escalationId && (
            <button onClick={handleEscalate} style={styles.sendButton}>
              Talk to Human Agent
            </button>
          )}
          {/* Logout button removed */}
        </div>
      </div>

      <div style={styles.chatBox}>
        {messages.map((msg, idx) => (
          <div key={msg.id || idx} style={{ marginBottom: 15, display: 'flex', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
            <div style={{
              ...styles.message,
              ...(msg.sender === 'user' ? styles.userMessage : msg.sender === 'system' ? styles.systemMessage : styles.botMessage)
            }}>
              {msg.isAgent && <span style={styles.agentBadge}>Human Agent</span>}
              {msg.accounts ? (
                <div>
                  <p style={{ margin: '0 0 12px 0', fontSize: 15, fontWeight: '500' }}>{msg.text}</p>
                  <div>
                    {msg.accounts.map((account, i) => <AccountCard key={i} account={account} index={i} />)}
                  </div>
                </div>
              ) : <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.text}</p>}
              <div style={styles.timestamp}>{new Date(msg.timestamp).toLocaleTimeString()}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{ ...styles.message, ...styles.loadingMessage }}>
              <div style={{ display: 'flex', gap: 5 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#667eea', animation: 'bounce 1.4s infinite ease-in-out' }}></div>
                <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#667eea', animation: 'bounce 1.4s infinite ease-in-out 0.2s' }}></div>
                <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#667eea', animation: 'bounce 1.4s infinite ease-in-out 0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputArea}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder={escalationId ? "Type your message to the agent..." : "Type your message..."}
          style={styles.input}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{ ...styles.sendButton, ...(loading || !input.trim() ? styles.sendButtonDisabled : {}) }}
        >
          Send
        </button>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }
      `}</style>
    </div>
  );
}

const styles = {
  container: { maxWidth: "1200px", margin: "0 auto", padding: "20px", fontFamily: "'Inter', sans-serif", height: "100vh", display: "flex", flexDirection: "column" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 15, paddingBottom: 15, borderBottom: "2px solid #e0e0e0" },
  title: { margin: 0, fontSize: "1.5rem", color: "#333", fontWeight: "600" },
  modeIndicator: { margin: "4px 0 0 0", fontSize: "0.85rem", color: "#4caf50", fontWeight: "500" },
  statusContainer: { display: "flex", gap: 10 },
  chatBox: { flex: 1, overflowY: "auto", padding: 15, border: "1px solid #ddd", borderRadius: 12, backgroundColor: "#fafafa" },
  message: { padding: "12px 16px", borderRadius: 12, maxWidth: "75%", lineHeight: 1.5, fontSize: 14 },
  userMessage: { backgroundColor: "#667eea", color: "white", marginLeft: "auto" },
  botMessage: { backgroundColor: "white", color: "#333", border: "1px solid #e0e0e0" },
  systemMessage: { backgroundColor: "#fff3cd", color: "#856404", border: "1px solid #ffc107", textAlign: "center", margin: "1rem auto", maxWidth: "85%", fontSize: 13 },
  agentBadge: { display: "inline-block", background: "#4caf50", color: "white", padding: "3px 8px", borderRadius: 12, fontSize: 11, fontWeight: 600, marginBottom: 8 },
  timestamp: { fontSize: 11, color: '#999', marginTop: 6, textAlign: 'right' },
  inputArea: { display: "flex", gap: 10, paddingTop: 15 },
  input: { flex: 1, padding: 12, border: "2px solid #ddd", borderRadius: 8, fontSize: 14, outline: "none" },
  sendButton: { padding: "12px 24px", backgroundColor: "#667eea", color: "white", border: "none", borderRadius: 8, cursor: "pointer", fontWeight: "500" },
  sendButtonDisabled: { backgroundColor: "#ccc", cursor: "not-allowed" },
  orderCard: { 
    backgroundColor: "white", 
    border: "2px solid #e0e0e0", 
    borderRadius: 12, 
    padding: 14, 
    cursor: "pointer", 
    marginBottom: 12,
    transition: "all 0.2s ease",
    boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
  },
  loadingMessage: { backgroundColor: "white", color: "#666", padding: 12, borderRadius: 12, border: "1px solid #e0e0e0" }
};

export default ChatWindow;