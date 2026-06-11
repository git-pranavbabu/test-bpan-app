import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import useAuthStore from './hooks/useAuthStore';
import api from './services/api';

import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import AdminModels from './pages/AdminModels';
import AdminLookup from './pages/AdminLookup';
import BPANCreate from './pages/BPANCreate';
import Reports from './pages/Reports';
import BPANView from './pages/BPANView';
import Layout from './components/Layout';

function ProtectedRoute({ children, requireAdmin = false }) {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (requireAdmin && useAuthStore.getState().user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
}

function canCreateBpan() {
  const role = useAuthStore.getState().user?.role;
  return role === 'admin' || role === 'production_team';
}

function BPANCreateRoute() {
  if (!canCreateBpan()) {
    return <Navigate to="/dashboard" replace />;
  }
  return <BPANCreate />;
}

function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="text-center py-20">
      <h1 className="text-4xl font-bold text-gray-300 mb-4">404</h1>
      <p className="text-gray-500 mb-6">Page not found</p>
      <button onClick={() => navigate('/dashboard')} className="btn btn-primary">Go to Dashboard</button>
    </div>
  );
}

function App() {
  const { setUser, setLoading } = useAuthStore();
  
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await api.get('/auth/me');
          setUser(response.data);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, [setUser, setLoading]);
  
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="admin" element={
            <ProtectedRoute requireAdmin>
              <AdminDashboard />
            </ProtectedRoute>
          } />
          <Route path="bpan/create" element={
            <ProtectedRoute>
              <BPANCreateRoute />
            </ProtectedRoute>
          } />
          <Route path="bpan/reports" element={
            <ProtectedRoute>
              <Reports />
            </ProtectedRoute>
          } />
          <Route path="bpan/:code" element={
            <ProtectedRoute>
              <BPANView />
            </ProtectedRoute>
          } />
          <Route path="admin/models" element={
            <ProtectedRoute requireAdmin>
              <AdminModels />
            </ProtectedRoute>
          } />
          <Route path="admin/lookup" element={
            <ProtectedRoute requireAdmin>
              <AdminLookup />
            </ProtectedRoute>
          } />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
