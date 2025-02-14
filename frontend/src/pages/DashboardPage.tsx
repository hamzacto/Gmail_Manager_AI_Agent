import { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle, Inbox } from 'lucide-react';
import api from '../lib/axios';

interface Email {
  id: string;
  subject: string;
  sender: string;
  snippet: string;
  date: string;
}

interface HealthStatus {
  version: string;
  status: 'healthy' | 'unhealthy';
  groq_api: boolean;
}

function DashboardPage() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [emailsResponse, healthResponse] = await Promise.all([
          api.get('/api/v1/emails/recent'),
          api.get('/health')
        ]);
        
        setEmails(emailsResponse.data);
        setHealth(healthResponse.data);
      } catch (error) {
        console.error('Échec du chargement des données du tableau de bord:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* État du Système */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">État du Système</h2>
        {health && (
          <div className="flex items-center space-x-4">
            <div className={`p-2 rounded-full ${health.status === 'healthy' ? 'bg-green-100' : 'bg-red-100'}`}>
              {health.status === 'healthy' ? (
                <CheckCircle className="h-6 w-6 text-green-600" />
              ) : (
                <AlertCircle className="h-6 w-6 text-red-600" />
              )}
            </div>
            <div>
              <p className="font-medium">
                Le système est {health.status === 'healthy' ? 'en bon état' : 'en difficulté'}
              </p>
              <p className="text-sm text-gray-500">
                Version: {health.version} | Service IA: {health.groq_api ? 'Connecté' : 'Déconnecté'}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Emails Récents */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Emails Récents</h1>
        <div className="flex items-center text-sm text-gray-500">
          <Inbox className="h-4 w-4 mr-1" />
          {emails.length} emails
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {emails.map((email) => (
            <li key={email.id} className="px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-blue-600 truncate">
                  {email.subject}
                </p>
                <div className="ml-2 flex-shrink-0 flex">
                  <p className="text-sm text-gray-500">
                    {new Date(email.date).toLocaleDateString('fr-FR')}
                  </p>
                </div>
              </div>
              <div className="mt-2">
                <p className="text-sm text-gray-600 line-clamp-2">{email.snippet}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default DashboardPage;