import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { authUtils } from './utils/auth';
import AuthPage from './pages/AuthPage';
import HomePage from './pages/HomePage';
import UserPage from './pages/UserPage';
import SettingsPage from './pages/SettingsPage';
import ManagePage from './pages/ManagePage';

// Защищенный маршрут
const ProtectedRoute = ({ children }) => {
  if (!authUtils.isAuthenticated()) {
    return <Navigate to="/auth" replace />;
  }
  return children;
};

// Маршрут только для ассистентов
const AssistentOnlyRoute = ({ children }) => {
  if (!authUtils.isAuthenticated()) {
    return <Navigate to="/auth" replace />;
  }
  const user = authUtils.getUser();
  if (user?.status !== 'ASSISTENT') {
    return <Navigate to="/" replace />;
  }
  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/user"
          element={
            <ProtectedRoute>
              <UserPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/manage"
          element={
            <AssistentOnlyRoute>
              <ManagePage />
            </AssistentOnlyRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;



