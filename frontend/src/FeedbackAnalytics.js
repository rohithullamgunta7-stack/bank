
import React, { useState, useEffect } from "react";
import API_BASE_URL from './config';

function FeedbackAnalytics({ token }) {
  const [analytics, setAnalytics] = useState(null);
  const [agentPerformance, setAgentPerformance] = useState(null);
  const [recentFeedback, setRecentFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState(30);
  const [selectedSentiment, setSelectedSentiment] = useState("all");

  useEffect(() => {
    fetchAnalytics();
    fetchAgentPerformance();
    fetchRecentFeedback();
  }, [period, selectedSentiment]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      // Line 21: REPLACED URL
      const response = await fetch(
        `${API_BASE_URL}/feedback/analytics?days=${period}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error("Error fetching analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAgentPerformance = async () => {
    try {
      // Line 38: REPLACED URL
      const response = await fetch(
        `${API_BASE_URL}/feedback/agent-performance?days=${period}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setAgentPerformance(data);
      }
    } catch (error) {
      console.error("Error fetching agent performance:", error);
    }
  };

  const fetchRecentFeedback = async () => {
    try {
      const sentimentParam = selectedSentiment !== "all" ? `?sentiment=${selectedSentiment}` : "";
      // Line 53: REPLACED URL
      const response = await fetch(
        `${API_BASE_URL}/feedback/recent${sentimentParam}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setRecentFeedback(data.feedback || []);
      }
    } catch (error) {
      console.error("Error fetching recent feedback:", error);
    }
  };

  const renderStars = (rating) => {
    return (
      <span style={styles.starsDisplay}>
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            style={{
              color: star <= rating ? "#ffc107" : "#e0e0e0",
              fontSize: "1.2rem"
            }}
          >
            ★
          </span>
        ))}
      </span>
    );
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case "positive": return "#48bb78";
      case "negative": return "#f56565";
      default: return "#a0aec0";
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case "positive": return "😊";
      case "negative": return "😞";
      default: return "😐";
    }
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.spinner}></div>
        <p>Loading feedback analytics...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header with Period Selector */}
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>Feedback & Ratings Analytics</h2>
          <p style={styles.subtitle}>Customer satisfaction insights</p>
        </div>
        <div style={styles.periodSelector}>
          <button
            style={{
              ...styles.periodButton,
              ...(period === 7 ? styles.periodButtonActive : {})
            }}
            onClick={() => setPeriod(7)}
          >
            7 Days
          </button>
          <button
            style={{
              ...styles.periodButton,
              ...(period === 30 ? styles.periodButtonActive : {})
            }}
            onClick={() => setPeriod(30)}
          >
            30 Days
          </button>
          <button
            style={{
              ...styles.periodButton,
              ...(period === 90 ? styles.periodButtonActive : {})
            }}
            onClick={() => setPeriod(90)}
          >
            90 Days
          </button>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div style={styles.metricsGrid}>
        <div style={{ ...styles.metricCard, ...styles.metricCardBlue }}>
          <div style={styles.metricIcon}>⭐</div>
          <div>
            <div style={styles.metricLabel}>Average Rating</div>
            <div style={styles.metricValue}>
              {analytics?.average_rating?.toFixed(1) || "0.0"}
              <span style={styles.metricUnit}>/5.0</span>
            </div>
            {renderStars(Math.round(analytics?.average_rating || 0))}
          </div>
        </div>

        <div style={{ ...styles.metricCard, ...styles.metricCardGreen }}>
          <div style={styles.metricIcon}>💬</div>
          <div>
            <div style={styles.metricLabel}>Total Feedback</div>
            <div style={styles.metricValue}>{analytics?.total_feedback || 0}</div>
            <div style={styles.metricTrend}>
              {analytics?.trend?.direction === "up" ? "↑" : 
               analytics?.trend?.direction === "down" ? "↓" : "→"}
              {" "}{Math.abs(analytics?.trend?.percentage || 0)}% vs prev period
            </div>
          </div>
        </div>

        <div style={{ ...styles.metricCard, ...styles.metricCardPurple }}>
          <div style={styles.metricIcon}>📊</div>
          <div>
            <div style={styles.metricLabel}>Response Rate</div>
            <div style={styles.metricValue}>
              {analytics?.response_rate || 0}%
            </div>
            <div style={styles.metricSubtext}>
              Users providing feedback
            </div>
          </div>
        </div>

        <div style={{ ...styles.metricCard, ...styles.metricCardOrange }}>
          <div style={styles.metricIcon}>✅</div>
          <div>
            <div style={styles.metricLabel}>Resolution Rate</div>
            <div style={styles.metricValue}>
              {analytics?.resolution_rate || 0}%
            </div>
            <div style={styles.metricSubtext}>
              Issues marked as resolved
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div style={styles.chartsRow}>
        {/* Sentiment Distribution */}
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Sentiment Distribution</h3>
          <div style={styles.sentimentBars}>
            {Object.entries(analytics?.sentiment_distribution || {}).map(([sentiment, count]) => {
              const total = analytics?.total_feedback || 1;
              const percentage = ((count / total) * 100).toFixed(1);
              return (
                <div key={sentiment} style={styles.sentimentRow}>
                  <div style={styles.sentimentLabel}>
                    <span style={styles.sentimentIcon}>
                      {getSentimentIcon(sentiment)}
                    </span>
                    <span style={{ textTransform: "capitalize" }}>{sentiment}</span>
                  </div>
                  <div style={styles.barContainer}>
                    <div
                      style={{
                        ...styles.bar,
                        width: `${percentage}%`,
                        backgroundColor: getSentimentColor(sentiment)
                      }}
                    />
                  </div>
                  <div style={styles.sentimentCount}>
                    {count} ({percentage}%)
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Rating Distribution */}
        <div style={styles.chartCard}>
          <h3 style={styles.chartTitle}>Rating Distribution</h3>
          <div style={styles.ratingBars}>
            {[5, 4, 3, 2, 1].map((rating) => {
              const count = analytics?.rating_distribution?.[rating] || 0;
              const total = analytics?.total_feedback || 1;
              const percentage = ((count / total) * 100).toFixed(1);
              return (
                <div key={rating} style={styles.ratingRow}>
                  <div style={styles.ratingLabel}>
                    {rating} ★
                  </div>
                  <div style={styles.barContainer}>
                    <div
                      style={{
                        ...styles.bar,
                        width: `${percentage}%`,
                        backgroundColor: rating >= 4 ? "#48bb78" : rating === 3 ? "#ed8936" : "#f56565"
                      }}
                    />
                  </div>
                  <div style={styles.ratingCount}>
                    {count}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Top Topics */}
      {analytics?.top_topics && analytics.top_topics.length > 0 && (
        <div style={styles.topicsCard}>
          <h3 style={styles.chartTitle}>Top Feedback Topics</h3>
          <div style={styles.topicsGrid}>
            {analytics.top_topics.map((topic, index) => (
              <div key={index} style={styles.topicBadge}>
                <span style={styles.topicName}>{topic.topic}</span>
                <span style={styles.topicCount}>{topic.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Performance */}
      {agentPerformance?.agents && agentPerformance.agents.length > 0 && (
        <div style={styles.agentCard}>
          <h3 style={styles.chartTitle}>Agent Performance Leaderboard</h3>
          <div style={styles.agentTable}>
            <div style={styles.agentTableHeader}>
              <div style={styles.agentHeaderCell}>Rank</div>
              <div style={styles.agentHeaderCell}>Agent</div>
              <div style={styles.agentHeaderCell}>Avg Rating</div>
              <div style={styles.agentHeaderCell}>Total Feedback</div>
              <div style={styles.agentHeaderCell}>Resolution Rate</div>
              <div style={styles.agentHeaderCell}>Positive</div>
            </div>
            {agentPerformance.agents.map((agent, index) => (
              <div key={agent.agent_id} style={styles.agentTableRow}>
                <div style={styles.agentCell}>
                  <span style={styles.rankBadge}>#{index + 1}</span>
                </div>
                <div style={styles.agentCell}>
                  <div style={styles.agentAvatar}>
                    {agent.agent_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div style={styles.agentName}>{agent.agent_name}</div>
                    <div style={styles.agentEmail}>{agent.agent_email}</div>
                  </div>
                </div>
                <div style={styles.agentCell}>
                  <div style={styles.agentRating}>
                    {agent.average_rating.toFixed(1)} ★
                  </div>
                </div>
                <div style={styles.agentCell}>
                  {agent.total_feedback}
                </div>
                <div style={styles.agentCell}>
                  <span style={{
                    ...styles.rateBadge,
                    backgroundColor: agent.resolution_rate >= 80 ? "#48bb78" : 
                                   agent.resolution_rate >= 60 ? "#ed8936" : "#f56565"
                  }}>
                    {agent.resolution_rate}%
                  </span>
                </div>
                <div style={styles.agentCell}>
                  {agent.positive_feedback}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Feedback */}
      <div style={styles.feedbackCard}>
        <div style={styles.feedbackHeader}>
          <h3 style={styles.chartTitle}>Recent Feedback</h3>
          <div style={styles.sentimentFilter}>
            <button
              style={{
                ...styles.filterButton,
                ...(selectedSentiment === "all" ? styles.filterButtonActive : {})
              }}
              onClick={() => setSelectedSentiment("all")}
            >
              All
            </button>
            <button
              style={{
                ...styles.filterButton,
                ...(selectedSentiment === "positive" ? styles.filterButtonActive : {})
              }}
              onClick={() => setSelectedSentiment("positive")}
            >
              Positive
            </button>
            <button
              style={{
                ...styles.filterButton,
                ...(selectedSentiment === "neutral" ? styles.filterButtonActive : {})
              }}
              onClick={() => setSelectedSentiment("neutral")}
            >
              Neutral
            </button>
            <button
              style={{
                ...styles.filterButton,
                ...(selectedSentiment === "negative" ? styles.filterButtonActive : {})
              }}
              onClick={() => setSelectedSentiment("negative")}
            >
              Negative
            </button>
          </div>
        </div>

        <div style={styles.feedbackList}>
          {recentFeedback.length === 0 ? (
            <div style={styles.emptyState}>
              <p>No feedback found for the selected filter</p>
            </div>
          ) : (
            recentFeedback.map((feedback, index) => (
              <div key={index} style={styles.feedbackItem}>
                <div style={styles.feedbackItemHeader}>
                  <div style={styles.feedbackUser}>
                    <div style={styles.feedbackAvatar}>
                      {feedback.user_name?.charAt(0)?.toUpperCase() || "U"}
                    </div>
                    <div>
                      <div style={styles.feedbackUserName}>
                        {feedback.user_name || "Anonymous"}
                      </div>
                      <div style={styles.feedbackUserEmail}>
                        {feedback.user_email || ""}
                      </div>
                    </div>
                  </div>
                  <div style={styles.feedbackMeta}>
                    {renderStars(feedback.rating)}
                    <span
                      style={{
                        ...styles.sentimentBadge,
                        backgroundColor: getSentimentColor(feedback.sentiment)
                      }}
                    >
                      {getSentimentIcon(feedback.sentiment)} {feedback.sentiment}
                    </span>
                  </div>
                </div>

                {feedback.comment && (
                  <div style={styles.feedbackComment}>
                    "{feedback.comment}"
                  </div>
                )}

                <div style={styles.feedbackFooter}>
                  <span style={styles.feedbackDate}>
                    {new Date(feedback.submitted_at).toLocaleString()}
                  </span>
                  {feedback.issue_resolved && (
                    <span style={styles.resolvedBadge}>✓ Issue Resolved</span>
                  )}
                  {feedback.topics && feedback.topics.length > 0 && (
                    <div style={styles.feedbackTopics}>
                      {feedback.topics.slice(0, 3).map((topic, i) => (
                        <span key={i} style={styles.feedbackTopicTag}>
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    gap: "1.5rem"
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
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "1rem"
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
  periodSelector: {
    display: "flex",
    gap: "0.5rem",
    background: "#f8f9fa",
    padding: "0.5rem",
    borderRadius: "8px"
  },
  periodButton: {
    padding: "0.5rem 1rem",
    background: "transparent",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "0.9rem",
    fontWeight: "500",
    color: "#6c757d",
    transition: "all 0.2s"
  },
  periodButtonActive: {
    background: "#667eea",
    color: "white"
  },
  metricsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
    gap: "1.5rem"
  },
  metricCard: {
    padding: "1.5rem",
    borderRadius: "12px",
    display: "flex",
    alignItems: "center",
    gap: "1rem",
    color: "white"
  },
  metricCardBlue: {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
  },
  metricCardGreen: {
    background: "linear-gradient(135deg, #48bb78 0%, #38a169 100%)"
  },
  metricCardPurple: {
    background: "linear-gradient(135deg, #9f7aea 0%, #805ad5 100%)"
  },
  metricCardOrange: {
    background: "linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)"
  },
  metricIcon: {
    fontSize: "2.5rem",
    opacity: 0.9
  },
  metricLabel: {
    fontSize: "0.875rem",
    fontWeight: "500",
    opacity: 0.9,
    marginBottom: "0.5rem",
    textTransform: "uppercase",
    letterSpacing: "0.5px"
  },
  metricValue: {
    fontSize: "2rem",
    fontWeight: "700",
    marginBottom: "0.25rem"
  },
  metricUnit: {
    fontSize: "1.2rem",
    opacity: 0.8
  },
  metricTrend: {
    fontSize: "0.8rem",
    opacity: 0.9,
    marginTop: "0.25rem"
  },
  metricSubtext: {
    fontSize: "0.8rem",
    opacity: 0.8,
    marginTop: "0.25rem"
  },
  starsDisplay: {
    display: "flex",
    gap: "0.1rem",
    marginTop: "0.25rem"
  },
  chartsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
    gap: "1.5rem"
  },
  chartCard: {
    background: "white",
    padding: "1.5rem",
    borderRadius: "12px",
    border: "1px solid #e0e0e0"
  },
  chartTitle: {
    margin: "0 0 1.5rem 0",
    fontSize: "1.1rem",
    fontWeight: "600",
    color: "#2d3748"
  },
  sentimentBars: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem"
  },
  sentimentRow: {
    display: "flex",
    alignItems: "center",
    gap: "1rem"
  },
  sentimentLabel: {
    minWidth: "100px",
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    fontSize: "0.9rem",
    fontWeight: "500"
  },
  sentimentIcon: {
    fontSize: "1.2rem"
  },
  barContainer: {
    flex: 1,
    height: "24px",
    background: "#f0f0f0",
    borderRadius: "12px",
    overflow: "hidden"
  },
  bar: {
    height: "100%",
    transition: "width 0.3s ease",
    borderRadius: "12px"
  },
  sentimentCount: {
    minWidth: "80px",
    textAlign: "right",
    fontSize: "0.9rem",
    fontWeight: "600",
    color: "#666"
  },
  ratingBars: {
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem"
  },
  ratingRow: {
    display: "flex",
    alignItems: "center",
    gap: "1rem"
  },
  ratingLabel: {
    minWidth: "50px",
    fontSize: "0.9rem",
    fontWeight: "600",
    color: "#666"
  },
  ratingCount: {
    minWidth: "40px",
    textAlign: "right",
    fontSize: "0.9rem",
    fontWeight: "600",
    color: "#666"
  },
  topicsCard: {
    background: "white",
    padding: "1.5rem",
    borderRadius: "12px",
    border: "1px solid #e0e0e0"
  },
  topicsGrid: {
    display: "flex",
    flexWrap: "wrap",
    gap: "0.75rem"
  },
  topicBadge: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    padding: "0.5rem 1rem",
    background: "#f8f9fa",
    borderRadius: "20px",
    border: "1px solid #e0e0e0"
  },
  topicName: {
    fontSize: "0.9rem",
    fontWeight: "500",
    color: "#495057",
    textTransform: "capitalize"
  },
  topicCount: {
    fontSize: "0.8rem",
    fontWeight: "700",
    color: "#667eea",
    background: "#e8eaf6",
    padding: "0.2rem 0.6rem",
    borderRadius: "10px"
  },
  agentCard: {
    background: "white",
    padding: "1.5rem",
    borderRadius: "12px",
    border: "1px solid #e0e0e0"
  },
  agentTable: {
    display: "flex",
    flexDirection: "column",
    gap: "0.5rem"
  },
  agentTableHeader: {
    display: "grid",
    gridTemplateColumns: "60px 2fr 1fr 1fr 1fr 1fr",
    gap: "1rem",
    padding: "0.75rem 1rem",
    background: "#f8f9fa",
    borderRadius: "8px",
    fontWeight: "600",
    fontSize: "0.85rem",
    color: "#666"
  },
  agentHeaderCell: {
    textTransform: "uppercase",
    letterSpacing: "0.5px"
  },
  agentTableRow: {
    display: "grid",
    gridTemplateColumns: "60px 2fr 1fr 1fr 1fr 1fr",
    gap: "1rem",
    padding: "1rem",
    background: "white",
    borderRadius: "8px",
    border: "1px solid #e9ecef",
    alignItems: "center",
    transition: "all 0.2s"
  },
  agentCell: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    fontSize: "0.9rem"
  },
  rankBadge: {
    width: "32px",
    height: "32px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#667eea",
    color: "white",
    borderRadius: "50%",
    fontWeight: "700",
    fontSize: "0.85rem"
  },
  agentAvatar: {
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "600",
    fontSize: "1rem"
  },
  agentName: {
    fontWeight: "600",
    color: "#2d3748",
    fontSize: "0.9rem"
  },
  agentEmail: {
    fontSize: "0.75rem",
    color: "#a0aec0"
  },
  agentRating: {
    fontWeight: "700",
    color: "#ffc107",
    fontSize: "1rem"
  },
  rateBadge: {
    padding: "0.3rem 0.75rem",
    borderRadius: "12px",
    color: "white",
    fontWeight: "600",
    fontSize: "0.85rem"
  },
  feedbackCard: {
    background: "white",
    padding: "1.5rem",
    borderRadius: "12px",
    border: "1px solid #e0e0e0"
  },
  feedbackHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "1.5rem"
  },
  sentimentFilter: {
    display: "flex",
    gap: "0.5rem"
  },
  filterButton: {
    padding: "0.5rem 1rem",
    background: "#f8f9fa",
    border: "1px solid #e0e0e0",
    borderRadius: "6px",
    cursor: "pointer",
    fontSize: "0.85rem",
    fontWeight: "500",
    color: "#6c757d",
    transition: "all 0.2s"
  },
  filterButtonActive: {
    background: "#667eea",
    color: "white",
    borderColor: "#667eea"
  },
  feedbackList: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
    maxHeight: "600px",
    overflowY: "auto"
  },
  feedbackItem: {
    padding: "1.25rem",
    background: "#f8f9fa",
    borderRadius: "12px",
    border: "1px solid #e9ecef"
  },
  feedbackItemHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "0.75rem"
  },
  feedbackUser: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem"
  },
  feedbackAvatar: {
    width: "40px",
    height: "40px",
    borderRadius: "50%",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "600"
  },
  feedbackUserName: {
    fontWeight: "600",
    color: "#2d3748",
    fontSize: "0.9rem"
  },
  feedbackUserEmail: {
    fontSize: "0.75rem",
    color: "#a0aec0"
  },
  feedbackMeta: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem"
  },
  sentimentBadge: {
    padding: "0.3rem 0.75rem",
    borderRadius: "12px",
    color: "white",
    fontWeight: "600",
    fontSize: "0.75rem",
    textTransform: "capitalize"
  },
  feedbackComment: {
    padding: "1rem",
    background: "white",
    borderRadius: "8px",
    fontSize: "0.9rem",
    lineHeight: "1.6",
    color: "#495057",
    fontStyle: "italic",
    marginBottom: "0.75rem"
  },
  feedbackFooter: {
    display: "flex",
    alignItems: "center",
    gap: "1rem",
    flexWrap: "wrap"
  },
  feedbackDate: {
    fontSize: "0.75rem",
    color: "#a0aec0"
  },
  resolvedBadge: {
    padding: "0.25rem 0.75rem",
    background: "#48bb78",
    color: "white",
    borderRadius: "12px",
    fontSize: "0.75rem",
    fontWeight: "600"
  },
  feedbackTopics: {
    display: "flex",
    gap: "0.5rem",
    flexWrap: "wrap"
  },
  feedbackTopicTag: {
    padding: "0.25rem 0.6rem",
    background: "#e8eaf6",
    color: "#667eea",
    borderRadius: "10px",
    fontSize: "0.75rem",
    fontWeight: "500"
  },
  emptyState: {
    textAlign: "center",
    padding: "3rem",
    color: "#a0aec0"
  }
};

// Add CSS animation
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;
if (!document.querySelector('style[data-feedback-analytics-animations]')) {
  styleSheet.setAttribute('data-feedback-analytics-animations', 'true');
  document.head.appendChild(styleSheet);
}

export default FeedbackAnalytics;