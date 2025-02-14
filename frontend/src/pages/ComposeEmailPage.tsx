import React, { useState } from 'react';
import { Send, Wand2 } from 'lucide-react';
import api from '../lib/axios';
import toast from 'react-hot-toast';

interface DraftResponse {
  subject: string;
  body: string;
}

function ComposeEmailPage() {
  const [recipients, setRecipients] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [context, setContext] = useState('');
  const [loading, setLoading] = useState(false);
  const [draftLoading, setDraftLoading] = useState(false);

  const handleSendEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post('/api/v1/emails/send', {
        recipients: recipients.split(',').map(email => email.trim()),
        subject,
        body
      });
      
      toast.success('Email envoyé avec succès !');
      // Clear form
      setRecipients('');
      setSubject('');
      setBody('');
    } catch (error) {
      console.error('Échec de l\'envoi de l\'email:', error);
      toast.error('Échec de l\'envoi de l\'email');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDraft = async () => {
    if (!context) {
      toast.error('Veuillez fournir un contexte pour le brouillon');
      return;
    }

    setDraftLoading(true);
    try {
      const response = await api.post<DraftResponse>('/api/v1/emails/draft', {
        context,
        recipient: recipients || undefined
      });
      
      setSubject(response.data.subject);
      setBody(response.data.body);
      toast.success('Brouillon généré avec succès !');
    } catch (error) {
      console.error('Échec de la génération du brouillon:', error);
      toast.error('Échec de la génération du brouillon');
    } finally {
      setDraftLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">Composer un Email</h1>

        {/* Générateur de brouillon IA */}
        <div className="mb-8 p-4 bg-blue-50 rounded-lg">
          <h2 className="text-lg font-semibold mb-3">Générer un brouillon IA</h2>
          <div className="space-y-4">
            <textarea
              placeholder="Décrivez ce que vous voulez écrire..."
              value={context}
              onChange={(e) => setContext(e.target.value)}
              className="w-full h-24 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleGenerateDraft}
              disabled={draftLoading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <Wand2 className="h-4 w-4 mr-2" />
              {draftLoading ? 'Génération...' : 'Générer un brouillon'}
            </button>
          </div>
        </div>

        {/* Formulaire d'email */}
        <form onSubmit={handleSendEmail} className="space-y-6">
          <div>
            <label htmlFor="recipients" className="block text-sm font-medium text-gray-700">
              À 
            </label>
            <input
              type="text"
              id="recipients"
              value={recipients}
              onChange={(e) => setRecipients(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="email@exemple.com"
              required
            />
          </div>

          <div>
            <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
              Objet
            </label>
            <input
              type="text"
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label htmlFor="body" className="block text-sm font-medium text-gray-700">
              Message
            </label>
            <textarea
              id="body"
              rows={8}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <Send className="h-4 w-4 mr-2" />
              {loading ? 'Envoi...' : 'Envoyer l\'email'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ComposeEmailPage;