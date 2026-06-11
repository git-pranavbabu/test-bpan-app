import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { TABLE_NAME_FIELD_MAP } from '../utils/constants';

const TABLES_WITH_OPTIONAL_CODE = ['power_20_soc'];

const SPECIAL_TABLES = ['dimensions'];

function getDisplayName(entry, tableName) {
  if (tableName === 'dimensions') {
    return `${entry.length_mm}×${entry.width_mm}×${entry.height_mm}`;
  }
  const field = TABLE_NAME_FIELD_MAP[tableName] || 'name';
  const value = entry[field];
  if (field === 'value_kwh' || field === 'value_v' || field === 'value_kw' || field === 'value_mohm' || field === 'value_kg' || field === 'value_kgco2ekwh' || field === 'years' || field === 'count') return value;
  if (typeof value === 'number') return value;
  return value || '-';
}

export default function AdminLookup() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [entries, setEntries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [newEntry, setNewEntry] = useState({ code: '', name: '', description: '' });
  const [dimensionsInput, setDimensionsInput] = useState({ length_mm: '', width_mm: '', height_mm: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      fetchEntries(selectedTable);
    }
  }, [selectedTable]);

  const fetchTables = async () => {
    try {
      const response = await api.get('/lookup/tables');
      setTables(response.data);
    } catch (err) {
      console.error('Failed to fetch tables', err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchEntries = async (tableName) => {
    try {
      const response = await api.get(`/lookup/${tableName}`);
      setEntries(response.data);
    } catch (err) {
      console.error('Failed to fetch entries', err);
      setEntries([]);
    }
  };

  const handleAddEntry = async (e) => {
    e.preventDefault();
    
    if (selectedTable === 'dimensions') {
      const l = dimensionsInput.length_mm;
      const w = dimensionsInput.width_mm;
      const h = dimensionsInput.height_mm;
      if (!l || !w || !h) {
        setError('All dimensions are required');
        return;
      }
      try {
        const code = `D${l}x${w}x${h}`;
        await api.post('/lookup/dimensions', {
          code,
          length_mm: parseInt(l),
          width_mm: parseInt(w),
          height_mm: parseInt(h),
        });
        setSuccess('Entry added successfully!');
        setDimensionsInput({ length_mm: '', width_mm: '', height_mm: '' });
        setError('');
        fetchEntries(selectedTable);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to add entry');
      }
      return;
    }
    
    const requiresCode = !TABLES_WITH_OPTIONAL_CODE.includes(selectedTable);
    
    if (requiresCode && !newEntry.code) {
      setError('Code is required');
      return;
    }
    
    if (!newEntry.name) {
      setError('Name is required');
      return;
    }
    
    try {
      const payload = { name: newEntry.name };
      if (newEntry.code) payload.code = newEntry.code;
      if (newEntry.description) payload.description = newEntry.description;
      await api.post(`/lookup/${selectedTable}`, payload);
      setSuccess('Entry added successfully!');
      setNewEntry({ code: '', name: '', description: '' });
      setError('');
      fetchEntries(selectedTable);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add entry');
    }
  };

  const handleUpdateEntry = async (entry) => {
    const nameField = TABLE_NAME_FIELD_MAP[selectedTable] || 'name';
    const identifier = selectedTable === 'power_20_soc' ? entry.id : entry.code;
    const payload = { name: entry.name ?? entry[nameField] };
    if (entry.description !== undefined) payload.description = entry.description;
    try {
      await api.put(`/lookup/${selectedTable}/${identifier}`, payload);
      setSuccess('Entry updated successfully!');
      setEditMode(false);
      setEditingEntry(null);
      fetchEntries(selectedTable);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update entry');
    }
  };

  const handleEditClick = (entry) => {
    if (SPECIAL_TABLES.includes(selectedTable)) return;
    const nameField = TABLE_NAME_FIELD_MAP[selectedTable] || 'name';
    setEditingEntry({ ...entry, name: entry[nameField] || entry.name });
  };

  const handleDeleteEntry = async (entry) => {
    const identifier = selectedTable === 'power_20_soc' ? entry.id : (entry.code || entry.id);
    if (!confirm(`Are you sure you want to delete entry '${identifier}'?`)) return;
    try {
      await api.delete(`/lookup/${selectedTable}/${identifier}`);
      setSuccess('Entry deleted successfully!');
      fetchEntries(selectedTable);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete entry');
    }
  };


  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <button onClick={() => navigate('/admin')} className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm mb-2">
        ← Back
      </button>
      <h1 className="text-2xl font-bold">Lookup Tables</h1>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>}
      {success && <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">{success}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Tables</h2>
          <div className="space-y-2">
            {tables.map((table) => (
              <button
                key={table.name}
                onClick={() => { setSelectedTable(table.name); setEditMode(false); setError(''); setSuccess(''); }}
                className={`w-full text-left px-3 py-2 rounded ${
                  selectedTable === table.name
                    ? 'bg-blue-100 text-blue-700'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="font-medium capitalize">{table.name.replace(/_/g, ' ')}</div>
                <div className="text-xs text-gray-500">{table.description}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-3 card">
          {selectedTable ? (
            <>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold capitalize">
                  {selectedTable.replace(/_/g, ' ')} Entries ({entries.length})
                </h2>
                <div className="flex gap-2">

                  <button
                    onClick={() => { setEditMode(!editMode); setError(''); setSuccess(''); }}
                    className="btn btn-secondary text-sm"
                  >
                    {editMode ? 'Cancel Edit' : 'Enable Edit'}
                  </button>
                </div>
              </div>

              {editMode && (
                <form onSubmit={handleAddEntry} className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium mb-2">Add New Entry</h3>
                  {selectedTable === 'dimensions' ? (
                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Length (mm)</label>
                        <input type="number" className="input" value={dimensionsInput.length_mm}
                          onChange={(e) => setDimensionsInput({ ...dimensionsInput, length_mm: e.target.value })} />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Width (mm)</label>
                        <input type="number" className="input" value={dimensionsInput.width_mm}
                          onChange={(e) => setDimensionsInput({ ...dimensionsInput, width_mm: e.target.value })} />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Height (mm)</label>
                        <input type="number" className="input" value={dimensionsInput.height_mm}
                          onChange={(e) => setDimensionsInput({ ...dimensionsInput, height_mm: e.target.value })} />
                      </div>
                    </div>
                  ) : (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <input
                        type="text"
                        placeholder={TABLES_WITH_OPTIONAL_CODE.includes(selectedTable) ? "Code (optional)" : "Code"}
                        className="input"
                        value={newEntry.code}
                        onChange={(e) => setNewEntry({ ...newEntry, code: e.target.value.toUpperCase() })}
                      />
                      {TABLES_WITH_OPTIONAL_CODE.includes(selectedTable) && (
                        <span className="text-xs text-gray-500">Optional</span>
                      )}
                    </div>
                    <input
                      type="text"
                      placeholder="Name"
                      className="input"
                      value={newEntry.name}
                      onChange={(e) => setNewEntry({ ...newEntry, name: e.target.value })}
                    />
                  </div>
                  )}
                  <button type="submit" className="btn btn-primary mt-2">Add Entry</button>
                </form>
              )}

              <table className="table">
<thead>
                   <tr>
                     <th>Code</th>
                     <th>Name</th>
                     {editMode && <th>Actions</th>}
                   </tr>
                 </thead>
                <tbody>
                  {entries.map((entry) => {
                    const isSpecial = SPECIAL_TABLES.includes(selectedTable);
                    const entryKey = selectedTable === 'power_20_soc' ? entry.id : (entry.code || entry.value_kw);
                    const nameField = TABLE_NAME_FIELD_MAP[selectedTable] || 'name';
                    const editId = selectedTable === 'power_20_soc' ? 'id' : 'code';
                    const isEditing = !isSpecial && editingEntry && editingEntry[editId] !== undefined && editingEntry[editId] === entry[editId];
                    return (
                    <tr key={entryKey}>
                      <td className="font-mono font-bold">{entry.code || '-'}</td>
                      <td>
                        {isEditing ? (
                          <input
                            type="text"
                            className="input w-full"
                            value={editingEntry.name || ''}
                            onChange={(e) => setEditingEntry({ ...editingEntry, name: e.target.value })}
                          />
                        ) : (
                          getDisplayName(entry, selectedTable)
                        )}
                      </td>
                      {editMode && (
                        <td>
                          {isEditing ? (
                            <div className="flex space-x-2">
                              <button
                                onClick={() => handleUpdateEntry(editingEntry)}
                                className="btn btn-primary text-sm py-1"
                              >
                                Save
                              </button>
                              <button
                                onClick={() => setEditingEntry(null)}
                                className="btn btn-secondary text-sm py-1"
                              >
                                Cancel
                              </button>
                            </div>
                          ) : (
                            <div className="flex space-x-2">
                              {!isSpecial && (
                                <button
                                  onClick={() => handleEditClick(entry)}
                                  className="btn btn-secondary text-sm py-1"
                                >
                                  Edit
                                </button>
                              )}
                              <button
                                onClick={() => handleDeleteEntry(entry)}
                                className="btn btn-danger text-sm py-1"
                              >
                                Delete
                              </button>
                            </div>
                          )}
                        </td>
                      )}
                    </tr>
                  );
                })}
                </tbody>
              </table>
              {entries.length === 0 && (
                <p className="text-gray-500 text-center py-4">No entries found.</p>
              )}
            </>
          ) : (
            <p className="text-gray-500 text-center py-8">Select a table to view entries.</p>
          )}
        </div>
      </div>
    </div>
  );
}