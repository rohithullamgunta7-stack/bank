// FeedbackModal.js
import React, { useState } from "react";

function FeedbackModal({ show, onClose, onSubmit, sessionId }) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState("");
  const [issueResolved, setIssueResolved] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) {
      alert("Please select a rating");
      return;
    }

    setSubmitting(true);
    await onSubmit({
      rating,
      comment: comment.trim() || null,
      issue_resolved: issueResolved,
      conversation_id: sessionId,
      feedback_type: "bot_chat"
    });
    setSubmitting(false);
  };

  if (!show) return null;

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <div style={styles.header}>
          <h3 style={styles.title}>How was your experience?</h3>
          <button onClick={onClose} style={styles.closeButton}>×</button>
        </div>

        <div style={styles.content}>
          <div style={styles.ratingSection}>
            <p style={styles.label}>Rate your experience</p>
            <div style={styles.stars}>
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  style={styles.starButton}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                  onClick={() => setRating(star)}
                >
                  <span style={{
                    fontSize: "2.5rem",
                    color: star <= (hoverRating || rating) ? "#ffc107" : "#e0e0e0",
                    transition: "all 0.2s"
                  }}>
                    ★
                  </span>
                </button>
              ))}
            </div>
            {rating > 0 && (
              <p style={styles.ratingText}>
                {rating === 5 ? "Excellent!" :
                 rating === 4 ? "Good!" :
                 rating === 3 ? "Average" :
                 rating === 2 ? "Below Average" :
                 "Poor"}
              </p>
            )}
          </div>

          <div style={styles.resolvedSection}>
            <label style={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={issueResolved}
                onChange={(e) => setIssueResolved(e.target.checked)}
                style={styles.checkbox}
              />
              <span>My issue was resolved</span>
            </label>
          </div>

          <div style={styles.commentSection}>
            <label style={styles.label}>
              Additional comments (optional)
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Tell us more about your experience..."
              maxLength={500}
              style={styles.textarea}
              rows={4}
            />
            <div style={styles.charCount}>
              {comment.length}/500
            </div>
          </div>

          <div style={styles.actions}>
            <button
              onClick={onClose}
              style={styles.skipButton}
              disabled={submitting}
            >
              Skip
            </button>
            <button
              onClick={handleSubmit}
              style={styles.submitButton}
              disabled={submitting || rating === 0}
            >
              {submitting ? "Submitting..." : "Submit Feedback"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    animation: "fadeIn 0.2s ease"
  },
  modal: {
    backgroundColor: "white",
    borderRadius: "16px",
    maxWidth: "500px",
    width: "90%",
    maxHeight: "90vh",
    overflow: "auto",
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
    animation: "slideUp 0.3s ease"
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "1.5rem",
    borderBottom: "1px solid #e0e0e0"
  },
  title: {
    margin: 0,
    fontSize: "1.25rem",
    fontWeight: "600",
    color: "#333"
  },
  closeButton: {
    background: "none",
    border: "none",
    fontSize: "2rem",
    color: "#999",
    cursor: "pointer",
    padding: 0,
    width: "32px",
    height: "32px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: "50%",
    transition: "all 0.2s"
  },
  content: {
    padding: "2rem"
  },
  ratingSection: {
    textAlign: "center",
    marginBottom: "2rem"
  },
  label: {
    display: "block",
    marginBottom: "0.75rem",
    fontSize: "0.95rem",
    fontWeight: "500",
    color: "#555"
  },
  stars: {
    display: "flex",
    justifyContent: "center",
    gap: "0.5rem",
    margin: "1rem 0"
  },
  starButton: {
    background: "none",
    border: "none",
    cursor: "pointer",
    padding: 0,
    transition: "transform 0.2s"
  },
  ratingText: {
    fontSize: "1.1rem",
    fontWeight: "600",
    color: "#667eea",
    margin: "0.5rem 0 0 0"
  },
  resolvedSection: {
    marginBottom: "1.5rem"
  },
  checkboxLabel: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    fontSize: "0.95rem",
    cursor: "pointer",
    padding: "1rem",
    background: "#f8f9fa",
    borderRadius: "8px",
    transition: "all 0.2s"
  },
  checkbox: {
    width: "20px",
    height: "20px",
    cursor: "pointer"
  },
  commentSection: {
    marginBottom: "1.5rem"
  },
  textarea: {
    width: "100%",
    padding: "0.75rem",
    border: "2px solid #e0e0e0",
    borderRadius: "8px",
    fontSize: "0.95rem",
    fontFamily: "inherit",
    resize: "vertical",
    outline: "none",
    transition: "border-color 0.2s"
  },
  charCount: {
    textAlign: "right",
    fontSize: "0.8rem",
    color: "#999",
    marginTop: "0.5rem"
  },
  actions: {
    display: "flex",
    gap: "1rem",
    justifyContent: "flex-end"
  },
  skipButton: {
    padding: "0.75rem 1.5rem",
    background: "white",
    border: "2px solid #e0e0e0",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "0.95rem",
    fontWeight: "500",
    color: "#666",
    transition: "all 0.2s"
  },
  submitButton: {
    padding: "0.75rem 2rem",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "0.95rem",
    fontWeight: "600",
    color: "white",
    transition: "all 0.2s"
  }
};

// Add CSS animations
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  button:hover:not(:disabled) {
    transform: translateY(-1px);
  }
  
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  textarea:focus {
    border-color: #667eea !important;
  }
  
  .checkboxLabel:hover {
    background: #e9ecef !important;
  }
`;
if (!document.querySelector('style[data-feedback-animations]')) {
  styleSheet.setAttribute('data-feedback-animations', 'true');
  document.head.appendChild(styleSheet);
}

export default FeedbackModal;