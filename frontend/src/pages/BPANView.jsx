import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function BPANView() {
  const { code } = useParams();
  const [bpanData, setBpanData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [pdfError, setPdfError] = useState('');
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchBPAN = async () => {
      try {
        const response = await api.get(`/bpan/${code}`);
        setBpanData(response.data);
      } catch (err) {
        setError('Failed to load BPAN data');
      } finally {
        setIsLoading(false);
      }
    };
    fetchBPAN();
  }, [code]);
  
  const handleDownloadPDF = async () => {
    setPdfError('');
    const password = prompt('Enter a password to encrypt the PDF (leave blank for no encryption):');
    if (password === null) return;
    try {
      const params = password ? `?password=${encodeURIComponent(password)}` : '';
      const response = await api.get(`/bpan/${code}/pdf${params}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `BPAN_${code}.pdf`);
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
  
  if (error || !bpanData) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">{error || 'BPAN not found'}</p>
        <button onClick={() => navigate('/bpan/create')} className="btn btn-primary">Create BPAN</button>
      </div>
    );
  }
  
  const model = bpanData.model || {};
  
  const ParamRow = ({ label, code, value }) => (
    <div className="bg-white border rounded-lg px-4 py-3">
      <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
      <div className="flex items-baseline gap-2 mt-1">
        {code && <span className="font-mono text-sm font-bold text-blue-600">{code}</span>}
        <span className="font-medium text-gray-800">{value || '-'}</span>
      </div>
    </div>
  );

  const SectionCard = ({ title, children }) => (
    <div className="card border-t-4 border-t-blue-500">
      <h2 className="font-semibold text-lg mb-4 text-blue-800">{title}</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {children}
      </div>
    </div>
  );
  
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <button onClick={() => navigate('/bpan/reports')} className="flex items-center gap-1 text-gray-500 hover:text-gray-700 text-sm mb-2">
        ← Back
      </button>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">BPAN Details</h1>
        <div className="flex space-x-3">
          <button onClick={handleDownloadPDF} className="btn btn-primary">Download PDF</button>
          <button onClick={() => navigate('/bpan/reports')} className="btn btn-secondary">Reports</button>
        </div>
      </div>
      
      <div className="bg-blue-50 text-3xl font-bold tracking-widest text-center p-6 rounded-lg border-2 border-blue-200">
        {code}
      </div>

      <SectionCard title="Battery Manufacturer Identifier (BMI)">
        <ParamRow label="Country code" code={model.country?.code || model.country_code} value={model.country?.name || model.country_code} />
        <ParamRow label="Manufacturer identifier" code={model.manufacturer?.code || model.manufacturer_code} value={model.manufacturer?.name || model.manufacturer_code} />
      </SectionCard>

      <SectionCard title="Battery Descriptor Section (BDS)">
        <ParamRow label="Battery Capacity" code={model.capacity?.code || model.capacity_code} value={`${model.capacity?.value_kwh || model.capacity_code} kWh`} />
        <ParamRow label="Battery Chemistry" code={model.chemistry?.code || model.chemistry_code} value={model.chemistry?.name || model.chemistry_code} />
        <ParamRow label="Nominal voltage" code={model.voltage?.code || model.voltage_code} value={`${model.voltage?.value_v || model.voltage_code} V`} />
        <ParamRow label="Cell Origin" code={model.cell_origin?.code || model.cell_origin_code} value={model.cell_origin?.country_name || model.cell_origin_code} />
        <ParamRow label="Extinguisher Class" code={model.extinguisher?.code || model.extinguisher_code} value={model.extinguisher?.class_name || model.extinguisher_code} />
      </SectionCard>

      <SectionCard title="Battery Identifier (BI)">
        <ParamRow label="Manufacturing Year" code={bpanData.year_code} value={bpanData.year?.year || bpanData.year_code} />
        <ParamRow label="Manufacturing Month" code={bpanData.month_code} value={bpanData.month?.name || bpanData.month_code} />
        <ParamRow label="Manufacturing Date" code={bpanData.date_code} value={bpanData.date?.day_num || bpanData.date_code} />
        <ParamRow label="Factory Code" code={model.factory?.code || model.factory_code} value={model.factory?.factory_name || model.factory_code} />
        <ParamRow label="Serial Number" code={String(bpanData.serial_number).padStart(4, '0')} value={`Unit ${bpanData.serial_number}`} />
      </SectionCard>

      <SectionCard title="Battery Material Composition Section (BMCS)">
        <ParamRow label="TAC Number" code={model.tac?.code || model.tac_code} value={model.tac?.tac_number || model.tac_code} />
        <ParamRow label="Number of cells per battery" code={model.num_cells?.code || model.num_cells_code} value={`${model.num_cells?.count || model.num_cells_code} Cells`} />
        <ParamRow label="Internal Resistance of Battery Pack" code={model.internal_resistance_code} value={model.internal_resistance ? `${model.internal_resistance.value_mohm} mΩ` : `${model.internal_resistance_code} mΩ`} />
        <ParamRow label="Battery Weight" code={model.weight_code} value={model.weight ? `${model.weight.value_kg} kg` : `${model.weight_code} kg`} />
        <ParamRow label="Battery warranty" code={model.warranty_code} value={model.warranty ? `${model.warranty.years} years` : `${model.warranty_code} years`} />
        <ParamRow label="Cell Type" code={model.cell_type?.code || model.cell_type_code} value={model.cell_type?.type_name || model.cell_type_code} />
        <ParamRow label="Cell form Factor" code={model.dimensions_code} value={model.dimensions ? `${model.dimensions.length_mm}×${model.dimensions.width_mm}×${model.dimensions.height_mm} mm` : `${model.dimensions_code} mm`} />
        <ParamRow label="Type of construction of battery pack" code={model.pack_construction?.code || model.pack_construction_code} value={model.pack_construction?.construction_type || model.pack_construction_code} />
        <ParamRow label="Type of construction of Module" code={model.module_construction?.code || model.module_construction_code} value={model.module_construction?.construction_type || model.module_construction_code} />
        <ParamRow label="Type of Cooling System" code={model.cooling?.code || model.cooling_code} value={model.cooling?.cooling_type || model.cooling_code} />
        <ParamRow label="Original power capability at 80% SoC" code={model.power_80_soc_code} value={model.power_80_soc ? `${model.power_80_soc.value_kw} kW` : `${model.power_80_soc_code} kW`} />
        <ParamRow label="Original power capability at 20% SoC" code={model.power_20_soc?.code || '-'} value={model.power_20_soc_value ? `${model.power_20_soc_value} kW` : '-'} />
      </SectionCard>

      <SectionCard title="Battery Carbon Footprint (BCF)">
        <ParamRow label="Total Battery Carbon Footprint Scaled kgCO2e/kWh" code={model.carbon_footprint_code} value={model.carbon_footprint ? `${model.carbon_footprint.value_kgco2ekwh} kgCO2e/kWh` : `${model.carbon_footprint_code} kgCO2e/kWh`} />
      </SectionCard>
      
      {pdfError && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">{pdfError}</div>}
      
      <div className="text-center pb-8">
        <button onClick={handleDownloadPDF} className="btn btn-primary text-lg px-8 py-3">
          Download PDF
        </button>
      </div>
    </div>
  );
}
