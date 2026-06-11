import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [stats, setStats] = useState({ today: 0, this_week: 0, last_week: 0, this_month: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [approvingUser, setApprovingUser] = useState(null);
  const [serialInfo, setSerialInfo] = useState({ current: 0, next_serial: 0, max_used: 0 });
  const [newSerial, setNewSerial] = useState('');
  const [serialError, setSerialError] = useState('');
  const [serialSuccess, setSerialSuccess] = useState('');
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [usersRes, pendingRes, statsRes] = await Promise.all([
          api.get('/auth/users'),
          api.get('/auth/users/pending'),
          api.get('/bpan/stats'),
        ]);
        setUsers(usersRes.data);
        setPendingUsers(pendingRes.data);
        setStats(statsRes.data);
      } catch (err) {
        console.error('Failed to fetch data', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
    
    fetchSerialInfo();
  }, []);

  const fetchSerialInfo = async () => {
    try {
      const res = await api.get('/bpan/global-serial');
      setSerialInfo(res.data);
    } catch {
      try {
        const res = await api.get('/bpan/last-serial');
        setSerialInfo({ max_used: res.data.serial_number, next_serial: res.data.serial_number + 1 });
      } catch {
        console.error('Failed to fetch serial info');
      }
    }
  };
  
  const handleApprove = async (userId, approved) => {
    setApprovingUser(userId);
    try {
      await api.post(`/auth/approve/${userId}`, { approved });
      const [usersRes, pendingRes] = await Promise.all([
        api.get('/auth/users'),
        api.get('/auth/users/pending'),
      ]);
      setUsers(usersRes.data);
      setPendingUsers(pendingRes.data);
    } catch (err) {
      alert('Failed to process approval');
    } finally {
      setApprovingUser(null);
    }
};

  const handleSetSerial = async () => {
    setSerialError('');
    setSerialSuccess('');
    const value = parseInt(newSerial);
    if (!value || value < 1) {
      setSerialError('Enter a valid serial number');
      return;
    }
    try {
      const res = await api.put('/bpan/global-serial', { value });
      setSerialSuccess(res.data.message);
      setNewSerial('');
      await fetchSerialInfo();
    } catch (err) {
      setSerialError(err.response?.data?.detail || 'Failed to update serial');
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>;
  }
  
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Admin Dashboard</h1>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="card">
          <h3 className="text-gray-500 text-sm">Today's BPANs</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.today}</p>
        </div>
        <div className="card">
          <h3 className="text-gray-500 text-sm">This Week</h3>
          <p className="text-3xl font-bold text-green-600">{stats.this_week}</p>
        </div>
        <div className="card">
          <h3 className="text-gray-500 text-sm">Last Week</h3>
          <p className="text-3xl font-bold text-orange-600">{stats.last_week}</p>
        </div>
        <div className="card">
          <h3 className="text-gray-500 text-sm">This Month</h3>
          <p className="text-3xl font-bold text-purple-600">{stats.this_month}</p>
        </div>
      </div>
      
      <div className="card">
        <div className="border-b border-gray-200 mb-4">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('users')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'users'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              All Users ({users.length})
            </button>
            <button
              onClick={() => setActiveTab('pending')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'pending'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Pending Approval ({pendingUsers.length})
            </button>
          </nav>
        </div>
        
        {activeTab === 'users' && (
          <table className="table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.username}</td>
                  <td className="capitalize">{u.role}</td>
                  <td>
                    <span className={`px-2 py-1 rounded text-xs ${
                      u.is_approved ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {u.is_approved ? 'Approved' : 'Pending'}
                    </span>
                  </td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        
        {activeTab === 'pending' && (
          <div className="space-y-4">
            {pendingUsers.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No pending users</p>
            ) : (
              pendingUsers.map((u) => (
                <div key={u.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">{u.username}</p>
                    <p className="text-sm text-gray-500">Role: {u.role}</p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleApprove(u.id, true)}
                      disabled={approvingUser === u.id}
                      className="btn btn-primary text-sm"
                    >
                      {approvingUser === u.id ? '...' : 'Approve'}
                    </button>
                    <button
                      onClick={() => handleApprove(u.id, false)}
                      disabled={approvingUser === u.id}
                      className="btn btn-danger text-sm"
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
      
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Global Serial Number</h2>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-500">Last Used Serial</p>
            <p className="text-2xl font-bold">{String(serialInfo.max_used || 0).padStart(4, '0')}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-500">Next Serial Number</p>
            <p className="text-2xl font-bold text-blue-600">{String(serialInfo.next_serial || 1).padStart(4, '0')}</p>
          </div>
        </div>
        <div className="flex gap-3 items-start">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">New Serial Number</label>
            <input type="number" className="input w-full" value={newSerial}
              onChange={(e) => setNewSerial(e.target.value)} placeholder="e.g. 500" min="1" />
          </div>
          <button onClick={handleSetSerial} className="btn btn-primary mt-6">Set Serial</button>
        </div>
        {serialError && <p className="text-red-500 text-sm mt-2">{serialError}</p>}
        {serialSuccess && <p className="text-green-600 text-sm mt-2">{serialSuccess}</p>}
      </div>
    </div>
  );
}
