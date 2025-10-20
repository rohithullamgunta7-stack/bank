

import React, { useState, useEffect, useRef } from 'react';
import API_BASE_URL from './config'; // Assuming the import is here, as per instructions

function EscalationChat({ escalationId, userRole, userId, token }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [connected, setConnected] = useState(false);
  const [agentInfo, setAgentInfo] = useState(null);
  const [escalationDetails, setEscalationDetails] = useState(null);
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Fetch escalation details
    fetchEscalationDetails();
    
    // Connect to WebSocket
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [escalationId, userId, userRole]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchEscalationDetails = async () => {
    try {
      // Line 29: fetch(${API_BASE_URL}/escalation/escalations/my, {
      const response = await fetch(`${API_BASE_URL}/escalation/escalations/my`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        const escalation = data.escalations.find(e => e.escalation_id === escalationId);
        setEscalationDetails(escalation);
        
        if (escalation?.assigned_agent_id) {
          fetchAgentInfo(escalation.assigned_agent_id);
        }
      }
    } catch (error) {
      console.error('Error fetching escalation details:', error);
    }
  };

  const fetchAgentInfo = async (agentId) => {
    try {
      // Line 48: fetch(${API_BASE_URL}/auth/users, {
      const response = await fetch(`${API_BASE_URL}/auth/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const users = await response.json();
        const agent = users.find(u => u.user_id === agentId);
        setAgentInfo(agent);
      }
    } catch (error) {
      console.error('Error fetching agent info:', error);
    }
  };

  const connectWebSocket = () => {
    // Keep WebSocket URL as is (Line 64)
    const wsUrl = userRole === 'customer_support_agent' || userRole === 'admin'
      ? `ws://127.0.0.1:8000/escalation/ws/agent/${userId}`
      : `ws://127.0.0.1:8000/escalation/ws/user/${userId}`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'agent_message' || data.type === 'user_message') {
        setMessages(prev => [...prev, {
          sender: data.type === 'agent_message' ? 'agent' : 'user',
          message: data.message,
          timestamp: data.timestamp
        }]);
      } else if (data.type === 'agent_assigned') {
        setAgentInfo({ name: data.agent_name });
      } else if (data.type === 'escalation_resolved') {
        alert('Your issue has been resolved by our support team.');
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };
    
    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
      
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (wsRef.current?.readyState === WebSocket.CLOSED) {
          connectWebSocket();
        }
      }, 3000);
    };
    
    wsRef.current = ws;
  };

  const sendMessage = () => {
    if (!input.trim() || !connected) return;
    
    const messageData = {
      type: 'message',
      escalation_id: escalationId,
      message: input.trim()
    };
    
    wsRef.current.send(JSON.stringify(messageData));
    
    // Add to local messages immediately
    setMessages(prev => [...prev, {
      sender: userRole === 'customer_support_agent' || userRole === 'admin' ? 'agent' : 'user',
      message: input.trim(),
      timestamp: new Date().toISOString()
    }]);
    
    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const resolveEscalation = async () => {
    if (!window.confirm('Are you sure you want to mark this issue as resolved?')) {
      return;
    }
    
    const resolutionNotes = prompt('Please enter resolution notes:');
    if (!resolutionNotes) return;
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/escalation/escalations/${escalationId}/resolve`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            resolution_notes: resolutionNotes,
            action_taken: 'Issue resolved',
            customer_satisfied: true
          }),
        }
      );
      
      if (response.ok) {
        alert('Escalation marked as resolved');
        window.location.reload();
      }
    } catch (error) {
      alert('Failed to resolve escalation');
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <div>
            <h3 style={styles.headerTitle}>
              {userRole === 'customer_support_agent' || userRole === 'admin'
                ? `Support Chat - Case #${escalationId?.slice(0, 8)}`
                : 'Live Agent Support'}
            </h3>
            <p style={styles.headerSubtitle}>
              {connected ? (
                <>
                  <span style={styles.onlineIndicator}>●</span> Connected
                  {agentInfo && ` with ${agentInfo.name}`}
                </>
              ) : (
                <>
                  <span style={styles.offlineIndicator}>●</span> Connecting...
                </>
              )}
            </p>
          </div>
          
          {(userRole === 'customer_support_agent' || userRole === 'admin') && (
            <button onClick={resolveEscalation} style={styles.resolveBtn}>
              Mark Resolved
            </button>
          )}
        </div>
      </div>

      {/* Escalation Info */}
      {escalationDetails && (
        <div style={styles.infoBar}>
          <div style={styles.infoBadge}>
            Priority: <strong>{escalationDetails.priority?.toUpperCase()}</strong>
          </div>
          <div style={styles.infoBadge}>
            Reason: <strong>{escalationDetails.reason}</strong>
          </div>
          <div style={styles.infoBadge}>
            Status: <strong>{escalationDetails.status?.toUpperCase()}</strong>
          </div>
        </div>
      )}

      {/* Messages */}
      <div style={styles.messagesContainer}>
        {messages.length === 0 && (
          <div style={styles.emptyState}>
            <p style={styles.emptyText}>
              {userRole === 'customer_support_agent' || userRole === 'admin'
                ? 'Start chatting with the customer to resolve their issue'
                : agentInfo
                ? `${agentInfo.name} is here to help. Describe your issue in detail.`
                : 'Waiting for an agent to join...'}
            </p>
          </div>
        )}
        
        {messages.map((msg, idx) => {
          const isOwnMessage = 
            (userRole === 'customer_support_agent' || userRole === 'admin')
              ? msg.sender === 'agent'
              : msg.sender === 'user';
          
          return (
            <div
              key={idx}
              style={{
                ...styles.messageRow,
                justifyContent: isOwnMessage ? 'flex-end' : 'flex-start'
              }}
            >
              <div
                style={{
                  ...styles.messageBubble,
                  ...(isOwnMessage ? styles.ownMessage : styles.otherMessage)
                }}
              >
                <div style={styles.messageText}>{msg.message}</div>
                <div style={styles.messageTime}>
                  {new Date(msg.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={styles.inputArea}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder={connected ? 'Type your message...' : 'Connecting...'}
          disabled={!connected}
          rows={2}
          style={styles.input}
        />
        <button
          onClick={sendMessage}
          disabled={!connected || !input.trim()}
          style={{
            ...styles.sendBtn,
            ...((!connected || !input.trim()) && styles.sendBtnDisabled)
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '600px',
    border: '1px solid #e0e0e0',
    borderRadius: '12px',
    overflow: 'hidden',
    backgroundColor: '#fff'
  },
  header: {
    backgroundColor: '#667eea',
    color: 'white',
    padding: '1rem'
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  headerTitle: {
    margin: 0,
    fontSize: '1.1rem',
    fontWeight: '600'
  },
  headerSubtitle: {
    margin: '0.25rem 0 0 0',
    fontSize: '0.9rem',
    opacity: 0.9
  },
  onlineIndicator: {
    color: '#4caf50'
  },
  offlineIndicator: {
    color: '#ff9800'
  },
  resolveBtn: {
    padding: '0.5rem 1rem',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    color: 'white',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    fontWeight: '500'
  },
  infoBar: {
    display: 'flex',
    gap: '1rem',
    padding: '0.75rem 1rem',
    backgroundColor: '#f8f9fa',
    borderBottom: '1px solid #e0e0e0',
    flexWrap: 'wrap'
  },
  infoBadge: {
    fontSize: '0.85rem',
    color: '#666'
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '1rem',
    backgroundColor: '#fafafa'
  },
  emptyState: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    textAlign: 'center'
  },
  emptyText: {
    color: '#999',
    fontSize: '0.95rem'
  },
  messageRow: {
    display: 'flex',
    marginBottom: '1rem'
  },
  messageBubble: {
    maxWidth: '70%',
    padding: '0.75rem 1rem',
    borderRadius: '12px'
  },
  ownMessage: {
    backgroundColor: '#667eea',
    color: 'white',
    borderBottomRightRadius: '4px'
  },
  otherMessage: {
    backgroundColor: 'white',
    color: '#333',
    border: '1px solid #e0e0e0',
    borderBottomLeftRadius: '4px'
  },
  messageText: {
    marginBottom: '0.25rem',
    fontSize: '0.95rem',
    lineHeight: '1.4'
  },
  messageTime: {
    fontSize: '0.7rem',
    opacity: 0.7
  },
  inputArea: {
    display: 'flex',
    gap: '0.75rem',
    padding: '1rem',
    borderTop: '1px solid #e0e0e0',
    backgroundColor: '#fff'
  },
  input: {
    flex: 1,
    padding: '0.75rem',
    border: '1px solid #ddd',
    borderRadius: '8px',
    fontSize: '0.95rem',
    resize: 'none',
    fontFamily: 'inherit'
  },
  sendBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: '500'
  },
  sendBtnDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed'
  }
};

export default EscalationChat;