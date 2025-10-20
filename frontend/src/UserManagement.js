
import React, { useState, useEffect } from "react";
import API_BASE_URL from './config';

function UserManagement({ token }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editingUser, setEditingUser] = useState(null);
  const [newRole, setNewRole] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, [token]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      // Line 16: fetch(${API_BASE_URL}/auth/users, {
      const response = await fetch(`${API_BASE_URL}/auth/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else {
        setError("Failed to fetch users");
      }
    } catch (err) {
      setError("Connection error");
    } finally {
      setLoading(false);
    }
  };

  const handleRoleUpdate = async (userId, currentRole) => {
    if (!newRole || newRole === currentRole) {
      setEditingUser(null);
      setNewRole("");
      return;
    }

    setIsUpdating(true);
    try {
      // Line 37: fetch(${API_BASE_URL}/auth/update-role, {
      const response = await fetch(`${API_BASE_URL}/auth/update-role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: userId,
          new_role: newRole,
        }),
      });

      if (response.ok) {
        // Refresh users list
        await fetchUsers();
        setEditingUser(null);
        setNewRole("");
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to update user role");
      }
    } catch (err) {
      setError("Connection error while updating role");
    } finally {
      setIsUpdating(false);
    }
  };

  const startEditing = (userId, currentRole) => {
    setEditingUser(userId);
    setNewRole(currentRole);
    setError("");
  };

  const cancelEditing = () => {
    setEditingUser(null);
    setNewRole("");
    setError("");
  };

  const getRoleColor = (role) => {
    switch (role) {
      case "admin":
        return "#dc3545"; // Red
      case "customer_support_agent":
        return "#28a745"; // Green
      case "user":
        return "#6c757d"; // Gray
      default:
        return "#6c757d";
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return <div className="loading-spinner">Loading users...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">{error}</div>
        <button onClick={fetchUsers} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="user-management">
      <div className="section-header">
        <h2>User Management</h2>
        <p>Manage user roles and permissions</p>
      </div>

      <div className="users-stats">
        <div className="stat-item">
          <span className="stat-label">Total Users:</span>
          <span className="stat-value">{users.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Admins:</span>
          <span className="stat-value">
            {users.filter(u => u.role === "admin").length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Support Agents:</span>
          <span className="stat-value">
            {users.filter(u => u.role === "customer_support_agent").length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Regular Users:</span>
          <span className="stat-value">
            {users.filter(u => u.role === "user").length}
          </span>
        </div>
      </div>

      <div className="users-table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>User ID</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user._id || user.user_id}>
                <td className="user-name">{user.name}</td>
                <td className="user-email">{user.email}</td>
                <td>
                  {editingUser === user.user_id ? (
                    <select
                      value={newRole}
                      onChange={(e) => setNewRole(e.target.value)}
                      className="role-select"
                      disabled={isUpdating}
                    >
                      <option value="user">User</option>
                      <option value="customer_support_agent">Support Agent</option>
                      <option value="admin">Admin</option>
                    </select>
                  ) : (
                    <span 
                      className="role-badge"
                      style={{ backgroundColor: getRoleColor(user.role) }}
                    >
                      {user.role.replace("_", " ").toUpperCase()}
                    </span>
                  )}
                </td>
                <td className="user-id">{user.user_id}</td>
                <td className="created-date">{formatDate(user.created_at)}</td>
                <td className="actions">
                  {editingUser === user.user_id ? (
                    <div className="edit-actions">
                      <button
                        onClick={() => handleRoleUpdate(user.user_id, user.role)}
                        disabled={isUpdating}
                        className="save-btn"
                      >
                        {isUpdating ? "Saving..." : "Save"}
                      </button>
                      <button
                        onClick={cancelEditing}
                        disabled={isUpdating}
                        className="cancel-btn"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => startEditing(user.user_id, user.role)}
                      className="edit-btn"
                    >
                      Edit Role
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {users.length === 0 && (
          <div className="no-users">
            <p>No users found</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default UserManagement;