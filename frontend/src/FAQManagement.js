
import React, { useState, useEffect } from "react";
import API_BASE_URL from "./config";

function FAQManagement({ token }) {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    question: "",
    answer: ""
  });

  useEffect(() => {
    fetchFAQs();
  }, []);

  const fetchFAQs = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/faq`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        console.log("✅ FAQ data received:", data);
        setFaqs(Array.isArray(data) ? data : []);
      } else {
        const errorText = await response.text();
        console.error("❌ FAQ fetch error:", response.status, errorText);
        setError(`Failed to fetch FAQs (${response.status})`);
      }
    } catch (err) {
      console.error("❌ Connection error:", err);
      setError("Connection error - check if backend is running on " + API_BASE_URL);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.question.trim() || !formData.answer.trim()) {
      alert("Please fill in both question and answer");
      return;
    }

    try {
      const url = `${API_BASE_URL}/faq`;
      const method = "POST";
      const body = JSON.stringify({
        question: formData.question,
        answer: formData.answer,
        category: "general",
        tags: [],
        source: "manual"
      });

      console.log(`Sending ${method} to ${url}:`, JSON.parse(body));

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body
      });

      if (response.ok) {
        await fetchFAQs();
        setShowAddModal(false);
        setFormData({ question: "", answer: "" });
        alert("✅ FAQ created!");
      } else {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        console.error("Save error:", errorData);
        alert(errorData.detail || "Failed to save FAQ");
      }
    } catch (err) {
      console.error("❌ Save error:", err);
      alert("Connection error");
    }
  };

  const handleDelete = async (faq) => {
    if (!window.confirm(`Delete this FAQ?\n\n"${faq.question}"`)) return;

    try {
      const response = await fetch(`${API_BASE_URL}/faq?faq_id=${encodeURIComponent(faq.faq_id)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        await fetchFAQs();
        alert("✅ FAQ deleted!");
      } else {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        alert(errorData.detail || "Failed to delete FAQ");
      }
    } catch (err) {
      console.error("❌ Delete error:", err);
      alert("Connection error");
    }
  };

  const closeModal = () => {
    setShowAddModal(false);
    setFormData({ question: "", answer: "" });
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.spinner}></div>
        <p>Loading FAQs...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>FAQ Management</h2>
          <p style={styles.subtitle}>Manage frequently asked questions</p>
        </div>
        <button onClick={() => setShowAddModal(true)} style={styles.addButton}>
          ➕ Add New FAQ
        </button>
      </div>

      {error && (
        <div style={styles.errorBanner}>
          <span>⚠️ {error}</span>
          <button onClick={fetchFAQs} style={styles.retryButton}>
            🔄 Retry
          </button>
        </div>
      )}

      <div style={styles.faqGrid}>
        {faqs.map((faq) => (
          <div key={faq.faq_id || faq._id} style={styles.faqCard}>
            <div style={styles.faqHeader}>
              <h3 style={styles.faqQuestion}>Q: {faq.question}</h3>
              <button
                onClick={() => handleDelete(faq)}
                style={styles.deleteButton}
                title="Delete"
              >
                🗑️
              </button>
            </div>
            <div style={styles.faqAnswer}>
              <strong>A:</strong> {faq.answer}
            </div>
            {(faq.category || faq.usage_count > 0) && (
              <div style={styles.faqMeta}>
                {faq.category && (
                  <span style={styles.categoryBadge}>{faq.category}</span>
                )}
                {faq.usage_count > 0 && (
                  <span style={styles.usageBadge}>Used {faq.usage_count}x</span>
                )}
              </div>
            )}
          </div>
        ))}

        {faqs.length === 0 && !error && (
          <div style={styles.emptyState}>
            <div style={styles.emptyIcon}>❓</div>
            <p style={styles.emptyText}>No FAQs yet</p>
            <p style={styles.emptySubtext}>Click "Add New FAQ" to create your first FAQ</p>
          </div>
        )}
      </div>

      {showAddModal && (
        <div style={styles.modalOverlay} onClick={closeModal}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3 style={styles.modalTitle}>Add New FAQ</h3>
              <button onClick={closeModal} style={styles.closeButton}>✕</button>
            </div>

            <div style={styles.form}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Question *</label>
                <textarea
                  value={formData.question}
                  onChange={(e) =>
                    setFormData({ ...formData, question: e.target.value })
                  }
                  style={styles.textarea}
                  placeholder="Enter the question..."
                  rows={3}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Answer *</label>
                <textarea
                  value={formData.answer}
                  onChange={(e) =>
                    setFormData({ ...formData, answer: e.target.value })
                  }
                  style={styles.textarea}
                  placeholder="Enter the answer..."
                  rows={5}
                />
              </div>

              <div style={styles.modalFooter}>
                <button onClick={closeModal} style={styles.cancelButton}>
                  Cancel
                </button>
                <button onClick={handleSubmit} style={styles.submitButton}>
                  Add FAQ
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// --- Styles (same as before) ---
const styles = {
  container: { padding: "1rem" },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "2rem",
    flexWrap: "wrap",
    gap: "1rem"
  },
  title: {
    margin: 0,
    fontSize: "1.75rem",
    fontWeight: "600",
    color: "#2d3748"
  },
  subtitle: {
    margin: "0.5rem 0 0 0",
    color: "#6c757d",
    fontSize: "0.95rem"
  },
  addButton: {
    padding: "0.75rem 1.5rem",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "500",
    boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)"
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
  errorBanner: {
    padding: "1rem",
    background: "#fee",
    color: "#c00",
    borderRadius: "8px",
    marginBottom: "1.5rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "1rem"
  },
  retryButton: {
    padding: "0.5rem 1rem",
    background: "#c00",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "0.9rem"
  },
  faqGrid: { display: "grid", gap: "1.5rem" },
  faqCard: {
    background: "#f8f9fa",
    border: "1px solid #e9ecef",
    borderRadius: "12px",
    padding: "1.5rem"
  },
  faqHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "1rem",
    gap: "1rem"
  },
  faqQuestion: {
    margin: 0,
    fontSize: "1.1rem",
    fontWeight: "600",
    color: "#2d3748",
    flex: 1
  },
  deleteButton: {
    padding: "0.5rem 0.75rem",
    background: "#fc8181",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "1rem"
  },
  faqAnswer: {
    color: "#495057",
    fontSize: "1rem",
    lineHeight: "1.6",
    marginBottom: "1rem"
  },
  faqMeta: { display: "flex", gap: "0.5rem", flexWrap: "wrap" },
  categoryBadge: {
    padding: "0.25rem 0.75rem",
    background: "#e9ecef",
    color: "#495057",
    borderRadius: "12px",
    fontSize: "0.85rem",
    fontWeight: "500"
  },
  usageBadge: {
    padding: "0.25rem 0.75rem",
    background: "#d1ecf1",
    color: "#0c5460",
    borderRadius: "12px",
    fontSize: "0.85rem"
  },
  emptyState: {
    textAlign: "center",
    padding: "4rem 2rem",
    color: "#6c757d"
  },
  emptyIcon: { fontSize: "4rem", marginBottom: "1rem" },
  emptyText: {
    margin: 0,
    fontSize: "1.25rem",
    fontWeight: "600",
    marginBottom: "0.5rem"
  },
  emptySubtext: { margin: 0, fontSize: "0.95rem" },
  modalOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000
  },
  modal: {
    background: "white",
    borderRadius: "12px",
    width: "90%",
    maxWidth: "600px",
    maxHeight: "90vh",
    overflow: "auto",
    boxShadow: "0 20px 60px rgba(0, 0, 0, 0.3)"
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "1.5rem",
    borderBottom: "1px solid #e9ecef"
  },
  modalTitle: {
    margin: 0,
    fontSize: "1.5rem",
    fontWeight: "600",
    color: "#2d3748"
  },
  closeButton: {
    background: "transparent",
    border: "none",
    fontSize: "1.5rem",
    cursor: "pointer",
    color: "#6c757d",
    padding: "0.25rem 0.5rem"
  },
  form: { padding: "1.5rem" },
  formGroup: { marginBottom: "1.5rem" },
  label: {
    display: "block",
    marginBottom: "0.5rem",
    fontWeight: "500",
    color: "#2d3748",
    fontSize: "0.95rem"
  },
  textarea: {
    width: "100%",
    padding: "0.75rem",
    border: "2px solid #e2e8f0",
    borderRadius: "8px",
    fontSize: "1rem",
    fontFamily: "inherit",
    resize: "vertical",
    boxSizing: "border-box"
  },
  modalFooter: {
    display: "flex",
    justifyContent: "flex-end",
    gap: "1rem",
    paddingTop: "1rem",
    borderTop: "1px solid #e9ecef"
  },
  cancelButton: {
    padding: "0.75rem 1.5rem",
    background: "#e9ecef",
    color: "#495057",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "500"
  },
  submitButton: {
    padding: "0.75rem 1.5rem",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: "500",
    boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)"
  }
};

// Animation
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  textarea:focus {
    outline: none;
    border-color: #667eea;
  }
  button:hover:not(:disabled) {
    transform: translateY(-2px);
  }
`;
if (!document.querySelector('style[data-faq-animations]')) {
  styleSheet.setAttribute('data-faq-animations', 'true');
  document.head.appendChild(styleSheet);
}

export default FAQManagement;
