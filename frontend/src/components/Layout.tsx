import { Outlet, Link, useNavigate } from 'react-router-dom';
import { Mail, Command, PenTool, LogOut } from 'lucide-react';
import { useAuthStore } from '../stores/auth';

function Layout() {
  const navigate = useNavigate();
  const { setToken } = useAuthStore();

  const handleLogout = () => {
    setToken(null);
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center px-4 text-gray-900">
                <Mail className="h-6 w-6" />
                <span className="ml-2 font-semibold">Agent Email IA</span>
              </Link>
              <div className="ml-6 flex space-x-4">
                <Link to="/compose" className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">
                  <PenTool className="h-4 w-4 mr-1" />
                  Composer
                </Link>
                <Link to="/command" className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900">
                  <Command className="h-4 w-4 mr-1" />
                  Commandes
                </Link>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
            >
              <LogOut className="h-4 w-4 mr-1" />
              Se déconnecter
            </button>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;