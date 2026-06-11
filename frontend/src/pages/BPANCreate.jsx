import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../hooks/useAuthStore';
import api from '../services/api';
import { QR_URL } from '../utils/constants';
import { checkPrinter as checkPrinterHelper, copyToClipboard } from '../utils/helpers';

export default function BPANCreate() {
  const { user } = useAuthStore();
  const isAdmin = user?.role === 'admin';
  
  const [models, setModels] = useState([]);
  const [selectedModelId, setSelectedModelId] = useState('');
  const [selectedModel, setSelectedModel] = useState(null);
  const [customDate, setCustomDate] = useState('');
  const [lastSerial, setLastSerial] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [pdfError, setPdfError] = useState('');
  const [copied, setCopied] = useState(false);
  const [printerOnline, setPrinterOnline] = useState(false);
  const [showSerialModal, setShowSerialModal] = useState(false);
  const [serialCount, setSerialCount] = useState('');
  const [serialProgress, setSerialProgress] = useState(0);
  const navigate = useNavigate();

  const checkPrinter = async () => {
    const online = await checkPrinterHelper();
    setPrinterOnline(online);
  };

  const copyBPAN = async (text) => {
    await copyToClipboard(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modelsRes, serialRes, dateRes] = await Promise.all([
          api.get('/bpan/models-for-creation'),
          api.get('/bpan/last-serial').catch(() => ({ data: { serial_number: 0 } })),
          api.get('/bpan/default-date').catch(() => ({ data: { date: null } })),
        ]);
        setModels(modelsRes.data);
        setLastSerial(serialRes.data.serial_number);
        if (dateRes.data.date) {
          setCustomDate(dateRes.data.date);
        }
        if (modelsRes.data.length > 0) {
          setSelectedModelId(modelsRes.data[0].id);
          setSelectedModel(modelsRes.data[0]);
        }
      } catch (err) {
        setError('Failed to load models');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
    checkPrinter();
    const interval = setInterval(checkPrinter, 30000);
    return () => clearInterval(interval);
  }, []);
  
  const handleModelChange = (modelId) => {
    setSelectedModelId(modelId);
    const model = models.find(m => m.id === modelId);
    setSelectedModel(model);
  };

  const handleDateChange = (value) => {
    setCustomDate(value);
    if (isAdmin && value) {
      api.post('/bpan/default-date', { date: value }).catch(() => {});
    }
  };
  
  const handleGenerate = async () => {
    setError('');
    setPdfError('');
    if (!selectedModel) {
      setError('Please select a model');
      return;
    }
    
    setIsGenerating(true);
    try {
      const response = await api.post('/bpan/generate', {
        model_id: selectedModel.id,
        factory_code: selectedModel.factory_code,
        custom_date: customDate || null,
      });
      setResult(response.data);
      setLastSerial(response.data.serial_number);

      try {
        const qrUrl = QR_URL;
        const printResponse = await fetch('http://127.0.0.1:9999/spool', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            bpan_number: response.data.code_21char,
            qr_url: qrUrl,
          }),
        });
        if (!printResponse.ok) throw new Error('Print proxy rejected');
      } catch (printErr) {
        console.error('Print trigger failed:', printErr);
        setPdfError('BPAN created, but printer not reachable on this computer.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate BPAN');
    } finally {
      setIsGenerating(false);
    }
};

  const handleSerialPrint = async () => {
    const count = parseInt(serialCount);
    if (!count || count < 1 || count > 100) {
      setPdfError('Enter a number between 1 and 100');
      return;
    }
    if (!selectedModel) {
      setError('Please select a model');
      return;
    }
    setShowSerialModal(false);
    setError('');
    setPdfError('');
    setIsGenerating(true);
    setSerialProgress(0);
    
    for (let i = 0; i < count; i++) {
      try {
        const response = await api.post('/bpan/generate', {
          model_id: selectedModel.id,
          factory_code: selectedModel.factory_code,
          custom_date: customDate || null,
        });
        if (i === count - 1) {
          setResult(response.data);
        }
        setLastSerial(response.data.serial_number);
        setSerialProgress(i + 1);
        
        try {
          await fetch('http://127.0.0.1:9999/spool', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              bpan_number: response.data.code_21char,
              qr_url: QR_URL,
            }),
          });
        } catch (printErr) {
          console.error('Print trigger failed for', response.data.code_21char, printErr);
        }
      } catch (err) {
        setPdfError(`Failed at BPAN ${i + 1}/${count}: ${err.response?.data?.detail || err.message}`);
        break;
      }
    }
    setIsGenerating(false);
  };

  const handleDownloadPDF = async () => {
    if (!result) return;
    setPdfError('');
    const password = prompt('Enter a password to encrypt the PDF (leave blank for no encryption):');
    if (password === null) return;
    try {
      const params = password ? `?password=${encodeURIComponent(password)}` : '';
      const response = await api.get(`/bpan/${result.code_21char}/pdf${params}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `BPAN_${result.code_21char}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setPdfError('Failed to download PDF');
    }
  };
  
  if (isLoading) {
    return <div className="text-center py-8">Loading...</div>;
  }
  
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <button onClick={() => navigate('/dashboard')} className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm mb-2">
        ← Back
      </button>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Create New BPAN</h1>
        <div className="flex items-center gap-3">
          <div className={`px-4 py-2 rounded text-sm font-medium border flex items-center gap-2 ${
            printerOnline ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-700 border-red-200'
          }`}>
            <span className={`w-2 h-2 rounded-full ${printerOnline ? 'bg-green-500' : 'bg-red-500'}`}></span>
            {printerOnline ? 'Printer Online' : 'Printer Offline'}
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-4 py-2 text-center">
          <p className="text-xs text-blue-500 uppercase tracking-wide">Next Serial Number</p>
          <p className="text-2xl font-bold font-mono text-blue-700">{String(lastSerial + 1).padStart(4, '0')}</p>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}
      {pdfError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">{pdfError}</div>
      )}
      
      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Battery Model</label>
          <select
            className="input w-full"
            value={selectedModelId}
            onChange={(e) => handleModelChange(e.target.value)}
          >
            <option value="">-- Select Model --</option>
            {models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} - {m.capacity_kwh} kWh - {m.chemistry_name} - {m.voltage_v}V
              </option>
            ))}
          </select>
        </div>
        
        {isAdmin && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Manufacturing Date (optional - defaults to today)
            </label>
            <input
              type="date"
              className="input w-full"
value={customDate}
                  onChange={(e) => handleDateChange(e.target.value)}
            />
          </div>
        )}
        
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !selectedModel}
          className="btn btn-primary w-full"
        >
          {isGenerating ? 'Generating...' : 'Generate BPAN'}
        </button>
        <button
          onClick={() => setShowSerialModal(true)}
          disabled={isGenerating || !selectedModel}
          className="btn btn-secondary w-full"
        >
          {isGenerating ? `Printing ${serialProgress}...` : 'Serial Print'}
        </button>
      </div>
      
      {!isAdmin && (
        <div className="card bg-blue-50 border border-blue-200">
          <p className="text-sm">
            <span className="text-gray-500">Manufacturing Date:</span>{' '}
            {customDate ? (
              <span className="font-semibold text-blue-700">{customDate}</span>
            ) : (
              <span className="font-medium">Today (server date)</span>
            )}
          </p>
        </div>
      )}
      
      {result && (
        <div className="card border-2 border-green-300 bg-green-50">
          <h2 className="text-lg font-semibold mb-4 text-green-700">BPAN Generated Successfully!</h2>
          <div className="bg-white text-3xl font-bold tracking-widest p-4 rounded-lg mb-4 border flex items-center justify-center gap-3">
            {result.code_21char}
            <button
              onClick={() => copyBPAN(result.code_21char)}
              className="text-2xl hover:scale-110 transition-transform"
              title="Copy BPAN code"
            >
              {copied ? '✓' : '📋'}
            </button>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-gray-500 text-sm">Manufacturing Date</p>
              <p className="font-medium">{result.manufacturing_date}</p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">Serial Number</p>
              <p className="font-medium">{String(result.serial_number).padStart(4, '0')}</p>
            </div>
          </div>
          <div className="flex space-x-3">
            <button onClick={() => navigate(`/bpan/${result.code_21char}`)} className="btn btn-primary">
              View Details
            </button>
            <button onClick={handleDownloadPDF} className="btn btn-secondary">
              Download PDF
            </button>
            <button onClick={handleGenerate} className="btn btn-primary">
              Create Another
            </button>
          </div>
        </div>
      )}
      
      {selectedModel && (
        <div className="card">
          <h2 className="font-semibold mb-4">Model Summary</h2>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div><span className="text-gray-500">Name:</span> {selectedModel.name}</div>
            <div><span className="text-gray-500">Country:</span> {selectedModel.country_name}</div>
            <div><span className="text-gray-500">Manufacturer:</span> {selectedModel.manufacturer_name}</div>
            <div><span className="text-gray-500">Capacity:</span> {selectedModel.capacity_kwh} kWh</div>
            <div><span className="text-gray-500">Chemistry:</span> {selectedModel.chemistry_name}</div>
            <div><span className="text-gray-500">Voltage:</span> {selectedModel.voltage_v} V</div>
            <div><span className="text-gray-500">Factory:</span> {selectedModel.factory_code}</div>
            {customDate && (
              <div><span className="text-gray-500">Custom Date:</span> {customDate}</div>
            )}
          </div>
        </div>
      )}
      
      {showSerialModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-80">
            <h3 className="text-lg font-semibold mb-4">Serial Print</h3>
            <p className="text-sm text-gray-600 mb-4">
              Generate and print multiple BPANs serially with the same model and date.
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1">Number of products to print</label>
              <input type="number" className="input w-full" value={serialCount}
                onChange={(e) => setSerialCount(e.target.value)} placeholder="e.g. 20" min="1" max="100" autoFocus />
            </div>
            <div className="flex space-x-3">
              <button onClick={handleSerialPrint} className="btn btn-primary flex-1">Print Serially</button>
              <button onClick={() => setShowSerialModal(false)} className="btn btn-secondary flex-1">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
