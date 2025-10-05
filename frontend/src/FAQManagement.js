// import React, { useState, useEffect } from 'react';

// export default function FAQManagement({ token }) {
//   const [activeTab, setActiveTab] = useState('browse');
//   const [faqs, setFaqs] = useState([]);
//   const [categories, setCategories] = useState([]);
//   const [selectedCategory, setSelectedCategory] = useState('all');
//   const [loading, setLoading] = useState(false);
//   const [analytics, setAnalytics] = useState(null);
//   const [gaps, setGaps] = useState([]);
//   const [searchQuery, setSearchQuery] = useState('');
//   const [searchResults, setSearchResults] = useState([]);
//   const [showCreateForm, setShowCreateForm] = useState(false);
//   const [editingFAQ, setEditingFAQ] = useState(null);
//   const [formData, setFormData] = useState({
//     question: '',
//     answer: '',
//     category: 'general',
//     tags: ''
//   });

//   useEffect(() => {
//     fetchFAQs();
//     fetchCategories();
//     fetchAnalytics();
//   }, []);

//   const fetchFAQs = async () => {
//     setLoading(true);
//     try {
//       const response = await fetch('http://127.0.0.1:8000/faq/all', {
//         headers: { Authorization: `Bearer ${token}` }
//       });
//       if (response.ok) {
//         const data = await response.json();
//         setFaqs(data);
//       } else {
//         console.error('Failed to fetch FAQs');
//       }
//     } catch (error) {
//       console.error('Error fetching FAQs:', error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const fetchCategories = async () => {
//     try {
//       const response = await fetch('http://127.0.0.1:8000/faq/categories', {
//         headers: { Authorization: `Bearer ${token}` }
//       });
//       if (response.ok) {
//         const data = await response.json();
//         setCategories(data.categories || []);
//       }
//     } catch (error) {
//       console.error('Error fetching categories:', error);
//     }
//   };

//   const fetchAnalytics = async () => {
//     try {
//       const response = await fetch('http://127.0.0.1:8000/faq/analytics', {
//         headers: { Authorization: `Bearer ${token}` }
//       });
//       if (response.ok) {
//         const data = await response.json();
//         setAnalytics(data);
//       }
//     } catch (error) {
//       console.error('Error fetching analytics:', error);
//     }
//   };

// const createFAQ = async (e) => {
//   e.preventDefault();
  
//   const payload = {
//     question: formData.question,
//     answer: formData.answer,
//     category: formData.category,
//     tags: formData.tags.split(',').map(t => t.trim()).filter(t => t),
//     source: 'manual'
//   };
  
//   console.log('📤 Sending FAQ payload:', payload); // ADD THIS
  
//   try {
//     const response = await fetch('http://127.0.0.1:8000/faq/create', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         Authorization: `Bearer ${token}`
//       },
//       body: JSON.stringify(payload)
//     });

//     console.log('📥 Response status:', response.status); // ADD THIS
    
//     if (response.ok) {
//       alert('FAQ created successfully!');
//       // ... rest
//     } else {
//       const error = await response.json();
//       console.error('❌ Error response:', error); // ADD THIS
//       alert(error.detail || 'Failed to create FAQ');
//     }
//   } catch (error) {
//     console.error('❌ Network error:', error); // ADD THIS
//     alert('Connection error');
//   }
// };

//   const updateFAQ = async (e) => {
//     e.preventDefault();
//     if (!editingFAQ) return;

//     try {
//       const response = await fetch(`http://127.0.0.1:8000/faq/${editingFAQ.faq_id}`, {
//         method: 'PUT',
//         headers: {
//           'Content-Type': 'application/json',
//           Authorization: `Bearer ${token}`
//         },
//         body: JSON.stringify({
//           question: formData.question,
//           answer: formData.answer,
//           category: formData.category,
//           tags: formData.tags.split(',').map(t => t.trim()).filter(t => t)
//         })
//       });

//       if (response.ok) {
//         alert('FAQ updated successfully!');
//         setEditingFAQ(null);
//         setFormData({ question: '', answer: '', category: 'general', tags: '' });
//         fetchFAQs();
//         fetchAnalytics();
//       } else {
//         const error = await response.json();
//         alert(error.detail || 'Failed to update FAQ');
//       }
//     } catch (error) {
//       alert('Connection error');
//     }
//   };

//   const deleteFAQ = async (faqId) => {
//     if (!window.confirm('Are you sure you want to delete this FAQ?')) return;

//     try {
//       const response = await fetch(`http://127.0.0.1:8000/faq/${faqId}`, {
//         method: 'DELETE',
//         headers: { Authorization: `Bearer ${token}` }
//       });

//       if (response.ok) {
//         alert('FAQ deleted successfully');
//         fetchFAQs();
//         fetchAnalytics();
//       } else {
//         alert('Failed to delete FAQ');
//       }
//     } catch (error) {
//       alert('Connection error');
//     }
//   };

//   const searchFAQs = async () => {
//     if (!searchQuery.trim()) return;
//     setLoading(true);
//     try {
//       const response = await fetch('http://127.0.0.1:8000/faq/search', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           Authorization: `Bearer ${token}`
//         },
//         body: JSON.stringify({ query: searchQuery, limit: 10 })
//       });
//       if (response.ok) {
//         const data = await response.json();
//         setSearchResults(data.results || []);
//       }
//     } catch (error) {
//       console.error('Search error:', error);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const learnFromConversations = async () => {
//     if (!window.confirm('Analyze conversations and auto-generate FAQs? This may take a minute.')) return;
//     setLoading(true);
//     try {
//       const response = await fetch('http://127.0.0.1:8000/faq/learning/learn-from-conversations?days=30', {
//         method: 'POST',
//         headers: { Authorization: `Bearer ${token}` }
//       });
//       if (response.ok) {
//         const data = await response.json();
//         alert(`Learning complete!\n\nConversations analyzed: ${data.conversations_analyzed}\nPatterns found: ${data.patterns_found}\nFAQs created: ${data.faqs_created}`);
//         fetchFAQs();
//         fetchAnalytics();
//       } else {
//         alert('Learning failed');
//       }
//     } catch (error) {
//       alert('Connection error');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const analyzeGaps = async () => {
//     setLoading(true);
//     try {
//       const response = await fetch('http://127.0.0.1:8000/faq/learning/analyze-gaps', {
//         method: 'POST',
//         headers: { Authorization: `Bearer ${token}` }
//       });
//       if (response.ok) {
//         const data = await response.json();
//         setGaps(data.missing_topics || []);
//         setActiveTab('gaps');
//         alert(`Found ${data.missing_topics?.length || 0} missing FAQ topics`);
//       }
//     } catch (error) {
//       console.error('Gap analysis error:', error);
//       alert('Failed to analyze gaps');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const startEdit = (faq) => {
//     setEditingFAQ(faq);
//     setFormData({
//       question: faq.question,
//       answer: faq.answer,
//       category: faq.category,
//       tags: faq.tags.join(', ')
//     });
//   };

//   const cancelEdit = () => {
//     setEditingFAQ(null);
//     setFormData({ question: '', answer: '', category: 'general', tags: '' });
//   };

//   const filteredFAQs = selectedCategory === 'all'
//     ? faqs
//     : faqs.filter(f => f.category === selectedCategory);

//   const categoryOptions = [
//     { value: 'general', label: 'General' },
//     { value: 'order_tracking', label: 'Order Tracking' },
//     { value: 'payment', label: 'Payment' },
//     { value: 'delivery', label: 'Delivery' },
//     { value: 'cancellation', label: 'Cancellation' },
//     { value: 'address', label: 'Address' },
//     { value: 'menu', label: 'Menu' },
//     { value: 'account', label: 'Account' },
//     { value: 'promo', label: 'Promo Codes' }
//   ];

//   return (
//     <div style={styles.container}>
//       <div style={styles.header}>
//         <div>
//           <h1 style={styles.title}>FAQ Management</h1>
//           <p style={styles.subtitle}>Manage frequently asked questions and auto-learn from conversations</p>
//         </div>
//         <div style={styles.actions}>
//           <button onClick={() => setShowCreateForm(true)} style={styles.btnPrimary}>
//             + Create FAQ
//           </button>
//           <button onClick={learnFromConversations} style={styles.btnSuccess} disabled={loading}>
//             Auto-Learn FAQs
//           </button>
//           <button onClick={analyzeGaps} style={styles.btnWarning} disabled={loading}>
//             Analyze Gaps
//           </button>
//         </div>
//       </div>

//       {analytics && (
//         <div style={styles.statsGrid}>
//           <div style={styles.statCard}>
//             <div style={styles.statLabel}>Total FAQs</div>
//             <div style={styles.statValue}>{analytics.total_faqs}</div>
//           </div>
//           <div style={styles.statCard}>
//             <div style={styles.statLabel}>Total Usage</div>
//             <div style={styles.statValue}>{analytics.total_usage}</div>
//           </div>
//           <div style={styles.statCard}>
//             <div style={styles.statLabel}>Manual</div>
//             <div style={styles.statValue}>{analytics.faqs_by_source?.manual || 0}</div>
//           </div>
//           <div style={styles.statCard}>
//             <div style={styles.statLabel}>Auto-Generated</div>
//             <div style={styles.statValue}>{analytics.faqs_by_source?.auto_generated || 0}</div>
//           </div>
//         </div>
//       )}

//       <div style={styles.tabs}>
//         {[
//           { id: 'browse', label: 'Browse FAQs' },
//           { id: 'search', label: 'Search' },
//           { id: 'analytics', label: 'Analytics' },
//           { id: 'gaps', label: `Gaps (${gaps.length})` }
//         ].map(tab => (
//           <button
//             key={tab.id}
//             style={{ ...styles.tab, ...(activeTab === tab.id && styles.tabActive) }}
//             onClick={() => setActiveTab(tab.id)}
//           >
//             {tab.label}
//           </button>
//         ))}
//       </div>

//       {(showCreateForm || editingFAQ) && (
//         <div style={styles.modal} onClick={(e) => {
//           if (e.target === e.currentTarget) {
//             setShowCreateForm(false);
//             cancelEdit();
//           }
//         }}>
//           <div style={styles.modalContent}>
//             <h2>{editingFAQ ? 'Edit FAQ' : 'Create New FAQ'}</h2>
//             <form onSubmit={editingFAQ ? updateFAQ : createFAQ}>
//               <div style={styles.formGroup}>
//                 <label style={styles.label}>Question *</label>
//                 <input
//                   type="text"
//                   placeholder="Enter the question"
//                   value={formData.question}
//                   onChange={(e) => setFormData({ ...formData, question: e.target.value })}
//                   required
//                   style={styles.input}
//                 />
//               </div>

//               <div style={styles.formGroup}>
//                 <label style={styles.label}>Answer *</label>
//                 <textarea
//                   placeholder="Enter the answer"
//                   value={formData.answer}
//                   onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
//                   required
//                   rows={5}
//                   style={styles.textarea}
//                 />
//               </div>

//               <div style={styles.formGroup}>
//                 <label style={styles.label}>Category *</label>
//                 <select
//                   value={formData.category}
//                   onChange={(e) => setFormData({ ...formData, category: e.target.value })}
//                   style={styles.select}
//                 >
//                   {categoryOptions.map(opt => (
//                     <option key={opt.value} value={opt.value}>{opt.label}</option>
//                   ))}
//                 </select>
//               </div>

//               <div style={styles.formGroup}>
//                 <label style={styles.label}>Tags (comma separated)</label>
//                 <input
//                   type="text"
//                   placeholder="e.g., order, tracking, delivery"
//                   value={formData.tags}
//                   onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
//                   style={styles.input}
//                 />
//               </div>

//               <div style={styles.modalButtons}>
//                 <button type="submit" style={styles.btnPrimary}>
//                   {editingFAQ ? 'Update' : 'Create'}
//                 </button>
//                 <button
//                   type="button"
//                   onClick={() => {
//                     setShowCreateForm(false);
//                     cancelEdit();
//                   }}
//                   style={styles.btnSecondary}
//                 >
//                   Cancel
//                 </button>
//               </div>
//             </form>
//           </div>
//         </div>
//       )}

//       <div style={styles.content}>
//         {activeTab === 'browse' && (
//           <>
//             <div style={styles.filterRow}>
//               <select
//                 value={selectedCategory}
//                 onChange={(e) => setSelectedCategory(e.target.value)}
//                 style={styles.select}
//               >
//                 <option value="all">All Categories</option>
//                 {categories.map(cat => (
//                   <option key={cat.category} value={cat.category}>
//                     {cat.category} ({cat.count})
//                   </option>
//                 ))}
//               </select>
//             </div>

//             {loading ? (
//               <p style={styles.loadingText}>Loading FAQs...</p>
//             ) : filteredFAQs.length === 0 ? (
//               <div style={styles.emptyState}>
//                 <p>No FAQs found. Create your first FAQ!</p>
//               </div>
//             ) : (
//               <div style={styles.faqList}>
//                 {filteredFAQs.map(faq => (
//                   <div key={faq.faq_id} style={styles.faqCard}>
//                     <div style={styles.faqHeader}>
//                       <h3 style={styles.faqQuestion}>{faq.question}</h3>
//                       <span style={styles.categoryBadge}>{faq.category}</span>
//                     </div>
//                     <p style={styles.faqAnswer}>{faq.answer}</p>
//                     <div style={styles.faqMeta}>
//                       <span>Used: {faq.usage_count}x</span>
//                       <span>Helpful: {faq.helpful_count}</span>
//                       <span>Source: {faq.source}</span>
//                     </div>
//                     {faq.tags && faq.tags.length > 0 && (
//                       <div style={styles.tagContainer}>
//                         {faq.tags.map((tag, idx) => (
//                           <span key={idx} style={styles.tag}>{tag}</span>
//                         ))}
//                       </div>
//                     )}
//                     <div style={styles.faqActions}>
//                       <button onClick={() => startEdit(faq)} style={styles.btnEdit}>
//                         Edit
//                       </button>
//                       <button onClick={() => deleteFAQ(faq.faq_id)} style={styles.btnDanger}>
//                         Delete
//                       </button>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             )}
//           </>
//         )}

//         {activeTab === 'search' && (
//           <div>
//             <div style={styles.searchBox}>
//               <input
//                 type="text"
//                 placeholder="Search FAQs..."
//                 value={searchQuery}
//                 onChange={(e) => setSearchQuery(e.target.value)}
//                 onKeyPress={(e) => e.key === 'Enter' && searchFAQs()}
//                 style={styles.input}
//               />
//               <button onClick={searchFAQs} style={styles.btnPrimary} disabled={loading}>
//                 Search
//               </button>
//             </div>

//             {searchResults.length > 0 && (
//               <div style={styles.faqList}>
//                 {searchResults.map(result => (
//                   <div key={result.faq_id} style={styles.faqCard}>
//                     <div style={styles.faqHeader}>
//                       <h3 style={styles.faqQuestion}>{result.question}</h3>
//                       <span style={styles.categoryBadge}>{result.category}</span>
//                     </div>
//                     <p style={styles.faqAnswer}>{result.answer}</p>
//                     <div style={styles.faqMeta}>
//                       <span>Relevance: {(result.relevance_score * 100).toFixed(0)}%</span>
//                       <span>Used: {result.usage_count}x</span>
//                     </div>
//                   </div>
//                 ))}
//               </div>
//             )}
//           </div>
//         )}

//         {activeTab === 'analytics' && analytics && (
//           <div>
//             <h2 style={styles.sectionTitle}>Top Used FAQs</h2>
//             <div style={styles.analyticsList}>
//               {analytics.top_used_faqs?.map((faq, idx) => (
//                 <div key={idx} style={styles.analyticsCard}>
//                   <div style={styles.rank}>{idx + 1}</div>
//                   <div style={styles.analyticsContent}>
//                     <div style={styles.analyticsQuestion}>{faq.question}</div>
//                     <div style={styles.analyticsMeta}>
//                       {faq.category} • Used {faq.usage_count} times
//                     </div>
//                   </div>
//                 </div>
//               ))}
//             </div>

//             <h2 style={styles.sectionTitle}>Most Helpful FAQs</h2>
//             <div style={styles.analyticsList}>
//               {analytics.most_helpful_faqs?.map((faq, idx) => (
//                 <div key={idx} style={styles.analyticsCard}>
//                   <div style={styles.rank}>{idx + 1}</div>
//                   <div style={styles.analyticsContent}>
//                     <div style={styles.analyticsQuestion}>{faq.question}</div>
//                     <div style={styles.analyticsMeta}>
//                       Helpfulness: {(faq.helpfulness_ratio * 100).toFixed(0)}% ({faq.helpful_count} votes)
//                     </div>
//                   </div>
//                 </div>
//               ))}
//             </div>
//           </div>
//         )}

//         {activeTab === 'gaps' && (
//           <div>
//             <h2 style={styles.sectionTitle}>Missing FAQ Topics</h2>
//             {gaps.length === 0 ? (
//               <div style={styles.emptyState}>
//                 <p>No gaps found. Click "Analyze Gaps" to find missing topics.</p>
//               </div>
//             ) : (
//               <div style={styles.gapsList}>
//                 {gaps.map((gap, idx) => (
//                   <div key={idx} style={styles.gapCard}>
//                     <div style={styles.gapHeader}>
//                       <span style={{...styles.priorityBadge, ...styles[`priority${gap.priority}`]}}>
//                         {gap.priority}
//                       </span>
//                       <span style={styles.frequency}>Frequency: {gap.frequency}</span>
//                     </div>
//                     <h4 style={styles.gapTopic}>{gap.missing_topic}</h4>
//                     <p style={styles.gapQuestion}>Suggested: {gap.suggested_question}</p>
//                     <p style={styles.gapReason}>{gap.reason}</p>
//                   </div>
//                 ))}
//               </div>
//             )}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }
// const styles = {
//   container: { fontFamily: 'system-ui, -apple-system, sans-serif' },

//   // Header
//   header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' },
//   title: { fontSize: '2rem', fontWeight: '700', color: '#1a202c', margin: '0 0 0.5rem 0' },
//   subtitle: { fontSize: '1rem', color: '#718096', margin: 0 },
//   actions: { display: 'flex', gap: '0.75rem' },

//   // Buttons
//   btnPrimary: {
//     padding: '0.75rem 1.5rem',
//     background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
//     color: 'white',
//     border: 'none',
//     borderRadius: '8px',
//     cursor: 'pointer',
//     fontWeight: '600',
//     fontSize: '0.95rem',
//     transition: 'transform 0.2s'
//   },
//   btnSuccess: {
//     padding: '0.75rem 1.5rem',
//     background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
//     color: 'white',
//     border: 'none',
//     borderRadius: '8px',
//     cursor: 'pointer',
//     fontWeight: '600',
//     fontSize: '0.95rem'
//   },
//   btnWarning: {
//     padding: '0.75rem 1.5rem',
//     background: 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)',
//     color: 'white',
//     border: 'none',
//     borderRadius: '8px',
//     cursor: 'pointer',
//     fontWeight: '600',
//     fontSize: '0.95rem'
//   },
//   btnSecondary: {
//     padding: '0.75rem 1.5rem',
//     background: '#e2e8f0',
//     color: '#2d3748',
//     border: 'none',
//     borderRadius: '8px',
//     cursor: 'pointer',
//     fontWeight: '600',
//     fontSize: '0.95rem'
//   },
//   btnDanger: {
//     padding: '0.5rem 1rem',
//     background: '#fc8181',
//     color: 'white',
//     border: 'none',
//     borderRadius: '6px',
//     cursor: 'pointer',
//     fontSize: '0.875rem'
//   },
//   btnEdit: {
//     padding: '0.5rem 1rem',
//     background: '#4299e1',
//     color: 'white',
//     border: 'none',
//     borderRadius: '6px',
//     cursor: 'pointer',
//     fontSize: '0.875rem'
//   },

//   // Stats
//   statsGrid: {
//     display: 'grid',
//     gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
//     gap: '1rem',
//     marginBottom: '2rem'
//   },
//   statCard: {
//     background: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
//     padding: '1.5rem',
//     borderRadius: '12px',
//     border: '1px solid #e2e8f0'
//   },
//   statLabel: {
//     fontSize: '0.875rem',
//     color: '#718096',
//     fontWeight: '600',
//     marginBottom: '0.5rem',
//     textTransform: 'uppercase',
//     letterSpacing: '0.5px'
//   },
//   statValue: { fontSize: '2rem', fontWeight: '700', color: '#2d3748' },

//   // Tabs
//   tabs: {
//     display: 'flex',
//     gap: '0.5rem',
//     marginBottom: '2rem',
//     borderBottom: '2px solid #e2e8f0',
//     paddingBottom: '0'
//   },
//   tab: {
//     padding: '0.75rem 1.5rem',
//     border: 'none',
//     background: 'transparent',
//     cursor: 'pointer',
//     fontSize: '0.95rem',
//     fontWeight: '600',
//     color: '#718096',
//     borderBottom: '3px solid transparent',
//     transition: 'all 0.2s'
//   },
//   tabActive: { color: '#667eea', borderBottom: '3px solid #667eea' },

//   // Content
//   content: {
//     background: 'white',
//     borderRadius: '12px',
//     padding: '2rem',
//     boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
//   },

//   // Inputs
//   filterRow: { marginBottom: '1.5rem' },
//   select: {
//     width: '100%',
//     maxWidth: '300px',
//     padding: '0.75rem',
//     borderRadius: '8px',
//     border: '1px solid #cbd5e0',
//     fontSize: '0.95rem',
//     background: 'white'
//   },
//   input: {
//     width: '100%',
//     padding: '0.75rem',
//     borderRadius: '8px',
//     border: '1px solid #cbd5e0',
//     fontSize: '0.95rem',
//     marginBottom: '1rem'
//   },
//   textarea: {
//     width: '100%',
//     padding: '0.75rem',
//     borderRadius: '8px',
//     border: '1px solid #cbd5e0',
//     fontSize: '0.95rem',
//     fontFamily: 'inherit',
//     resize: 'vertical'
//   },

//   // States
//   loadingText: { textAlign: 'center', color: '#718096', fontSize: '1rem', padding: '2rem' },
//   emptyState: { textAlign: 'center', padding: '3rem', color: '#718096' },

//   // FAQ Section
//   faqList: { display: 'flex', flexDirection: 'column', gap: '1rem' },
//   faqCard: {
//     background: '#f7fafc',
//     border: '1px solid #e2e8f0',
//     borderRadius: '12px',
//     padding: '1.5rem',
//     transition: 'all 0.2s'
//   },
//   faqHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' },
//   faqQuestion: { fontSize: '1.125rem', fontWeight: '600', color: '#2d3748', margin: 0, flex: 1 },
//   categoryBadge: {
//     padding: '0.25rem 0.75rem',
//     background: '#667eea',
//     color: 'white',
//     borderRadius: '12px',
//     fontSize: '0.75rem',
//     fontWeight: '600',
//     textTransform: 'uppercase',
//     marginLeft: '1rem'
//   },
//   faqAnswer: { color: '#4a5568', fontSize: '0.95rem', lineHeight: '1.6', marginBottom: '1rem' },
//   faqMeta: { display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#718096', marginBottom: '0.75rem' },
//   tagContainer: { display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' },
//   tag: { padding: '0.25rem 0.75rem', background: '#e2e8f0', color: '#4a5568', borderRadius: '12px', fontSize: '0.75rem' },
//   faqActions: { display: 'flex', gap: '0.75rem', marginTop: '1rem' },

//   // Modal
//   modal: {
//     position: 'fixed',
//     top: 0,
//     left: 0,
//     right: 0,
//     bottom: 0,
//     background: 'rgba(0, 0, 0, 0.5)',
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'center',
//     zIndex: 1000,
//     padding: '1rem'
//   },
//   modalContent: {
//     background: 'white',
//     borderRadius: '12px',
//     padding: '2rem',
//     width: '100%',
//     maxWidth: '600px',
//     maxHeight: '90vh',
//     overflow: 'auto'
//   },
//   formGroup: { marginBottom: '1.5rem' },
//   label: {
//     display: 'block',
//     marginBottom: '0.5rem',
//     fontWeight: '600',
//     color: '#2d3748',
//     fontSize: '0.95rem'
//   },
//   modalButtons: { display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' },

//   // Search
//   searchBox: { display: 'flex', gap: '1rem', marginBottom: '2rem' },

//   // Analytics
//   sectionTitle: {
//     fontSize: '1.5rem',
//     fontWeight: '700',
//     color: '#2d3748',
//     marginBottom: '1.5rem',
//     marginTop: '2rem'
//   },
//   analyticsList: { display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' },
//   analyticsCard: {
//     display: 'flex',
//     gap: '1rem',
//     background: '#f7fafc',
//     padding: '1rem',
//     borderRadius: '8px',
//     border: '1px solid #e2e8f0'
//   },
//   rank: {
//     width: '40px',
//     height: '40px',
//     borderRadius: '50%',
//     background: '#667eea',
//     color: 'white',
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'center',
//     fontWeight: '700',
//     fontSize: '1.25rem',
//     flexShrink: 0
//   },
//   analyticsContent: { flex: 1 },
//   analyticsQuestion: { fontWeight: '600', color: '#2d3748', marginBottom: '0.5rem' },
//   analyticsMeta: { fontSize: '0.875rem', color: '#718096' },

//   // Gaps Section
//   gapsList: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1rem' },
//   gapCard: { background: '#fff5f5', border: '1px solid #feb2b2', borderRadius: '12px', padding: '1.5rem' },
//   gapHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' },
//   priorityBadge: {
//     padding: '0.25rem 0.75rem',
//     borderRadius: '12px',
//     fontSize: '0.75rem',
//     fontWeight: '700',
//     textTransform: 'uppercase'
//   },
//   priorityhigh: { background: '#fc8181', color: 'white' },
//   prioritymedium: { background: '#f6ad55', color: 'white' },
//   prioritylow: { background: '#68d391', color: 'white' },
//   frequency: { fontSize: '0.875rem', color: '#718096' },
//   gapTopic: { fontSize: '1.125rem', fontWeight: '600', color: '#2d3748', marginBottom: '0.5rem' },
//   gapQuestion: { fontSize: '0.95rem', color: '#4a5568', marginBottom: '0.5rem', fontStyle: 'italic' },
//   gapReason: { fontSize: '0.875rem', color: '#718096' }
// };

import React, { useState, useEffect } from 'react';
import API_BASE_URL from './config';

export default function FAQManagement({ token }) {
  const [activeTab, setActiveTab] = useState('browse');
  const [faqs, setFaqs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingFAQ, setEditingFAQ] = useState(null);
  const [formData, setFormData] = useState({
    question: '',
    answer: '',
    category: 'general',
    tags: ''
  });

  useEffect(() => {
    fetchFAQs();
    fetchCategories();
    fetchAnalytics();
  }, []);

  const fetchFAQs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/faq/all`, { // REPLACED URL
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setFaqs(data);
      } else {
        console.error('Failed to fetch FAQs');
      }
    } catch (error) {
      console.error('Error fetching FAQs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/faq/categories`, { // REPLACED URL
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories || []);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/faq/analytics`, { // REPLACED URL
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

const createFAQ = async (e) => {
  e.preventDefault();
  
  const payload = {
    question: formData.question,
    answer: formData.answer,
    category: formData.category,
    tags: formData.tags.split(',').map(t => t.trim()).filter(t => t),
    source: 'manual'
  };
  
  console.log('📤 Sending FAQ payload:', payload); // ADD THIS
  
  try {
    const response = await fetch(`${API_BASE_URL}/faq/create`, { // REPLACED URL
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });

    console.log('📥 Response status:', response.status); // ADD THIS
    
    if (response.ok) {
      alert('FAQ created successfully!');
      // ... rest
    } else {
      const error = await response.json();
      console.error('❌ Error response:', error); // ADD THIS
      alert(error.detail || 'Failed to create FAQ');
    }
  } catch (error) {
    console.error('❌ Network error:', error); // ADD THIS
    alert('Connection error');
  }
};

  const updateFAQ = async (e) => {
    e.preventDefault();
    if (!editingFAQ) return;

    try {
      const response = await fetch(`${API_BASE_URL}/faq/${editingFAQ.faq_id}`, { // REPLACED URL
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          question: formData.question,
          answer: formData.answer,
          category: formData.category,
          tags: formData.tags.split(',').map(t => t.trim()).filter(t => t)
        })
      });

      if (response.ok) {
        alert('FAQ updated successfully!');
        setEditingFAQ(null);
        setFormData({ question: '', answer: '', category: 'general', tags: '' });
        fetchFAQs();
        fetchAnalytics();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to update FAQ');
      }
    } catch (error) {
      alert('Connection error');
    }
  };

  const deleteFAQ = async (faqId) => {
    if (!window.confirm('Are you sure you want to delete this FAQ?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/faq/${faqId}`, { // REPLACED URL
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('FAQ deleted successfully');
        fetchFAQs();
        fetchAnalytics();
      } else {
        alert('Failed to delete FAQ');
      }
    } catch (error) {
      alert('Connection error');
    }
  };

  const searchFAQs = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/faq/search`, { // REPLACED URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ query: searchQuery, limit: 10 })
      });
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const learnFromConversations = async () => {
    if (!window.confirm('Analyze conversations and auto-generate FAQs? This may take a minute.')) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/faq/learning/learn-from-conversations?days=30`, { // REPLACED URL
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        alert(`Learning complete!\n\nConversations analyzed: ${data.conversations_analyzed}\nPatterns found: ${data.patterns_found}\nFAQs created: ${data.faqs_created}`);
        fetchFAQs();
        fetchAnalytics();
      } else {
        alert('Learning failed');
      }
    } catch (error) {
      alert('Connection error');
    } finally {
      setLoading(false);
    }
  };

  const analyzeGaps = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/faq/learning/analyze-gaps`, { // REPLACED URL
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setGaps(data.missing_topics || []);
        setActiveTab('gaps');
        alert(`Found ${data.missing_topics?.length || 0} missing FAQ topics`);
      }
    } catch (error) {
      console.error('Gap analysis error:', error);
      alert('Failed to analyze gaps');
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (faq) => {
    setEditingFAQ(faq);
    setFormData({
      question: faq.question,
      answer: faq.answer,
      category: faq.category,
      tags: faq.tags.join(', ')
    });
  };

  const cancelEdit = () => {
    setEditingFAQ(null);
    setFormData({ question: '', answer: '', category: 'general', tags: '' });
  };

  const filteredFAQs = selectedCategory === 'all'
    ? faqs
    : faqs.filter(f => f.category === selectedCategory);

  const categoryOptions = [
    { value: 'general', label: 'General' },
    { value: 'order_tracking', label: 'Order Tracking' },
    { value: 'payment', label: 'Payment' },
    { value: 'delivery', label: 'Delivery' },
    { value: 'cancellation', label: 'Cancellation' },
    { value: 'address', label: 'Address' },
    { value: 'menu', label: 'Menu' },
    { value: 'account', label: 'Account' },
    { value: 'promo', label: 'Promo Codes' }
  ];

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>FAQ Management</h1>
          <p style={styles.subtitle}>Manage frequently asked questions and auto-learn from conversations</p>
        </div>
        <div style={styles.actions}>
          <button onClick={() => setShowCreateForm(true)} style={styles.btnPrimary}>
            + Create FAQ
          </button>
          <button onClick={learnFromConversations} style={styles.btnSuccess} disabled={loading}>
            Auto-Learn FAQs
          </button>
          <button onClick={analyzeGaps} style={styles.btnWarning} disabled={loading}>
            Analyze Gaps
          </button>
        </div>
      </div>

      {analytics && (
        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Total FAQs</div>
            <div style={styles.statValue}>{analytics.total_faqs}</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Total Usage</div>
            <div style={styles.statValue}>{analytics.total_usage}</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Manual</div>
            <div style={styles.statValue}>{analytics.faqs_by_source?.manual || 0}</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Auto-Generated</div>
            <div style={styles.statValue}>{analytics.faqs_by_source?.auto_generated || 0}</div>
          </div>
        </div>
      )}

      <div style={styles.tabs}>
        {[
          { id: 'browse', label: 'Browse FAQs' },
          { id: 'search', label: 'Search' },
          { id: 'analytics', label: 'Analytics' },
          { id: 'gaps', label: `Gaps (${gaps.length})` }
        ].map(tab => (
          <button
            key={tab.id}
            style={{ ...styles.tab, ...(activeTab === tab.id && styles.tabActive) }}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {(showCreateForm || editingFAQ) && (
        <div style={styles.modal} onClick={(e) => {
          if (e.target === e.currentTarget) {
            setShowCreateForm(false);
            cancelEdit();
          }
        }}>
          <div style={styles.modalContent}>
            <h2>{editingFAQ ? 'Edit FAQ' : 'Create New FAQ'}</h2>
            <form onSubmit={editingFAQ ? updateFAQ : createFAQ}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Question *</label>
                <input
                  type="text"
                  placeholder="Enter the question"
                  value={formData.question}
                  onChange={(e) => setFormData({ ...formData, question: e.target.value })}
                  required
                  style={styles.input}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Answer *</label>
                <textarea
                  placeholder="Enter the answer"
                  value={formData.answer}
                  onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                  required
                  rows={5}
                  style={styles.textarea}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Category *</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  style={styles.select}
                >
                  {categoryOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Tags (comma separated)</label>
                <input
                  type="text"
                  placeholder="e.g., order, tracking, delivery"
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  style={styles.input}
                />
              </div>

              <div style={styles.modalButtons}>
                <button type="submit" style={styles.btnPrimary}>
                  {editingFAQ ? 'Update' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    cancelEdit();
                  }}
                  style={styles.btnSecondary}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div style={styles.content}>
        {activeTab === 'browse' && (
          <>
            <div style={styles.filterRow}>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                style={styles.select}
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat.category} value={cat.category}>
                    {cat.category} ({cat.count})
                  </option>
                ))}
              </select>
            </div>

            {loading ? (
              <p style={styles.loadingText}>Loading FAQs...</p>
            ) : filteredFAQs.length === 0 ? (
              <div style={styles.emptyState}>
                <p>No FAQs found. Create your first FAQ!</p>
              </div>
            ) : (
              <div style={styles.faqList}>
                {filteredFAQs.map(faq => (
                  <div key={faq.faq_id} style={styles.faqCard}>
                    <div style={styles.faqHeader}>
                      <h3 style={styles.faqQuestion}>{faq.question}</h3>
                      <span style={styles.categoryBadge}>{faq.category}</span>
                    </div>
                    <p style={styles.faqAnswer}>{faq.answer}</p>
                    <div style={styles.faqMeta}>
                      <span>Used: {faq.usage_count}x</span>
                      <span>Helpful: {faq.helpful_count}</span>
                      <span>Source: {faq.source}</span>
                    </div>
                    {faq.tags && faq.tags.length > 0 && (
                      <div style={styles.tagContainer}>
                        {faq.tags.map((tag, idx) => (
                          <span key={idx} style={styles.tag}>{tag}</span>
                        ))}
                      </div>
                    )}
                    <div style={styles.faqActions}>
                      <button onClick={() => startEdit(faq)} style={styles.btnEdit}>
                        Edit
                      </button>
                      <button onClick={() => deleteFAQ(faq.faq_id)} style={styles.btnDanger}>
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {activeTab === 'search' && (
          <div>
            <div style={styles.searchBox}>
              <input
                type="text"
                placeholder="Search FAQs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && searchFAQs()}
                style={styles.input}
              />
              <button onClick={searchFAQs} style={styles.btnPrimary} disabled={loading}>
                Search
              </button>
            </div>

            {searchResults.length > 0 && (
              <div style={styles.faqList}>
                {searchResults.map(result => (
                  <div key={result.faq_id} style={styles.faqCard}>
                    <div style={styles.faqHeader}>
                      <h3 style={styles.faqQuestion}>{result.question}</h3>
                      <span style={styles.categoryBadge}>{result.category}</span>
                    </div>
                    <p style={styles.faqAnswer}>{result.answer}</p>
                    <div style={styles.faqMeta}>
                      <span>Relevance: {(result.relevance_score * 100).toFixed(0)}%</span>
                      <span>Used: {result.usage_count}x</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && analytics && (
          <div>
            <h2 style={styles.sectionTitle}>Top Used FAQs</h2>
            <div style={styles.analyticsList}>
              {analytics.top_used_faqs?.map((faq, idx) => (
                <div key={idx} style={styles.analyticsCard}>
                  <div style={styles.rank}>{idx + 1}</div>
                  <div style={styles.analyticsContent}>
                    <div style={styles.analyticsQuestion}>{faq.question}</div>
                    <div style={styles.analyticsMeta}>
                      {faq.category} • Used {faq.usage_count} times
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <h2 style={styles.sectionTitle}>Most Helpful FAQs</h2>
            <div style={styles.analyticsList}>
              {analytics.most_helpful_faqs?.map((faq, idx) => (
                <div key={idx} style={styles.analyticsCard}>
                  <div style={styles.rank}>{idx + 1}</div>
                  <div style={styles.analyticsContent}>
                    <div style={styles.analyticsQuestion}>{faq.question}</div>
                    <div style={styles.analyticsMeta}>
                      Helpfulness: {(faq.helpfulness_ratio * 100).toFixed(0)}% ({faq.helpful_count} votes)
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'gaps' && (
          <div>
            <h2 style={styles.sectionTitle}>Missing FAQ Topics</h2>
            {gaps.length === 0 ? (
              <div style={styles.emptyState}>
                <p>No gaps found. Click "Analyze Gaps" to find missing topics.</p>
              </div>
            ) : (
              <div style={styles.gapsList}>
                {gaps.map((gap, idx) => (
                  <div key={idx} style={styles.gapCard}>
                    <div style={styles.gapHeader}>
                      <span style={{...styles.priorityBadge, ...styles[`priority${gap.priority}`]}}>
                        {gap.priority}
                      </span>
                      <span style={styles.frequency}>Frequency: {gap.frequency}</span>
                    </div>
                    <h4 style={styles.gapTopic}>{gap.missing_topic}</h4>
                    <p style={styles.gapQuestion}>Suggested: {gap.suggested_question}</p>
                    <p style={styles.gapReason}>{gap.reason}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
const styles = {
  container: { fontFamily: 'system-ui, -apple-system, sans-serif' },

  // Header
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' },
  title: { fontSize: '2rem', fontWeight: '700', color: '#1a202c', margin: '0 0 0.5rem 0' },
  subtitle: { fontSize: '1rem', color: '#718096', margin: 0 },
  actions: { display: 'flex', gap: '0.75rem' },

  // Buttons
  btnPrimary: {
    padding: '0.75rem 1.5rem',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '600',
    fontSize: '0.95rem',
    transition: 'transform 0.2s'
  },
  btnSuccess: {
    padding: '0.75rem 1.5rem',
    background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '600',
    fontSize: '0.95rem'
  },
  btnWarning: {
    padding: '0.75rem 1.5rem',
    background: 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '600',
    fontSize: '0.95rem'
  },
  btnSecondary: {
    padding: '0.75rem 1.5rem',
    background: '#e2e8f0',
    color: '#2d3748',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '600',
    fontSize: '0.95rem'
  },
  btnDanger: {
    padding: '0.5rem 1rem',
    background: '#fc8181',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.875rem'
  },
  btnEdit: {
    padding: '0.5rem 1rem',
    background: '#4299e1',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.875rem'
  },

  // Stats
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
    marginBottom: '2rem'
  },
  statCard: {
    background: 'linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)',
    padding: '1.5rem',
    borderRadius: '12px',
    border: '1px solid #e2e8f0'
  },
  statLabel: {
    fontSize: '0.875rem',
    color: '#718096',
    fontWeight: '600',
    marginBottom: '0.5rem',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  },
  statValue: { fontSize: '2rem', fontWeight: '700', color: '#2d3748' },

  // Tabs
  tabs: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '2rem',
    borderBottom: '2px solid #e2e8f0',
    paddingBottom: '0'
  },
  tab: {
    padding: '0.75rem 1.5rem',
    border: 'none',
    background: 'transparent',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: '600',
    color: '#718096',
    borderBottom: '3px solid transparent',
    transition: 'all 0.2s'
  },
  tabActive: { color: '#667eea', borderBottom: '3px solid #667eea' },

  // Content
  content: {
    background: 'white',
    borderRadius: '12px',
    padding: '2rem',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
  },

  // Inputs
  filterRow: { marginBottom: '1.5rem' },
  select: {
    width: '100%',
    maxWidth: '300px',
    padding: '0.75rem',
    borderRadius: '8px',
    border: '1px solid #cbd5e0',
    fontSize: '0.95rem',
    background: 'white'
  },
  input: {
    width: '100%',
    padding: '0.75rem',
    borderRadius: '8px',
    border: '1px solid #cbd5e0',
    fontSize: '0.95rem',
    marginBottom: '1rem'
  },
  textarea: {
    width: '100%',
    padding: '0.75rem',
    borderRadius: '8px',
    border: '1px solid #cbd5e0',
    fontSize: '0.95rem',
    fontFamily: 'inherit',
    resize: 'vertical'
  },

  // States
  loadingText: { textAlign: 'center', color: '#718096', fontSize: '1rem', padding: '2rem' },
  emptyState: { textAlign: 'center', padding: '3rem', color: '#718096' },

  // FAQ Section
  faqList: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  faqCard: {
    background: '#f7fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
    padding: '1.5rem',
    transition: 'all 0.2s'
  },
  faqHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' },
  faqQuestion: { fontSize: '1.125rem', fontWeight: '600', color: '#2d3748', margin: 0, flex: 1 },
  categoryBadge: {
    padding: '0.25rem 0.75rem',
    background: '#667eea',
    color: 'white',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: '600',
    textTransform: 'uppercase',
    marginLeft: '1rem'
  },
  faqAnswer: { color: '#4a5568', fontSize: '0.95rem', lineHeight: '1.6', marginBottom: '1rem' },
  faqMeta: { display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#718096', marginBottom: '0.75rem' },
  tagContainer: { display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' },
  tag: { padding: '0.25rem 0.75rem', background: '#e2e8f0', color: '#4a5568', borderRadius: '12px', fontSize: '0.75rem' },
  faqActions: { display: 'flex', gap: '0.75rem', marginTop: '1rem' },

  // Modal
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '1rem'
  },
  modalContent: {
    background: 'white',
    borderRadius: '12px',
    padding: '2rem',
    width: '100%',
    maxWidth: '600px',
    maxHeight: '90vh',
    overflow: 'auto'
  },
  formGroup: { marginBottom: '1.5rem' },
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    fontWeight: '600',
    color: '#2d3748',
    fontSize: '0.95rem'
  },
  modalButtons: { display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '2rem' },

  // Search
  searchBox: { display: 'flex', gap: '1rem', marginBottom: '2rem' },

  // Analytics
  sectionTitle: {
    fontSize: '1.5rem',
    fontWeight: '700',
    color: '#2d3748',
    marginBottom: '1.5rem',
    marginTop: '2rem'
  },
  analyticsList: { display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' },
  analyticsCard: {
    display: 'flex',
    gap: '1rem',
    background: '#f7fafc',
    padding: '1rem',
    borderRadius: '8px',
    border: '1px solid #e2e8f0'
  },
  rank: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: '#667eea',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: '700',
    fontSize: '1.25rem',
    flexShrink: 0
  },
  analyticsContent: { flex: 1 },
  analyticsQuestion: { fontWeight: '600', color: '#2d3748', marginBottom: '0.5rem' },
  analyticsMeta: { fontSize: '0.875rem', color: '#718096' },

  // Gaps Section
  gapsList: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1rem' },
  gapCard: { background: '#fff5f5', border: '1px solid #feb2b2', borderRadius: '12px', padding: '1.5rem' },
  gapHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' },
  priorityBadge: {
    padding: '0.25rem 0.75rem',
    borderRadius: '12px',
    fontSize: '0.75rem',
    fontWeight: '700',
    textTransform: 'uppercase'
  },
  priorityhigh: { background: '#fc8181', color: 'white' },
  prioritymedium: { background: '#f6ad55', color: 'white' },
  prioritylow: { background: '#68d391', color: 'white' },
  frequency: { fontSize: '0.875rem', color: '#718096' },
  gapTopic: { fontSize: '1.125rem', fontWeight: '600', color: '#2d3748', marginBottom: '0.5rem' },
  gapQuestion: { fontSize: '0.95rem', color: '#4a5568', marginBottom: '0.5rem', fontStyle: 'italic' },
  gapReason: { fontSize: '0.875rem', color: '#718096' }
};