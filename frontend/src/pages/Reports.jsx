import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../hooks/useAuthStore';
import api from '../services/api';
import { QR_URL } from '../utils/constants';
import { copyToClipboard } from '../utils/helpers';

export default function Reports() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === 'admin';
  const [reports, setReports] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    model_name: '',
    date_from: '',
    date_to: '',
    serial_from: '',
    serial_to: '',
  });
  const [showEditModal, setShowEditModal] = useState(false);
  const [editBPAN, setEditBPAN] = useState(null);
  const [editDate, setEditDate] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const PAGE_SIZE = 50;
  const [models, setModels] = useState([]);
  const [editModelId, setEditModelId] = useState('');
  const [editError, setEditError] = useState('');
  const [copiedCode, setCopiedCode] = useState('');
  const navigate = useNavigate();

  const goToPage = (newPage) => {
    if (searchResults || searchQuery || Object.values(filters).some(v => v)) {
      handleSearch(null, newPage);
    } else {
      fetchAllReports(newPage);
    }
  };

  const copyBPAN = async (text) => {
    await copyToClipboard(text);
    setCopiedCode(text);
    setTimeout(() => setCopiedCode(''), 2000);
  };

  useEffect(() => {
    fetchAllReports();
  }, []);

  const fetchModels = async () => {
    try {
      const res = await api.get('/bpan/models-for-creation');
      setModels(res.data);
    } catch (err) {
      console.error('Failed to fetch models', err);
    }
  };

  const fetchAllReports = async (pageNumber = 1) => {
    setIsLoading(true);
    try {
      const skip = (pageNumber - 1) * PAGE_SIZE;
      const response = await api.get(`/bpan/reports?skip=${skip}&limit=${PAGE_SIZE}`);
      setReports(response.data.items || response.data);
      setTotalCount(response.data.total || 0);
      setPage(pageNumber);
    } catch (err) {
      console.error('Failed to fetch reports', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (e, pageNumber = 1) => {
    if (e && e.preventDefault) e.preventDefault();
    if (searchQuery.length > 0 && searchQuery.length < 2) {
      setSearchError('Enter at least 2 characters');
      return;
    }
    setIsSearching(true);
    setSearchError('');
    try {
      const skip = (pageNumber - 1) * PAGE_SIZE;
      const params = new URLSearchParams({ skip, limit: PAGE_SIZE });
      if (searchQuery) params.set('q', searchQuery);
      if (filters.model_name) params.set('model_name', filters.model_name);
      if (filters.date_from) params.set('date_from', filters.date_from);
      if (filters.date_to) params.set('date_to', filters.date_to);
      if (filters.serial_from) params.set('serial_from', filters.serial_from);
      if (filters.serial_to) params.set('serial_to', filters.serial_to);
      const response = await api.get(`/bpan/reports?${params.toString()}`);
      setSearchResults(response.data.items || response.data);
      setTotalCount(response.data.total || 0);
      setPage(pageNumber);
    } catch (err) {
      setSearchError('Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  const handleClear = () => {
    setPage(1);
    setSearchQuery('');
    setSearchResults(null);
    setSearchError('');
    setFilters({ model_name: '', date_from: '', date_to: '', serial_from: '', serial_to: '' });
    fetchAllReports();
  };

  const handleQuickPeriod = (period) => {
    const now = new Date();
    let from = new Date();
    
    switch (period) {
      case 'last_week': { from = new Date(); from.setDate(from.getDate() - 7); break; }
      case 'today': from = new Date(now.getFullYear(), now.getMonth(), now.getDate()); break;
      case 'week': {
        const day = now.getDay();
        const monday = new Date(now);
        monday.setDate(now.getDate() - (day === 0 ? 6 : day - 1));
        from = monday;
        break;
      }
      case 'month': from = new Date(now.getFullYear(), now.getMonth(), 1); break;
      case 'q1': from = new Date(now); from.setMonth(now.getMonth() - 3); break;
      case 'q2': from = new Date(now); from.setMonth(now.getMonth() - 6); break;
      case 'year': from = new Date(now); from.setFullYear(now.getFullYear() - 1); break;
      default: return;
    }
    const formatDate = (d) => d.toISOString().split('T')[0];
    const newFilters = { ...filters, date_from: formatDate(from), date_to: formatDate(new Date()) };
    setFilters(newFilters);
    setSearchResults(null);
    fetchWithParams(newFilters);
  };

  const fetchWithParams = async (f, pageNumber = 1) => {
    setIsLoading(true);
    try {
      const skip = (pageNumber - 1) * PAGE_SIZE;
      const params = new URLSearchParams({ skip, limit: PAGE_SIZE });
      if (searchQuery) params.set('q', searchQuery);
      if (f.model_name) params.set('model_name', f.model_name);
      if (f.date_from) params.set('date_from', f.date_from);
      if (f.date_to) params.set('date_to', f.date_to);
      if (f.serial_from) params.set('serial_from', f.serial_from);
      if (f.serial_to) params.set('serial_to', f.serial_to);
      const response = await api.get(`/bpan/reports?${params.toString()}`);
      setReports(response.data.items || response.data);
      setTotalCount(response.data.total || 0);
      setPage(pageNumber);
      setSearchResults(null);
    } catch (err) {
      console.error('Failed to fetch', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePrint = async (code_21char) => {
    try {
      await fetch('http://127.0.0.1:9999/spool', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bpan_number: code_21char,
          qr_url: QR_URL,
        }),
      });
    } catch (err) {
      console.error('Print failed:', err);
    }
  };

  const handleDownloadPDF = async (code_21char) => {
    const password = prompt('Enter a password to encrypt the PDF (leave blank for no encryption):');
    if (password === null) return;
    try {
      const params = password ? `?password=${encodeURIComponent(password)}` : '';
      const response = await api.get(`/bpan/${code_21char}/pdf${params}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `BPAN_${code_21char}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to download PDF');
    }
  };

  const openEditModal = async (item) => {
    await fetchModels();
    setEditBPAN(item);
    setEditDate('');
    setEditModelId('');
    setEditError('');
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    setEditError('');
    try {
      const payload = {};
      if (editModelId) payload.model_id = editModelId;
      if (editDate) payload.manufacturing_date = editDate;
      await api.put(`/bpan/${editBPAN.code_21char}`, payload);
      setShowEditModal(false);
      fetchAllReports();
    } catch (err) {
      setEditError(err.response?.data?.detail || 'Failed to update BPAN');
    }
  };

  const displayedResults = searchResults || reports;

  if (isLoading && displayedResults.length === 0) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <button onClick={() => navigate('/dashboard')} className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm mb-2">
        ← Back
      </button>
      <h1 className="text-2xl font-bold">Reports</h1>

      <div className="card space-y-4">
        <form onSubmit={handleSearch} className="flex gap-3">
          <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by BPAN code..." className="input flex-1" />
          <button type="submit" className="btn btn-primary" disabled={isSearching}>
            {isSearching ? 'Searching...' : 'Search'}
          </button>
          <button type="button" onClick={() => setShowFilters(!showFilters)}
            className={`btn ${showFilters ? 'btn-primary' : 'btn-secondary'}`}>Filters</button>
          {(searchResults || searchQuery || Object.values(filters).some(v => v)) && (
            <button type="button" onClick={handleClear} className="btn btn-secondary">Clear</button>
          )}
        </form>
        {searchError && <p className="text-red-500 text-sm">{searchError}</p>}

        {showFilters && (
          <>
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-gray-500 mr-1 mt-1">Quick:</span>
              {[
                { key: 'today', label: 'Today' }, { key: 'last_week', label: 'Last 7 Days' },
                { key: 'week', label: 'This Week' }, { key: 'month', label: 'This Month' },
                { key: 'q1', label: 'Last Q1' }, { key: 'q2', label: 'Last Q2' },
                { key: 'year', label: 'Last Year' },
              ].map(({ key, label }) => (
                <button key={key} type="button" onClick={() => handleQuickPeriod(key)}
                  className="px-3 py-1 text-xs bg-white border rounded hover:bg-blue-50 hover:border-blue-300">{label}</button>
              ))}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-6 gap-3 p-4 bg-gray-50 rounded-lg">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Model Name</label>
                <input type="text" placeholder="e.g. Test" className="input w-full text-sm"
                  value={filters.model_name} onChange={(e) => setFilters({ ...filters, model_name: e.target.value })} />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Date From</label>
                <input type="date" className="input w-full text-sm"
                  value={filters.date_from} onChange={(e) => setFilters({ ...filters, date_from: e.target.value })} />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Date To</label>
                <input type="date" className="input w-full text-sm"
                  value={filters.date_to} onChange={(e) => setFilters({ ...filters, date_to: e.target.value })} />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Serial From</label>
                <input type="number" placeholder="e.g. 1" className="input w-full text-sm"
                  value={filters.serial_from} onChange={(e) => setFilters({ ...filters, serial_from: e.target.value })} />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Serial To</label>
                <input type="number" placeholder="e.g. 100" className="input w-full text-sm"
                  value={filters.serial_to} onChange={(e) => setFilters({ ...filters, serial_to: e.target.value })} />
              </div>
              <div className="flex items-end pb-1">
                <button type="button" onClick={() => fetchWithParams(filters)}
                  className="btn btn-primary w-full text-sm">Apply</button>
              </div>
            </div>
          </>
        )}
      </div>

      {displayedResults.length > 0 ? (
        <div className="card">
          <p className="text-sm text-gray-500 mb-4">Showing {displayedResults.length} BPAN{displayedResults.length !== 1 ? 's' : ''}</p>
          <table className="table">
            <thead>
              <tr>
                <th>BPAN Code</th>
                <th>Model</th>
                <th>Serial</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {displayedResults.map((item) => (
                <tr key={item.code_21char}>
                  <td className="font-mono font-bold text-sm flex items-center gap-1">
                    {item.code_21char}
                    <button
                      onClick={() => copyBPAN(item.code_21char)}
                      className="p-0.5 hover:bg-gray-100 rounded text-blue-500"
                      title="Copy"
                    >
                      {copiedCode === item.code_21char ? '✓' : '📋'}
                    </button>
                  </td>
                  <td>{item.model_name}</td>
                  <td>{String(item.serial_number || '').padStart(4, '0')}</td>
                  <td>{item.created_at ? new Date(item.created_at).toLocaleDateString() : '-'}</td>
                  <td>
                    <div className="flex space-x-2">
                      <button onClick={() => navigate(`/bpan/${item.code_21char}`)}
                        className="btn btn-secondary text-sm py-1">View</button>
                      <button onClick={() => handleDownloadPDF(item.code_21char)}
                        className="btn btn-primary text-sm py-1">PDF</button>
                      <button onClick={() => handlePrint(item.code_21char)}
                        className="btn btn-secondary text-sm py-1">Print</button>
                      {isAdmin && (
                        <button onClick={() => openEditModal(item)}
                          className="btn btn-secondary text-sm py-1">Edit</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex justify-between items-center mt-4">
            <span className="text-sm text-gray-500">
              Showing {displayedResults.length > 0 ? (page - 1) * PAGE_SIZE + 1 : 0} to {Math.min(page * PAGE_SIZE, totalCount)} of {totalCount} results
            </span>
            <div className="flex gap-2">
              <button 
                disabled={page === 1} 
                onClick={() => goToPage(page - 1)}
                className="px-3 py-1 border rounded disabled:opacity-50 hover:bg-gray-50 text-sm"
              >
                Previous
              </button>
              <button 
                disabled={page * PAGE_SIZE >= totalCount} 
                onClick={() => goToPage(page + 1)}
                className="px-3 py-1 border rounded disabled:opacity-50 hover:bg-gray-50 text-sm"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-gray-500 text-center py-8">
          {searchResults ? 'No BPANs found matching your search.' : 'No BPANs generated yet.'}
        </p>
      )}

      {showEditModal && editBPAN && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h3 className="text-lg font-semibold mb-4">Edit BPAN: {editBPAN.code_21char}</h3>
            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Battery Model</label>
                <select className="input w-full" value={editModelId}
                  onChange={(e) => setEditModelId(e.target.value)}>
                  <option value="">-- Keep Current --</option>
                  {models.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name} - {m.capacity_kwh} kWh - {m.chemistry_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Manufacturing Date</label>
                <input type="date" className="input w-full" value={editDate}
                  onChange={(e) => setEditDate(e.target.value)} />
              </div>
              {editError && <p className="text-red-500 text-sm">{editError}</p>}
              <div className="flex space-x-3">
                <button type="submit" className="btn btn-primary flex-1">Save Changes</button>
                <button type="button" onClick={() => setShowEditModal(false)}
                  className="btn btn-secondary flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
