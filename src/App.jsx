import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { DataProvider, useData } from './context/DataContext'
import { NotificationProvider } from './context/NotificationContext'
import Dashboard from './pages/Index'
import WhatIf from './pages/Builder'
import Header from './components/Header'
import Auth from './pages/Auth'
import SpecialtySelection from './pages/SpecialtySelection'
import MinorSelection from './pages/MinorSelection'

const ProtectedRoute = ({ element }) => {
  const { isUrFUStudent, selectedSpecialtyId, selectedMinorId, isLoadingUser } = useData();

  // Показываем загрузку, пока проверяем авторизацию
  if (isLoadingUser || isUrFUStudent === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-[#FF3B77] border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Загрузка...</p>
        </div>
      </div>
    );
  }
  
  if (!isUrFUStudent) {
    return <Navigate to="/onboarding/auth" replace />;
  }
  
  // Шаг 2: Выбор Основной специальности
  if (!selectedSpecialtyId) {
    return <Navigate to="/onboarding/specialty" replace />;
  }
  
  // Шаг 3: Выбор Майнера (Орбиты)
  if (!selectedMinorId) {
    return <Navigate to="/onboarding/minor" replace />;
  }

  return element;
}

const AppContent = () => {
  const { selectedSpecialtyId } = useData();

  return (
    <div className="min-h-screen bg-white dark:bg-[#0A0A0A] transition-colors">
      <Header />
      <Routes>
        <Route path="/onboarding/auth" element={<Auth />} />
        
        {/* Шаг 2: Выбор Основной специальности */}
        <Route 
          path="/onboarding/specialty" 
          element={<SpecialtySelection />} 
        />
        
        {/* Шаг 3: Выбор Майнера (Орбиты) */}
        <Route
          path="/onboarding/minor"
          element={<MinorSelection />}
        />
        
        {/* Защищенные маршруты */}
        <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
        <Route path="/what-if" element={<ProtectedRoute element={<WhatIf />} />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  );
};

function App() {
  return (
    <Router>
      <NotificationProvider>
        <DataProvider>
          <AppContent />
        </DataProvider>
      </NotificationProvider>
    </Router>
  );
}

export default App;