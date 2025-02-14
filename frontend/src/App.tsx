import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ComposeEmailPage from './pages/ComposeEmailPage';
import CommandPage from './pages/CommandPage';
import Layout from './components/Layout';
import { useAuthStore } from './stores/auth';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="compose" element={<ComposeEmailPage />} />
          <Route path="command" element={<CommandPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;