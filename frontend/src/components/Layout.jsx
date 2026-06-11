import { Outlet, Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../hooks/useAuthStore';

export default function Layout() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  
  const canCreate = user?.role === 'admin' || user?.role === 'production_team';

  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  if (!isAuthenticated) {
    return <Outlet />;
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-blue-600">BPAN System</h1>
              <div className="hidden md:flex ml-10 space-x-8">
                <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                  Dashboard
                </Link>
                {canCreate && (
                  <Link to="/bpan/create" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                    Create BPAN
                  </Link>
                )}
                <Link to="/bpan/reports" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                  Reports
                </Link>
                {user?.role === 'admin' && (
                  <Link to="/admin" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                    Admin
                  </Link>
                )}
              </div>
            </div>
            <div className="flex items-center">
              <span className="mr-4 text-sm text-gray-600">{user?.username}</span>
              <button onClick={handleLogout} className="btn btn-secondary text-sm">
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}
