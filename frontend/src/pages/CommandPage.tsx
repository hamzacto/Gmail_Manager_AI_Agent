import React, { useState } from 'react';
import { Send } from 'lucide-react';
import api from '../lib/axios';
import toast from 'react-hot-toast';

interface CommandResponse {
  id?: string;
  threadId?: string;
  subject?: string;
  from?: string;
  to?: string;
  date?: string;
  body?: string;
}

function CommandPage() {
  const [command, setCommand] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CommandResponse | string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;

    setLoading(true);
    try {
      const response = await api.post<CommandResponse | string>('/api/emails/process-command', {
        command: command.trim()
      });
      
      setResult(response.data);
      toast.success('Commande exécutée avec succès');
    } catch (error) {
      console.error('Échec du traitement de la commande:', error);
      toast.error('Échec du traitement de la commande');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">Centre de Commandes IA</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="command" className="block text-sm font-medium text-gray-700 mb-2">
              Entrez votre commande
            </label>
            <input
              type="text"
              id="command"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="ex: 'envoyer un email à jean@exemple.com concernant la réunion de demain'"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <Send className="h-4 w-4 mr-2" />
            {loading ? 'Traitement...' : 'Exécuter la commande'}
          </button>
        </form>

        {result && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-4">Résultat</h2>
            <div className="bg-gray-50 rounded-lg p-4">
              {typeof result === 'string' ? (
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">{result}</pre>
              ) : (
                <>
                  {result.id && (
                    <p className="text-sm text-gray-600 mb-2">
                      Message envoyé avec succès (ID: {result.id})
                    </p>
                  )}
                  {result.subject && (
                    <div className="bg-white p-3 rounded border border-gray-200">
                      <p className="font-medium">{result.subject}</p>
                      {result.from && <p className="text-sm text-gray-500">De: {result.from}</p>}
                      {result.to && <p className="text-sm text-gray-500">À: {result.to}</p>}
                      {result.body && <p className="mt-2 text-gray-700">{result.body}</p>}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CommandPage;