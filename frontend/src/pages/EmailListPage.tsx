import { useState, useEffect } from 'react';
import { Search, Mail } from 'lucide-react';
import api from '../lib/axios';
import { formatDate } from '../lib/utils';

interface Email {
  id: string;
  subject: string;
  sender: string;
  received_at: string;
  priority: 'high' | 'medium' | 'low';
  preview: string;
}

function EmailListPage() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');

  useEffect(() => {
    const fetchEmails = async () => {
      try {
        const params = new URLSearchParams();
        if (searchTerm) params.append('subject', searchTerm);
        if (priorityFilter !== 'all') params.append('priority', priorityFilter);

        const response = await api.get('/v1/emails?' + params.toString());
        setEmails(response.data);
      } catch (error) {
        console.error('Échec du chargement des emails:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchEmails();
  }, [searchTerm, priorityFilter]);

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'Haute';
      case 'medium':
        return 'Moyenne';
      case 'low':
        return 'Basse';
      default:
        return priority;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Emails</h1>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher des emails..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Toutes les priorités</option>
            <option value="high">Priorité haute</option>
            <option value="medium">Priorité moyenne</option>
            <option value="low">Priorité basse</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow divide-y divide-gray-200">
          {emails.map((email) => (
            <div key={email.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-start space-x-3">
                <Mail className="h-5 w-5 text-gray-400 mt-1" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-gray-900">{email.subject}</h3>
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${email.priority === 'high' ? 'bg-red-100 text-red-800' :
                          email.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                        }`}>
                        {getPriorityLabel(email.priority)}
                      </span>
                      <span className="text-sm text-gray-500">{formatDate(email.received_at)}</span>
                    </div>
                  </div>
                  <p className="mt-1 text-sm text-gray-500">{email.sender}</p>
                  <p className="mt-1 text-sm text-gray-600 line-clamp-2">{email.preview}</p>
                </div>
              </div>
            </div>
          ))}
          {emails.length === 0 && (
            <div className="p-6 text-center text-gray-500">
              Aucun email trouvé
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default EmailListPage;