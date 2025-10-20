
import React, { useState, useEffect } from 'react';
import API_BASE_URL from './config'; // Assuming config is available via import

function EscalationButton({ token, onEscalationCreated }) {
  const [showModal, setShowModal] = useState(false);
  const [reason, setReason] = useState('');
  const [issueType, setIssueType] = useState('food_quality');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [myEscalations, setMyEscalations] = useState([]);
  const [showEscalations, setShowEscalations] = useState(false);

  useEffect(() => {
    fetchMyEscalations();
  }, [token]);

  const fetchMyEscalations = async () => {
    try {
      // REPLACED hardcoded URL
      const response = await fetch(`${API_BASE_URL}/escalation/escalations/my`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMyEscalations(data.escalations || []);
      }
    } catch (error) {
      console.error('Error fetching escalations:', error);
    }
  };

  const handleEscalate = async () => {
    if (!reason.trim()) {
      alert('Please describe your issue');
      return;
    }

    setIsSubmitting(true);

    try {
      // REPLACED hardcoded URL
      const response = await fetch(`${API_BASE_URL}/escalation/escalate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          reason: reason.trim(),
          issue_type: issueType
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // NOTE: Changed window.alert() to use the prompt-defined style for clarity, 
        // though the original prompt uses alert(). Keeping the original code's behavior for now.
        alert(data.message || 'Your issue has been escalated to a support agent');
        setShowModal(false);
        setReason('');
        fetchMyEscalations();
        
        if (onEscalationCreated) {
          onEscalationCreated(data.escalation_id);
        }
      } else {
        const errorData = await response.json();
        alert(errorData.detail || 'Failed to escalate issue');
      }
    } catch (error) {
      alert('Connection error. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#ff9800';
      case 'assigned': return '#2196f3';
      case 'resolved': return '#4caf50';
      case 'closed': return '#9e9e9e';
      default: return '#757575';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#2196f3';
      default: return '#9e9e9e';
    }
  };

  return (
    <>
      <div style={styles.container}>
        <button
          onClick={() => setShowModal(true)}
          style={styles.escalateBtn}
        >
          🎧 Talk to Human Agent
        </button>
        
        {myEscalations.length > 0 && (
          <button
            onClick={() => setShowEscalations(!showEscalations)}
            style={styles.viewBtn}
          >
            View My Cases ({myEscalations.length})
          </button>
        )}
      </div>

      {/* Escalations List */}
      {showEscalations && (
        <div style={styles.escalationsList}>
          <h4 style={styles.listTitle}>My Support Cases</h4>
          {myEscalations.map((esc) => (
            <div key={esc.escalation_id} style={styles.escalationCard}>
              <div style={styles.cardHeader}>
                <span style={styles.caseId}>
                  Case #{esc.escalation_id.slice(0, 8)}
                </span>
                <div style={styles.badges}>
                  <span
                    style={{
                      ...styles.badge,
                      backgroundColor: getPriorityColor(esc.priority)
                    }}
                  >
                    {esc.priority}
                  </span>
                  <span
                    style={{
                      ...styles.badge,
                      backgroundColor: getStatusColor(esc.status)
                    }}
                  >
                    {esc.status}
                  </span>
                </div>
              </div>
              <p style={styles.reason}>{esc.reason}</p>
              <p style={styles.timestamp}>
                Created: {new Date(esc.created_at).toLocaleString()}
              </p>
              {esc.status === 'assigned' && (
                <p style={styles.agentNote}>
                  An agent is working on your case
                </p>
              )}
              {esc.status === 'resolved' && esc.resolution && (
                <div style={styles.resolution}>
                  <strong>Resolution:</strong> {esc.resolution.resolution_notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Escalation Modal */}
      {showModal && (
        <div style={styles.modalOverlay} onClick={() => setShowModal(false)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div style={styles.modalHeader}>
              <h3 style={styles.modalTitle}>Request Human Support Agent</h3>
              <button
                onClick={() => setShowModal(false)}
                style={styles.closeBtn}
              >
                ×
              </button>
            </div>

            <div style={styles.modalBody}>
              <p style={styles.modalDescription}>
                Our AI assistant will connect you with a live support agent who can help resolve your issue immediately.
              </p>

              <div style={styles.formGroup}>
                <label style={styles.label}>Issue Type</label>
                <select
                  value={issueType}
                  onChange={(e) => setIssueType(e.target.value)}
                  style={styles.select}
                >
                  <option value="food_quality">Food Quality Issue</option>
                  <option value="delivery">Delivery Problem</option>
                  <option value="refund">Refund Request</option>
                  <option value="missing_items">Missing Items</option>
                  <option value="wrong_order">Wrong Order</option>
                  <option value="other">Other Issue</option>
                </select>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>
                  Describe Your Issue <span style={styles.required}>*</span>
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Please provide details about your issue..."
                  rows={5}
                  style={styles.textarea}
                  maxLength={500}
                />
                <div style={styles.charCount}>
                  {reason.length}/500 characters
                </div>
              </div>

              <div style={styles.infoBox}>
                <strong>What happens next?</strong>
                <ul style={styles.infoList}>
                  <li>We'll create a priority support ticket</li>
                  <li>A live agent will be assigned within 5-10 minutes</li>
                  <li>You can chat directly with the agent</li>
                  <li>The agent has access to your order history</li>
                </ul>
              </div>
            </div>

            <div style={styles.modalFooter}>
              <button
                onClick={() => setShowModal(false)}
                style={styles.cancelBtn}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                onClick={handleEscalate}
                style={styles.submitBtn}
                disabled={isSubmitting || !reason.trim()}
              >
                {isSubmitting ? 'Submitting...' : 'Request Agent'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

const styles = {
  container: {
    display: 'flex',
    gap: '0.5rem',
    padding: '0.5rem',
    flexWrap: 'wrap'
  },
  escalateBtn: {
    padding: '0.75rem 1.25rem',
    backgroundColor: '#ff6b6b',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    fontWeight: '500',
    transition: 'all 0.2s'
  },
  viewBtn: {
    padding: '0.75rem 1.25rem',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    fontWeight: '500'
  },
  escalationsList: {
    padding: '1rem',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    marginTop: '0.5rem'
  },
  listTitle: {
    margin: '0 0 1rem 0',
    fontSize: '1rem',
    fontWeight: '600',
    color: '#333'
  },
  escalationCard: {
    backgroundColor: 'white',
    padding: '1rem',
    borderRadius: '8px',
    marginBottom: '0.75rem',
    border: '1px solid #e0e0e0'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.5rem'
  },
  caseId: {
    fontWeight: '600',
    color: '#333',
    fontSize: '0.9rem'
  },
  badges: {
    display: 'flex',
    gap: '0.5rem'
  },
  badge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: '600',
    color: 'white',
    textTransform: 'uppercase'
  },
  reason: {
    margin: '0.5rem 0',
    color: '#666',
    fontSize: '0.9rem'
  },
  timestamp: {
    margin: '0.5rem 0',
    fontSize: '0.8rem',
    color: '#999'
  },
  agentNote: {
    margin: '0.5rem 0 0 0',
    padding: '0.5rem',
    backgroundColor: '#e3f2fd',
    borderRadius: '4px',
    fontSize: '0.85rem',
    color: '#1976d2'
  },
  resolution: {
    marginTop: '0.5rem',
    padding: '0.75rem',
    backgroundColor: '#f1f8e9',
    borderRadius: '4px',
    fontSize: '0.85rem',
    color: '#558b2f'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000
  },
  modal: {
    backgroundColor: 'white',
    borderRadius: '12px',
    maxWidth: '500px',
    width: '90%',
    maxHeight: '90vh',
    overflow: 'auto',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1.25rem',
    borderBottom: '1px solid #e0e0e0'
  },
  modalTitle: {
    margin: 0,
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#333'
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    fontSize: '2rem',
    cursor: 'pointer',
    color: '#999',
    lineHeight: 1
  },
  modalBody: {
    padding: '1.25rem'
  },
  modalDescription: {
    margin: '0 0 1.5rem 0',
    color: '#666',
    fontSize: '0.95rem'
  },
  formGroup: {
    marginBottom: '1.25rem'
  },
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    fontWeight: '500',
    color: '#333',
    fontSize: '0.9rem'
  },
  required: {
    color: '#f44336'
  },
  select: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '0.95rem',
    backgroundColor: 'white'
  },
  textarea: {
    width: '100%',
    padding: '0.75rem',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '0.95rem',
    fontFamily: 'inherit',
    resize: 'vertical'
  },
  charCount: {
    textAlign: 'right',
    fontSize: '0.8rem',
    color: '#999',
    marginTop: '0.25rem'
  },
  infoBox: {
    padding: '1rem',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    border: '1px solid #e0e0e0'
  },
  infoList: {
    margin: '0.5rem 0 0 0',
    paddingLeft: '1.25rem',
    fontSize: '0.85rem',
    color: '#666'
  },
  modalFooter: {
    display: 'flex',
    gap: '0.75rem',
    padding: '1.25rem',
    borderTop: '1px solid #e0e0e0',
    justifyContent: 'flex-end'
  },
  cancelBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#f5f5f5',
    color: '#666',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: '500'
  },
  submitBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#ff6b6b',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: '500'
  }
};

export default EscalationButton;
