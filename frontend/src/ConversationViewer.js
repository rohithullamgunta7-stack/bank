// import React, { useState, useEffect } from "react";

// function ConversationViewer({ token, role }) {
//   const [conversations, setConversations] = useState([]);
//   const [selectedConversation, setSelectedConversation] = useState(null);
//   const [conversationHistory, setConversationHistory] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [historyLoading, setHistoryLoading] = useState(false);
//   const [error, setError] = useState("");
//   const [searchTerm, setSearchTerm] = useState("");
//   const [sortBy, setSortBy] = useState("recent");

//   useEffect(() => {
//     fetchConversationSummaries();
//   }, [token, role]);

//   const fetchConversationSummaries = async () => {
//     try {
//       setLoading(true);
//       const endpoint = role === "admin" 
//         ? "http://127.0.0.1:8000/admin/conversation-summaries"
//         : "http://127.0.0.1:8000/support/conversation-summaries";

//       const response = await fetch(endpoint, {
//         headers: {
//           Authorization: `Bearer ${token}`,
//         },
//       });

//       if (response.ok) {
//         const data = await response.json();
//         setConversations(data.summaries || []);
//       } else {
//         setError("Failed to fetch conversations");
//       }
//     } catch (err) {
//       setError("Connection error");
//     } finally {
//       setLoading(false);
//     }
//   };

//   const fetchConversationHistory = async (userId) => {
//     try {
//       setHistoryLoading(true);
//       const response = await fetch(`http://127.0.0.1:8000/conversation/${userId}`, {
//         headers: {
//           Authorization: `Bearer ${token}`,
//         },
//       });

//       if (response.ok) {
//         const data = await response.json();
//         setConversationHistory(data.conversation || []);
//       } else {
//         setError("Failed to fetch conversation history");
//       }
//     } catch (err) {
//       setError("Connection error while fetching history");
//     } finally {
//       setHistoryLoading(false);
//     }
//   };

//   const handleConversationSelect = (conversation) => {
//     setSelectedConversation(conversation);
//     fetchConversationHistory(conversation.user_id);
//   };

//   const formatTimestamp = (timestamp) => {
//     return new Date(timestamp).toLocaleString();
//   };

//   const filteredConversations = conversations.filter(conv =>
//     conv.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
//     conv.user_email.toLowerCase().includes(searchTerm.toLowerCase())
//   );

//   const sortedConversations = [...filteredConversations].sort((a, b) => {
//     switch (sortBy) {
//       case "recent":
//         return new Date(b.last_timestamp) - new Date(a.last_timestamp);
//       case "oldest":
//         return new Date(a.last_timestamp) - new Date(b.last_timestamp);
//       case "messages":
//         return b.message_count - a.message_count;
//       case "name":
//         return a.user_name.localeCompare(b.user_name);
//       default:
//         return 0;
//     }
//   });

//   if (loading) {
//     return <div className="loading-spinner">Loading conversations...</div>;
//   }

//   return (
//     <div className="conversation-viewer">
//       <div className="conversation-controls">
//         <div className="search-and-sort">
//           <input
//             type="text"
//             placeholder="Search by name or email..."
//             value={searchTerm}
//             onChange={(e) => setSearchTerm(e.target.value)}
//             className="search-input"
//           />
//           <select
//             value={sortBy}
//             onChange={(e) => setSortBy(e.target.value)}
//             className="sort-select"
//           >
//             <option value="recent">Most Recent</option>
//             <option value="oldest">Oldest First</option>
//             <option value="messages">Most Messages</option>
//             <option value="name">Name A-Z</option>
//           </select>
//         </div>
//         <button 
//           onClick={fetchConversationSummaries}
//           className="refresh-btn"
//         >
//           Refresh
//         </button>
//       </div>

//       {error && (
//         <div className="error-message">
//           {error}
//           <button onClick={() => setError("")} className="close-error">Ã—</button>
//         </div>
//       )}

//       <div className="conversation-layout">
//         <div className="conversation-list">
//           <h3>Conversations ({sortedConversations.length})</h3>
//           <div className="conversations-container">
//             {sortedConversations.map((conversation) => (
//               <div
//                 key={conversation.user_id}
//                 className={`conversation-summary ${
//                   selectedConversation?.user_id === conversation.user_id ? "selected" : ""
//                 }`}
//                 onClick={() => handleConversationSelect(conversation)}
//               >
//                 <div className="conversation-header">
//                   <div className="user-info">
//                     <span className="user-name">{conversation.user_name}</span>
//                     <span className="user-email">({conversation.user_email})</span>
//                   </div>
//                   <div className="conversation-meta">
//                     <span className="message-count">
//                       {conversation.message_count} messages
//                     </span>
//                     <span className="timestamp">
//                       {formatTimestamp(conversation.last_timestamp)}
//                     </span>
//                   </div>
//                 </div>
//                 <div className="last-message">
//                   <strong>Last:</strong> {conversation.last_message.substring(0, 100)}
//                   {conversation.last_message.length > 100 && "..."}
//                 </div>
//               </div>
//             ))}

//             {sortedConversations.length === 0 && !loading && (
//               <div className="no-conversations">
//                 <p>No conversations found</p>
//                 {searchTerm && (
//                   <button 
//                     onClick={() => setSearchTerm("")}
//                     className="clear-search"
//                   >
//                     Clear search
//                   </button>
//                 )}
//               </div>
//             )}
//           </div>
//         </div>

//         <div className="conversation-detail">
//           {selectedConversation ? (
//             <div>
//               <div className="conversation-detail-header">
//                 <h3>
//                   Conversation with {selectedConversation.user_name}
//                 </h3>
//                 <p className="user-email">{selectedConversation.user_email}</p>
//                 <p className="conversation-stats">
//                   {selectedConversation.message_count} messages â€¢ 
//                   Last active: {formatTimestamp(selectedConversation.last_timestamp)}
//                 </p>
//               </div>

//               <div className="conversation-history">
//                 {historyLoading ? (
//                   <div className="loading-spinner">Loading conversation...</div>
//                 ) : (
//                   <div className="messages-container">
//                     {conversationHistory.map((message, index) => (
//                       <div
//                         key={index}
//                         className={`message ${message.role === "user" ? "user-message" : "bot-message"}`}
//                       >
//                         <div className="message-header">
//                           <span className="sender">
//                             {message.role === "user" ? selectedConversation.user_name : "Assistant"}
//                           </span>
//                           {message.timestamp && (
//                             <span className="message-timestamp">
//                               {formatTimestamp(message.timestamp)}
//                             </span>
//                           )}
//                         </div>
//                         <div className="message-content">
//                           {message.content}
//                         </div>
//                       </div>
//                     ))}

//                     {conversationHistory.length === 0 && !historyLoading && (
//                       <div className="no-messages">
//                         <p>No messages in this conversation</p>
//                       </div>
//                     )}
//                   </div>
//                 )}
//               </div>
//             </div>
//           ) : (
//             <div className="no-selection">
//               <div className="no-selection-content">
//                 <h3>Select a conversation</h3>
//                 <p>Choose a conversation from the list to view its details</p>
//               </div>
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default ConversationViewer;


import React, { useState, useEffect } from "react";
import API_BASE_URL from './config'; // ADDED IMPORT

function ConversationViewer({ token, role }) {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("recent");

  useEffect(() => {
    fetchConversationSummaries();
  }, [token, role]);

  const fetchConversationSummaries = async () => {
    try {
      setLoading(true);
      // REPLACED URLS and fixed template literal syntax (Line 33-34)
      const endpoint = role === "admin" 
        ? `${API_BASE_URL}/admin/conversation-summaries`
        : `${API_BASE_URL}/support/conversation-summaries`;

      const response = await fetch(endpoint, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data.summaries || []);
      } else {
        setError("Failed to fetch conversations");
      }
    } catch (err) {
      setError("Connection error");
    } finally {
      setLoading(false);
    }
  };

  const fetchConversationHistory = async (userId) => {
    try {
      setHistoryLoading(true);
      // REPLACED URL
      const response = await fetch(`${API_BASE_URL}/conversation/${userId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setConversationHistory(data.conversation || []);
      } else {
        setError("Failed to fetch conversation history");
      }
    } catch (err) {
      setError("Connection error while fetching history");
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
    fetchConversationHistory(conversation.user_id);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const filteredConversations = conversations.filter(conv =>
    conv.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.user_email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedConversations = [...filteredConversations].sort((a, b) => {
    switch (sortBy) {
      case "recent":
        return new Date(b.last_timestamp) - new Date(a.last_timestamp);
      case "oldest":
        return new Date(a.last_timestamp) - new Date(b.last_timestamp);
      case "messages":
        return b.message_count - a.message_count;
      case "name":
        return a.user_name.localeCompare(b.user_name);
      default:
        return 0;
    }
  });

  if (loading) {
    return <div className="loading-spinner">Loading conversations...</div>;
  }

  return (
    <div className="conversation-viewer">
      <div className="conversation-controls">
        <div className="search-and-sort">
          <input
            type="text"
            placeholder="Search by name or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="recent">Most Recent</option>
            <option value="oldest">Oldest First</option>
            <option value="messages">Most Messages</option>
            <option value="name">Name A-Z</option>
          </select>
        </div>
        <button 
          onClick={fetchConversationSummaries}
          className="refresh-btn"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError("")} className="close-error">Ã—</button>
        </div>
      )}

      <div className="conversation-layout">
        <div className="conversation-list">
          <h3>Conversations ({sortedConversations.length})</h3>
          <div className="conversations-container">
            {sortedConversations.map((conversation) => (
              <div
                key={conversation.user_id}
                className={`conversation-summary ${
                  selectedConversation?.user_id === conversation.user_id ? "selected" : ""
                }`}
                onClick={() => handleConversationSelect(conversation)}
              >
                <div className="conversation-header">
                  <div className="user-info">
                    <span className="user-name">{conversation.user_name}</span>
                    <span className="user-email">({conversation.user_email})</span>
                  </div>
                  <div className="conversation-meta">
                    <span className="message-count">
                      {conversation.message_count} messages
                    </span>
                    <span className="timestamp">
                      {formatTimestamp(conversation.last_timestamp)}
                    </span>
                  </div>
                </div>
                <div className="last-message">
                  <strong>Last:</strong> {conversation.last_message.substring(0, 100)}
                  {conversation.last_message.length > 100 && "..."}
                </div>
              </div>
            ))}

            {sortedConversations.length === 0 && !loading && (
              <div className="no-conversations">
                <p>No conversations found</p>
                {searchTerm && (
                  <button 
                    onClick={() => setSearchTerm("")}
                    className="clear-search"
                  >
                    Clear search
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="conversation-detail">
          {selectedConversation ? (
            <div>
              <div className="conversation-detail-header">
                <h3>
                  Conversation with {selectedConversation.user_name}
                </h3>
                <p className="user-email">{selectedConversation.user_email}</p>
                <p className="conversation-stats">
                  {selectedConversation.message_count} messages â€¢ 
                  Last active: {formatTimestamp(selectedConversation.last_timestamp)}
                </p>
              </div>

              <div className="conversation-history">
                {historyLoading ? (
                  <div className="loading-spinner">Loading conversation...</div>
                ) : (
                  <div className="messages-container">
                    {conversationHistory.map((message, index) => (
                      <div
                        key={index}
                        className={`message ${message.role === "user" ? "user-message" : "bot-message"}`}
                      >
                        <div className="message-header">
                          <span className="sender">
                            {message.role === "user" ? selectedConversation.user_name : "Assistant"}
                          </span>
                          {message.timestamp && (
                            <span className="message-timestamp">
                              {formatTimestamp(message.timestamp)}
                            </span>
                          )}
                        </div>
                        <div className="message-content">
                          {message.content}
                        </div>
                      </div>
                    ))}

                    {conversationHistory.length === 0 && !historyLoading && (
                      <div className="no-messages">
                        <p>No messages in this conversation</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="no-selection">
              <div className="no-selection-content">
                <h3>Select a conversation</h3>
                <p>Choose a conversation from the list to view its details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ConversationViewer;