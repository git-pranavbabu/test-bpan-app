import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../hooks/useAuthStore';
import api from '../services/api';
import { checkPrinter as checkPrinterHelper } from '../utils/helpers';

export default function Dashboard() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({ today: 0, this_week: 0, this_month: 0 });
  const [statsError, setStatsError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [defaultDate, setDefaultDate] = useState('');
  const [editingDate, setEditingDate] = useState(false);
  const [printerOnline, setPrinterOnline] = useState(false);
  const navigate = useNavigate();
  
  const checkPrinter = async () => {
    const online = await checkPrinterHelper();
    setPrinterOnline(online);
  };

  const fetchStats = async () => {
    try {
      const [statsRes, dateRes] = await Promise.all([
        api.get('/bpan/stats'),
        api.get('/bpan/default-date').catch(() => ({ data: { date: null } })),
      ]);
      setStats(statsRes.data);
      setDefaultDate(dateRes.data.date || '');
    } catch (err) {
      setStatsError('Failed to load BPAN statistics');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    checkPrinter();
    const interval = setInterval(checkPrinter, 30000);
    return () => clearInterval(interval);
  }, []);

  const isAdmin = user?.role === 'admin';
  const canCreate = isAdmin || user?.role === 'production_team';

  const handleDateSave = async (value) => {
    setDefaultDate(value);
    setEditingDate(false);
    if (value) {
      api.post('/bpan/default-date', { date: value }).catch(() => {});
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Welcome, {user?.username}</h1>
        <div className="flex items-center gap-3">
          <div className={`px-4 py-2 rounded text-sm font-medium border flex items-center gap-2 ${
            printerOnline ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'
          }`}>
            <span className={`w-2 h-2 rounded-full ${printerOnline ? 'bg-green-500' : 'bg-red-500'}`}></span>
            {printerOnline ? 'Printer Online' : 'Printer Offline'}
          </div>
          {editingDate && isAdmin ? (
            <input
              type="date"
              className="input py-1 px-2 text-sm"
              value={defaultDate}
              onChange={(e) => setDefaultDate(e.target.value)}
              onBlur={(e) => handleDateSave(e.target.value)}
              autoFocus
            />
          ) : (
            <button 
              onClick={() => isAdmin && setEditingDate(true)}
              className={`px-4 py-2 rounded text-sm font-medium border ${
                isAdmin ? 'cursor-pointer hover:bg-gray-100' : 'cursor-default'
              } ${defaultDate ? 'bg-gray-50 text-blue-700 border-blue-200' : 'bg-gray-50 text-gray-500 border-gray-200'}`}
            >
              📅 {defaultDate || 'Today'}
            </button>
          )}
          {canCreate && (
          <button onClick={() => navigate('/bpan/create')} className="btn btn-primary">
            Create New BPAN
          </button>
          )}
        </div>
      </div>
      
      {statsError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">{statsError}</div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <h3 className="text-gray-500 text-sm">Your Role</h3>
          <p className="text-2xl font-bold capitalize">{user?.role}</p>
        </div>
        <div className="card">
          <h3 className="text-gray-500 text-sm">Today's BPANs</h3>
          <p className="text-2xl font-bold text-blue-600">{stats.today}</p>
        </div>
        <div className="card">
          <h3 className="text-gray-500 text-sm">This Week</h3>
          <p className="text-2xl font-bold text-green-600">{stats.this_week}</p>
        </div>
        <div className="card">
          <h3 className="text-gray-500 text-sm">This Month</h3>
          <p className="text-2xl font-bold text-purple-600">{stats.this_month}</p>
        </div>
      </div>
      
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {canCreate && (
          <button 
            onClick={() => navigate('/bpan/create')} 
            className="p-4 border rounded-lg hover:bg-gray-50 text-center"
          >
            <div className="text-2xl mb-2">+</div>
            <div className="text-sm">Create BPAN</div>
          </button>
          )}
          <button 
            onClick={() => navigate('/bpan/reports')} 
            className="p-4 border rounded-lg hover:bg-gray-50 text-center"
          >
            <div className="text-2xl mb-2">📊</div>
            <div className="text-sm">Reports</div>
          </button>
          {user?.role === 'admin' && (
            <>
              <button 
                onClick={() => navigate('/admin/models')} 
                className="p-4 border rounded-lg hover:bg-gray-50 text-center"
              >
                <div className="text-2xl mb-2">📦</div>
                <div className="text-sm">Manage Models</div>
              </button>
              <button 
                onClick={() => navigate('/admin/lookup')} 
                className="p-4 border rounded-lg hover:bg-gray-50 text-center"
              >
                <div className="text-2xl mb-2">📋</div>
                <div className="text-sm">Lookup Tables</div>
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
