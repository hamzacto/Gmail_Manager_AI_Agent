import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail } from 'lucide-react';
import api from '../lib/axios';
import { useAuthStore } from '../stores/auth';
import toast from 'react-hot-toast';

function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, setToken } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);

  const handleGoogleLogin = async () => {
    try {
      const response = await api.get('/api/v1/auth/google/url');
      if (!response.data?.url) {
        toast.error('Réponse invalide du serveur');
        return;
      }

      // Open popup window
      const popup = window.open(
        response.data.url,
        'Connexion Google',
        'width=500,height=600'
      );

      // Listen for message from popup
      window.addEventListener('message', (event) => {
        if (event.data.token) {
          setToken(event.data.token);
          toast.success('Connexion réussie !');
          navigate('/');
        }
      }, { once: true });

    } catch (error) {
      console.error('Échec de l\'obtention de l\'URL OAuth Google:', error);
      toast.error('Échec de l\'initialisation de la connexion Google');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
            <Mail className="h-6 w-6 text-blue-600" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Agent Email IA
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Connectez-vous avec Google pour gérer vos emails intelligemment
          </p>
        </div>
        <button
          onClick={handleGoogleLogin}
          className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <img
            className="h-5 w-5 mr-2"
            src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
            alt="Logo Google"
          />
          Se connecter avec Google
        </button>
      </div>
    </div>
  );
}

export default LoginPage;