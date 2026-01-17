import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

interface User {
  id: string;
  email: string;
  username: string;
  role: 'admin' | 'premium' | 'demo';
  is_active: boolean;
  created_at: string;
}

interface UserQuota {
  user_id: string;
  daily_used: number;
  daily_limit: number;
  monthly_used: number;
  monthly_limit: number;
  last_reset_daily: string;
  last_reset_monthly: string;
}

interface UserWithQuota extends User {
  quota?: UserQuota;
}

interface SystemStats {
  total_users: number;
  active_users: number;
  total_requests_today: number;
  total_requests_month: number;
  users_by_role: {
    admin: number;
    premium: number;
    demo: number;
  };
}

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<UserWithQuota[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('anonyma_token');

      // Fetch users and stats in parallel
      const [usersRes, statsRes] = await Promise.all([
        fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/admin/users`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/admin/stats`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (!usersRes.ok || !statsRes.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const usersData = await usersRes.json();
      const statsData = await statsRes.json();

      setUsers(usersData);
      setStats(statsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      const token = localStorage.getItem('anonyma_token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/admin/users/${userId}/role`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ role: newRole }),
        }
      );

      if (!response.ok) throw new Error('Failed to update role');

      setSuccessMessage(`User role updated to ${newRole}`);
      setTimeout(() => setSuccessMessage(''), 3000);
      fetchDashboardData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleResetQuota = async (userId: string) => {
    try {
      const token = localStorage.getItem('anonyma_token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/admin/users/${userId}/reset-quota`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error('Failed to reset quota');

      setSuccessMessage('Quota reset successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
      fetchDashboardData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleToggleActive = async (userId: string, isActive: boolean) => {
    try {
      const token = localStorage.getItem('anonyma_token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/admin/users/${userId}/active`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ is_active: !isActive }),
        }
      );

      if (!response.ok) throw new Error('Failed to update user status');

      setSuccessMessage(`User ${!isActive ? 'activated' : 'deactivated'}`);
      setTimeout(() => setSuccessMessage(''), 3000);
      fetchDashboardData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  if (user?.role !== 'admin') {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Access denied. Admin only.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Admin Dashboard</h2>
          <p className="mt-2 text-sm text-gray-600">Manage users and system</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          {successMessage}
        </div>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-blue-100 rounded-md p-3">
                <span className="text-2xl">👥</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Users</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.total_users}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                <span className="text-2xl">✅</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Users</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.active_users}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-purple-100 rounded-md p-3">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Requests Today</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats.total_requests_today}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-yellow-100 rounded-md p-3">
                <span className="text-2xl">📈</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Requests Month</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {stats.total_requests_month}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Role Distribution */}
      {stats && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Users by Role</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-3xl mb-2">👑</div>
              <p className="text-2xl font-bold text-purple-600">{stats.users_by_role.admin}</p>
              <p className="text-sm text-gray-600">Admin</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">⭐</div>
              <p className="text-2xl font-bold text-blue-600">{stats.users_by_role.premium}</p>
              <p className="text-sm text-gray-600">Premium</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">🎯</div>
              <p className="text-2xl font-bold text-gray-600">{stats.users_by_role.demo}</p>
              <p className="text-sm text-gray-600">Demo</p>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Users
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by username or email..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Role
            </label>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Roles</option>
              <option value="admin">Admin</option>
              <option value="premium">Premium</option>
              <option value="demo">Demo</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usage (Daily/Monthly)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{user.username}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className={`text-sm rounded-full px-3 py-1 font-medium ${
                        user.role === 'admin'
                          ? 'bg-purple-100 text-purple-800'
                          : user.role === 'premium'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <option value="admin">👑 Admin</option>
                      <option value="premium">⭐ Premium</option>
                      <option value="demo">🎯 Demo</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {user.quota ? (
                      <div className="text-sm">
                        <div className="text-gray-900">
                          {user.quota.daily_used} / {user.quota.daily_limit}
                        </div>
                        <div className="text-gray-500">
                          {user.quota.monthly_used} / {user.quota.monthly_limit}
                        </div>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">No data</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        user.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <button
                      onClick={() => handleResetQuota(user.id)}
                      className="text-blue-600 hover:text-blue-900"
                      title="Reset quota"
                    >
                      Reset Quota
                    </button>
                    <button
                      onClick={() => handleToggleActive(user.id, user.is_active)}
                      className={`${
                        user.is_active
                          ? 'text-red-600 hover:text-red-900'
                          : 'text-green-600 hover:text-green-900'
                      }`}
                      title={user.is_active ? 'Deactivate' : 'Activate'}
                    >
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredUsers.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No users found matching your criteria.
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
