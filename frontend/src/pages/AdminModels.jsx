import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { TABLE_NAME_FIELD_MAP } from '../utils/constants';

function getDisplayValue(entry, tableName) {
  const field = TABLE_NAME_FIELD_MAP[tableName];
  if (!field || !entry) return '-';
  
  if (tableName === 'dimensions') {
    return `${entry.length_mm}×${entry.width_mm}×${entry.height_mm}`;
  }
  
  const value = entry[field];
  if (field === 'value_kwh' || field === 'value_v' || field === 'value_mohm' || 
      field === 'value_kg' || field === 'value_kw' || field === 'value_kgco2ekwh') {
    return value;
  }
  if (typeof value === 'number') return value;
  return value || '-';
}

function getOptionLabel(option, tableName) {
  if (tableName === 'power_20_soc') {
    return `${option.value_kw} kW${option.code ? ` (${option.code})` : ''}`;
  }
  const code = option.code;
  const value = getDisplayValue(option, tableName);
  return `${code} - ${value}`;
}

export default function AdminModels() {
  const [models, setModels] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('list');
  const [editModelId, setEditModelId] = useState(null);
  const navigate = useNavigate();
  
  const [lookups, setLookups] = useState({
    countries: [],
    manufacturers: [],
    battery_capacities: [],
    battery_chemistries: [],
    nominal_voltages: [],
    cell_origins: [],
    extinguisher_classes: [],
    factory_codes: [],
    tac_numbers: [],
    cell_types: [],
    pack_construction_types: [],
    module_construction_types: [],
    cooling_systems: [],
    internal_resistances: [],
    battery_weights: [],
    battery_warranties: [],
    power_80_soc: [],
    power_20_soc: [],
    carbon_footprints: [],
    number_of_cells: [],
    dimensions: [],
  });
  
  const [formData, setFormData] = useState({
    name: '',
    country_code: '',
    manufacturer_code: '',
    capacity_code: '',
    chemistry_code: '',
    voltage_code: '',
    cell_origin_code: '',
    extinguisher_code: '',
    factory_code: '9',
    tac_code: '',
    internal_resistance_code: '',
    warranty_code: '',
    cell_type_code: '',
    pack_construction_code: '',
    module_construction_code: '',
    cooling_code: '',
    num_cells_code: '',
    weight_code: '',
    dimensions_code: '',
    power_80_soc_code: '',
    power_20_soc_value: '',
    carbon_footprint_code: '',
  });
  
  const [dimensionsInput, setDimensionsInput] = useState({ length_mm: '', width_mm: '', height_mm: '' });
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [showQuickAdd, setShowQuickAdd] = useState(false);
  const [quickAddField, setQuickAddField] = useState('');
  const [quickAddData, setQuickAddData] = useState({ code: '', name: '', description: '' });

  useEffect(() => {
    fetchModels();
    fetchLookups();
  }, []);

  const fetchModels = async () => {
    setError('');
    try {
      const response = await api.get('/models/');
      setModels(response.data);
    } catch (err) {
      console.error('Failed to fetch models', err);
      setError(err.response?.status === 403 
        ? 'Admin access required. Please re-login.' 
        : err.response?.data?.detail || 'Failed to load models');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLookups = async () => {
    try {
      const [countries, manufacturers, capacities, chemistries, voltages, cellOrigins, extinguishers, factories, tacs, cellTypes, packConstructions, moduleConstructions, cooling, internalResistances, weights, warranties, power80, power20, carbon, numCells, dimensions] = await Promise.all([
        api.get('/lookup/countries'),
        api.get('/lookup/manufacturers'),
        api.get('/lookup/battery_capacities'),
        api.get('/lookup/battery_chemistries'),
        api.get('/lookup/nominal_voltages'),
        api.get('/lookup/cell_origins'),
        api.get('/lookup/extinguisher_classes'),
        api.get('/lookup/factory_codes'),
        api.get('/lookup/tac_numbers'),
        api.get('/lookup/cell_types'),
        api.get('/lookup/pack_construction_types'),
        api.get('/lookup/module_construction_types'),
        api.get('/lookup/cooling_systems'),
        api.get('/lookup/internal_resistances'),
        api.get('/lookup/battery_weights'),
        api.get('/lookup/battery_warranties'),
        api.get('/lookup/power_80_soc'),
        api.get('/lookup/power_20_soc'),
        api.get('/lookup/carbon_footprints'),
        api.get('/lookup/number_of_cells'),
        api.get('/lookup/dimensions'),
      ]);
      setLookups({
        countries: countries.data,
        manufacturers: manufacturers.data,
        battery_capacities: capacities.data,
        battery_chemistries: chemistries.data,
        nominal_voltages: voltages.data,
        cell_origins: cellOrigins.data,
        extinguisher_classes: extinguishers.data,
        factory_codes: factories.data,
        tac_numbers: tacs.data,
        cell_types: cellTypes.data,
        pack_construction_types: packConstructions.data,
        module_construction_types: moduleConstructions.data,
        cooling_systems: cooling.data,
        internal_resistances: internalResistances.data,
        battery_weights: weights.data,
        battery_warranties: warranties.data,
        power_80_soc: power80.data,
        power_20_soc: power20.data,
        carbon_footprints: carbon.data,
        number_of_cells: numCells.data,
        dimensions: dimensions.data,
      });
    } catch (err) {
      console.error('Failed to fetch lookups', err);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to deactivate this model?')) return;
    try {
      await api.delete(`/models/${id}`);
      fetchModels();
    } catch (err) {
      alert('Failed to deactivate model');
    }
  };

  const handleActivate = async (id) => {
    if (!confirm('Are you sure you want to reactivate this model?')) return;
    try {
      await api.patch(`/models/${id}/activate`);
      fetchModels();
    } catch (err) {
      alert('Failed to activate model');
    }
  };

  const handleEdit = (model) => {
    setFormData({
      name: model.name || '',
      country_code: model.country_code || '',
      manufacturer_code: model.manufacturer_code || '',
      capacity_code: model.capacity_code || '',
      chemistry_code: model.chemistry_code || '',
      voltage_code: model.voltage_code || '',
      cell_origin_code: model.cell_origin_code || '',
      extinguisher_code: model.extinguisher_code || '',
      factory_code: model.factory_code || '',
      tac_code: model.tac_code || '',
      internal_resistance_code: model.internal_resistance_code || '',
      warranty_code: model.warranty_code || '',
      cell_type_code: model.cell_type_code || '',
      pack_construction_code: model.pack_construction_code || '',
      module_construction_code: model.module_construction_code || '',
      cooling_code: model.cooling_code || '',
      num_cells_code: model.num_cells_code || '',
      weight_code: model.weight_code || '',
      dimensions_code: model.dimensions_code || '',
      power_80_soc_code: model.power_80_soc_code || '',
      power_20_soc_value: model.power_20_soc_value || '',
      carbon_footprint_code: model.carbon_footprint_code || '',
    });
    setEditModelId(model.id);
    setActiveTab('create');
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const openQuickAdd = (field) => {
    setQuickAddField(field);
    setQuickAddData({ code: '', name: '', description: '' });
    if (field === 'dimensions') {
      setDimensionsInput({ length_mm: '', width_mm: '', height_mm: '' });
    }
    setShowQuickAdd(true);
  };

  const handleQuickAdd = async (e) => {
    e.preventDefault();
    try {
      if (quickAddField === 'dimensions') {
        const code = `D${dimensionsInput.length_mm}x${dimensionsInput.width_mm}x${dimensionsInput.height_mm}`;
        await api.post('/lookup/dimensions', {
          code: code,
          length_mm: parseInt(dimensionsInput.length_mm) || 0,
          width_mm: parseInt(dimensionsInput.width_mm) || 0,
          height_mm: parseInt(dimensionsInput.height_mm) || 0,
        });
      } else {
        await api.post(`/lookup/${quickAddField}`, quickAddData);
      }
      setShowQuickAdd(false);
      fetchLookups();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add entry');
    }
  };

  const handleDimensionsChange = (field, value) => {
    const newDims = { ...dimensionsInput, [field]: value };
    setDimensionsInput(newDims);
    
    const l = newDims.length_mm;
    const w = newDims.width_mm;
    const h = newDims.height_mm;
    
    if (l && w && h) {
      const existing = lookups.dimensions.find(d => d.length_mm == l && d.width_mm == w && d.height_mm == h);
      if (existing) {
        handleInputChange('dimensions_code', existing.code);
      } else {
        const code = `D${l}x${w}x${h}`;
        setQuickAddData({ code: code, name: `${l}×${w}×${h}`, description: '' });
        handleInputChange('dimensions_code', code);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    if (!formData.name) {
      setError('Please enter model name');
      return;
    }
    
    const requiredFields = [
      'country_code', 'manufacturer_code', 'capacity_code', 'chemistry_code',
      'voltage_code', 'cell_origin_code', 'extinguisher_code', 'factory_code', 'tac_code',
      'internal_resistance_code', 'warranty_code', 'cell_type_code', 'pack_construction_code',
      'module_construction_code', 'cooling_code', 'num_cells_code', 'weight_code',
      'dimensions_code', 'power_80_soc_code', 'power_20_soc_value', 'carbon_footprint_code'
    ];
    
    for (const field of requiredFields) {
      if (!formData[field]) {
        setError('Please fill in all required fields');
        return;
      }
    }
    
    try {
      const payload = { ...formData };
      if (editModelId) {
        await api.put(`/models/${editModelId}`, payload);
        setSuccess('Model updated successfully!');
        setEditModelId(null);
      } else {
        await api.post('/models/', payload);
        setSuccess('Model created successfully!');
      }
      setFormData({
        name: '',
        country_code: '',
        manufacturer_code: '',
        capacity_code: '',
        chemistry_code: '',
        voltage_code: '',
        cell_origin_code: '',
        extinguisher_code: '',
        factory_code: '9',
        tac_code: '',
        internal_resistance_code: '',
        warranty_code: '',
        cell_type_code: '',
        pack_construction_code: '',
        module_construction_code: '',
        cooling_code: '',
        num_cells_code: '',
        weight_code: '',
        dimensions_code: '',
        power_80_soc_code: '',
        power_20_soc_value: '',
        carbon_footprint_code: '',
      });
      setDimensionsInput({ length_mm: '', width_mm: '', height_mm: '' });
      setActiveTab('list');
      setEditModelId(null);
      fetchModels();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create model');
    }
  };

  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>;
  }

  const inputClass = "input w-full";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  const SelectWithAdd = ({ label, field, value, onChange, options, placeholder, optional }) => (
    <div className="relative">
      <label className={labelClass}>{label}{optional ? '' : ' *'}</label>
      <div className="flex gap-2">
        <select className={inputClass} value={value} onChange={(e) => onChange(e.target.value)}>
          <option value="">{placeholder}</option>
          {options.map(o => <option key={o.code} value={o.code}>{getOptionLabel(o, field)}</option>)}
        </select>
        <button type="button" onClick={() => openQuickAdd(field)} className="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-lg font-bold">+</button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <button onClick={() => { setActiveTab('list'); navigate('/dashboard'); }} className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm mb-2">
        ← Back
      </button>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Battery Models</h1>
        <button onClick={() => setActiveTab('create')} className="btn btn-primary">
          Create New Model
        </button>
      </div>

      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>}
      {success && <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">{success}</div>}

      {showQuickAdd && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h3 className="text-lg font-semibold mb-4">Add {quickAddField.replace(/_/g, ' ')}</h3>
            <form onSubmit={handleQuickAdd} className="space-y-4">
              {quickAddField === 'dimensions' ? (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">Length (mm) *</label>
                    <input type="number" className="input w-full" value={dimensionsInput.length_mm} onChange={(e) => setDimensionsInput({...dimensionsInput, length_mm: e.target.value})} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Width (mm) *</label>
                    <input type="number" className="input w-full" value={dimensionsInput.width_mm} onChange={(e) => setDimensionsInput({...dimensionsInput, width_mm: e.target.value})} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Height (mm) *</label>
                    <input type="number" className="input w-full" value={dimensionsInput.height_mm} onChange={(e) => setDimensionsInput({...dimensionsInput, height_mm: e.target.value})} required />
                  </div>
                </>
              ) : quickAddField === 'power_20_soc' ? (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">Power Value (kW) *</label>
                    <input type="number" step="0.01" className="input w-full" value={quickAddData.name} onChange={(e) => setQuickAddData({...quickAddData, name: e.target.value})} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Code (optional)</label>
                    <input type="text" className="input w-full" value={quickAddData.code} onChange={(e) => setQuickAddData({...quickAddData, code: e.target.value.toUpperCase()})} />
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-1">Code *</label>
                    <input type="text" className="input w-full" value={quickAddData.code} onChange={(e) => setQuickAddData({...quickAddData, code: e.target.value.toUpperCase()})} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Name *</label>
                    <input type="text" className="input w-full" value={quickAddData.name} onChange={(e) => setQuickAddData({...quickAddData, name: e.target.value})} required />
                  </div>
                </>
              )}
              <div className="flex space-x-3">
                <button type="submit" className="btn btn-primary flex-1">Add</button>
                <button type="button" onClick={() => setShowQuickAdd(false)} className="btn btn-secondary flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {activeTab === 'list' && (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Country</th>
                <th>Manufacturer</th>
                <th>Capacity (kWh)</th>
                <th>Chemistry</th>
                <th>Voltage (V)</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {models.map((model) => (
                <tr key={model.id}>
                  <td className="font-medium">{model.name}</td>
                  <td>{model.country?.name} ({model.country_code})</td>
                  <td>{model.manufacturer?.name}</td>
                  <td>{model.capacity?.value_kwh}</td>
                  <td>{model.chemistry?.name}</td>
                  <td>{model.voltage?.value_v}</td>
                  <td>
                    <span className={`px-2 py-1 rounded text-xs ${
                      model.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {model.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(model)}
                        className="btn btn-secondary text-sm py-1"
                      >
                        Edit
                      </button>
                      {model.is_active ? (
                        <button
                          onClick={() => handleDelete(model.id)}
                          className="btn btn-danger text-sm py-1"
                        >
                          Deactivate
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivate(model.id)}
                          className="btn btn-primary text-sm py-1"
                        >
                          Activate
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {models.length === 0 && (
            <p className="text-gray-500 text-center py-4">No models found.</p>
          )}
        </div>
      )}

      {activeTab === 'create' && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">{editModelId ? 'Edit Battery Model' : 'Create New Battery Model'}</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SelectWithAdd label="1. Country Code *" field="countries" value={formData.country_code} onChange={(v) => handleInputChange('country_code', v)} options={lookups.countries} placeholder="Select Country" required />
              
              <SelectWithAdd label="2. Manufacturer Identifier *" field="manufacturers" value={formData.manufacturer_code} onChange={(v) => handleInputChange('manufacturer_code', v)} options={lookups.manufacturers} placeholder="Select Manufacturer" required />
              
              <SelectWithAdd label="3. Battery Capacity (KW) *" field="battery_capacities" value={formData.capacity_code} onChange={(v) => handleInputChange('capacity_code', v)} options={lookups.battery_capacities} placeholder="Select Capacity" required />
              
              <SelectWithAdd label="4. Battery Chemistry *" field="battery_chemistries" value={formData.chemistry_code} onChange={(v) => handleInputChange('chemistry_code', v)} options={lookups.battery_chemistries} placeholder="Select Chemistry" required />
              
              <SelectWithAdd label="5. Nominal Voltage *" field="nominal_voltages" value={formData.voltage_code} onChange={(v) => handleInputChange('voltage_code', v)} options={lookups.nominal_voltages} placeholder="Select Voltage" required />
              
              <SelectWithAdd label="6. Cell Origin *" field="cell_origins" value={formData.cell_origin_code} onChange={(v) => handleInputChange('cell_origin_code', v)} options={lookups.cell_origins} placeholder="Select Cell Origin" required />
              
              <SelectWithAdd label="7. Fire Extinguisher Class *" field="extinguisher_classes" value={formData.extinguisher_code} onChange={(v) => handleInputChange('extinguisher_code', v)} options={lookups.extinguisher_classes} placeholder="Select Class" required />
              
              <SelectWithAdd label="8. TAC Number *" field="tac_numbers" value={formData.tac_code} onChange={(v) => handleInputChange('tac_code', v)} options={lookups.tac_numbers} placeholder="Select TAC" required />
              
              <SelectWithAdd label="9. Number of Cells per Battery *" field="number_of_cells" value={formData.num_cells_code} onChange={(v) => handleInputChange('num_cells_code', v)} options={lookups.number_of_cells} placeholder="Select Cells" required />
              
              <SelectWithAdd label="10. Internal Resistance of Battery(m ohm) *" field="internal_resistances" value={formData.internal_resistance_code} onChange={(v) => handleInputChange('internal_resistance_code', v)} options={lookups.internal_resistances} placeholder="Select Resistance" required />
              
              <SelectWithAdd label="11. Battery Weight(Kg) *" field="battery_weights" value={formData.weight_code} onChange={(v) => handleInputChange('weight_code', v)} options={lookups.battery_weights} placeholder="Select Weight" required />
              
              <SelectWithAdd label="12. Battery Warranty(Years) *" field="battery_warranties" value={formData.warranty_code} onChange={(v) => handleInputChange('warranty_code', v)} options={lookups.battery_warranties} placeholder="Select Warranty" required />
              
              <SelectWithAdd label="13. Cell Type *" field="cell_types" value={formData.cell_type_code} onChange={(v) => handleInputChange('cell_type_code', v)} options={lookups.cell_types} placeholder="Select Cell Type" required />
              
              <SelectWithAdd label="14. Length*Width*Height(mm) *" field="dimensions" value={formData.dimensions_code} onChange={(v) => handleInputChange('dimensions_code', v)} options={lookups.dimensions} placeholder="Select Dimensions" required />
              
              <SelectWithAdd label="15. Type of Construction of Battery Pack *" field="pack_construction_types" value={formData.pack_construction_code} onChange={(v) => handleInputChange('pack_construction_code', v)} options={lookups.pack_construction_types} placeholder="Select Pack Construction" required />
              
              <SelectWithAdd label="16. Type of Construction of Module *" field="module_construction_types" value={formData.module_construction_code} onChange={(v) => handleInputChange('module_construction_code', v)} options={lookups.module_construction_types} placeholder="Select Module Construction" required />
              
              <SelectWithAdd label="17. Type of Cooling System *" field="cooling_systems" value={formData.cooling_code} onChange={(v) => handleInputChange('cooling_code', v)} options={lookups.cooling_systems} placeholder="Select Cooling" required />
              
              <SelectWithAdd label="18. Original Power Capability at 80% SoC *" field="power_80_soc" value={formData.power_80_soc_code} onChange={(v) => handleInputChange('power_80_soc_code', v)} options={lookups.power_80_soc} placeholder="Select Power 80%" required />
              
              <div>
                <label className={labelClass}>19. Original Power Capability at 20% SoC (kW) *</label>
                <div className="flex gap-2">
                  <select className={inputClass} value={formData.power_20_soc_value} onChange={(e) => handleInputChange('power_20_soc_value', e.target.value)}>
                    <option value="">Select Power 20%</option>
                    {lookups.power_20_soc.map(o => <option key={String(o.value_kw)} value={String(o.value_kw)}>{o.value_kw} kW{o.code ? ` (${o.code})` : ''}</option>)}
                  </select>
                  <button type="button" onClick={() => openQuickAdd('power_20_soc')} className="px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-lg font-bold">+</button>
                </div>
              </div>
              
              <SelectWithAdd label="20. Total Battery Carbon Footprint Scaled(kgCO2e/kWh) *" field="carbon_footprints" value={formData.carbon_footprint_code} onChange={(v) => handleInputChange('carbon_footprint_code', v)} options={lookups.carbon_footprints} placeholder="Select Carbon" required />
            </div>
            
            <div className="pt-4 border-t">
              <label className={labelClass}>Model Name *</label>
              <input type="text" className={inputClass} value={formData.name} onChange={(e) => handleInputChange('name', e.target.value)} placeholder="e.g., HYK-100Ah-48V" required />
            </div>
            
            <div className="flex space-x-4">
              <button type="submit" className="btn btn-primary">{editModelId ? 'Update Model' : 'Create Model'}</button>
              <button type="button" onClick={() => { setActiveTab('list'); setEditModelId(null); setFormData({
                name: '', country_code: '', manufacturer_code: '', capacity_code: '',
                chemistry_code: '', voltage_code: '', cell_origin_code: '', extinguisher_code: '',
                factory_code: '9', tac_code: '', internal_resistance_code: '', warranty_code: '',
                cell_type_code: '', pack_construction_code: '', module_construction_code: '',
                cooling_code: '', num_cells_code: '', weight_code: '', dimensions_code: '',
                power_80_soc_code: '', power_20_soc_value: '', carbon_footprint_code: '',
              }); }} className="btn btn-secondary">Cancel</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}