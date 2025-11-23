import React, { useState, useEffect } from 'react';
import { User, Settings, LogOut, Moon, Sun, Home } from 'lucide-react'; // Target будет удален
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { useNotifications } from '../context/NotificationContext';
import UserProfileModal from './UserProfileModal';
import { authAPI, specializationsAPI, minorsAPI } from '../api';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isUrFUStudent, selectedSpecialtyId, selectedMinorId, setSelectedSpecialtyId, setSelectedMinorId } = useData();
  const [isDark, setIsDark] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoadingUser, setIsLoadingUser] = useState(false);
  const [specializationName, setSpecializationName] = useState(null);
  const [minorName, setMinorName] = useState(null);
  const { showSuccess, showError } = useNotifications();
    
  const isUserAuthenticated = isUrFUStudent !== null;
  const isDashboardReady = selectedSpecialtyId && selectedMinorId;

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          setIsLoadingUser(true);
          const response = await authAPI.getMe();
          const userData = response.data;
          setUser(userData);
          
          // Загружаем название специальности
          if (userData.specialization_id) {
            try {
              const specResponse = await specializationsAPI.getById(userData.specialization_id);
              setSpecializationName(specResponse.data.name);
              // Синхронизируем с DataContext
              setSelectedSpecialtyId(userData.specialization_id);
            } catch (err) {
              console.error('Ошибка загрузки специальности:', err);
              setSpecializationName('Не удалось загрузить');
            }
          } else {
            setSpecializationName(null);
            setSelectedSpecialtyId(null);
          }
          
          // Загружаем название текущего майнера (selected)
          if (userData.minor_ids && userData.minor_ids.length > 0) {
            try {
              // Получаем историю майнеров, чтобы найти текущий выбранный
              const minorsHistoryResponse = await minorsAPI.getMyHistory();
              const selectedMinor = minorsHistoryResponse.data.find(
                (m) => m.status === 'selected'
              );
              
              if (selectedMinor) {
                const minorResponse = await minorsAPI.getById(selectedMinor.minor_id);
                setMinorName(minorResponse.data.name);
                // Синхронизируем с DataContext
                setSelectedMinorId(selectedMinor.minor_id);
              } else {
                setMinorName(null);
                setSelectedMinorId(null);
              }
            } catch (err) {
              console.error('Ошибка загрузки майнера:', err);
              setMinorName('Не удалось загрузить');
            }
          } else {
            setMinorName(null);
            setSelectedMinorId(null);
          }
        } catch (err) {
          console.error('Ошибка загрузки профиля:', err);
        } finally {
          setIsLoadingUser(false);
        }
      }
    };

    if (isUserAuthenticated) {
      fetchUser();
    }
  }, [isUserAuthenticated]);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'light' || (!savedTheme && !prefersDark)) {
      setIsDark(false);
      document.documentElement.classList.remove('dark');
    } else {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }
  }, []);
    
  const toggleTheme = () => {
    const newIsDark = !isDark;
    setIsDark(newIsDark);
    
    if (newIsDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const handleLogout = () => {
    // Очищаем все данные из localStorage
    localStorage.removeItem('isUrFUStudent');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Сбрасываем состояние в DataContext
    setIsUrFUStudent(false);
    setSelectedSpecialtyId(null);
    setSelectedMinorId(null);
    
    // Перенаправляем на страницу авторизации
    window.location.href = '/onboarding/auth';
  };
    
  const handleProfileClick = async () => {
    setIsModalOpen(true);
    // Обновляем данные при открытии модального окна
    if (user) {
      await refreshUserData();
    }
  };
  
  const refreshUserData = async () => {
    try {
      const response = await authAPI.getMe();
      const userData = response.data;
      setUser(userData);
      
      // Обновляем название специальности
      if (userData.specialization_id) {
        try {
          const specResponse = await specializationsAPI.getById(userData.specialization_id);
          setSpecializationName(specResponse.data.name);
          // Синхронизируем с DataContext
          setSelectedSpecialtyId(userData.specialization_id);
        } catch (err) {
          console.error('Ошибка загрузки специальности:', err);
        }
      } else {
        setSpecializationName(null);
        setSelectedSpecialtyId(null);
      }
      
      // Обновляем название майнера
      if (userData.minor_ids && userData.minor_ids.length > 0) {
        try {
          const minorsHistoryResponse = await minorsAPI.getMyHistory();
          const selectedMinor = minorsHistoryResponse.data.find(
            (m) => m.status === 'selected'
          );
          
          if (selectedMinor) {
            const minorResponse = await minorsAPI.getById(selectedMinor.minor_id);
            setMinorName(minorResponse.data.name);
            // Синхронизируем с DataContext
            setSelectedMinorId(selectedMinor.minor_id);
          } else {
            setMinorName(null);
            setSelectedMinorId(null);
          }
        } catch (err) {
          console.error('Ошибка загрузки майнера:', err);
        }
      } else {
        setMinorName(null);
        setSelectedMinorId(null);
      }
    } catch (err) {
      console.error('Ошибка обновления данных пользователя:', err);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleChangePassword = async (data) => {
    try {
      const response = await authAPI.changePassword({
        current_password: data.currentPassword,
        new_password: data.newPassword,
        confirm_password: data.confirmPassword
      });
      
      // Показываем успешное сообщение
      const message = response.data?.message || 'Пароль успешно изменен';
      showSuccess(message);
      
      // Не закрываем модальное окно здесь - оно закроется в ChangePasswordModal после успешной отправки
    } catch (err) {
      console.error('Ошибка смены пароля:', err);
      // Пробрасываем ошибку дальше, чтобы ChangePasswordModal мог её обработать
      throw err;
    }
  };
    
  const handleMinorChangedSuccess = async (newMinorId) => {
    console.log('Minor changed via profile to:', newMinorId);
    // Обновляем данные пользователя после смены майнера
    await refreshUserData();
  };

  // Формируем данные пользователя для модального окна
  const userData = user ? {
    name: user.full_name,
    email: user.email,
    specialty: specializationName || (user.specialization_id ? 'Загрузка...' : 'Не выбрана'),
    minor: minorName || (user.minor_ids && user.minor_ids.length > 0 ? 'Загрузка...' : 'Не выбран'),
    avatarInitials: user.full_name ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) : 'U'
  } : {
    name: 'Загрузка...',
    email: '',
    specialty: '',
    minor: '',
    avatarInitials: 'U'
  };

  return (
    <>
      <header className="bg-white/80 dark:bg-[#0A0A0A]/80 backdrop-blur-md sticky top-0 z-40 border-b border-gray-200 dark:border-[#1A1A1A]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex justify-between items-center">
          <Link    
            to={isDashboardReady ? "/dashboard" : "/onboarding/auth"}    
            className="text-lg font-extrabold flex items-center space-x-2"
          >
            <span className="gradient-text">УрФУ KnowledgeHub</span>
          </Link>

          {isDashboardReady && (
            <div className="flex items-center space-x-3">
            </div>
          )}

          <div className="flex items-center space-x-2">
            <button    
              onClick={toggleTheme}
              className="p-2 rounded-full text-gray-600 dark:text-[#A0A0A0] hover:bg-gray-100 dark:hover:bg-[#1A1A1A] transition-colors"
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            
            {isUserAuthenticated ? (
              <button    
                onClick={handleProfileClick}
                className="flex items-center space-x-2 p-2 rounded-lg text-gray-600 dark:text-[#A0A0A0] hover:bg-gray-100 dark:hover:bg-[#1A1A1A] transition-colors"
                disabled={isLoadingUser}
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-[#FF3B77] to-[#7E3BF2] flex items-center justify-center text-white text-sm font-bold">
                  {userData.avatarInitials}
                </div>
              </button>
            ) : (
              <Link    
                to="/onboarding/auth"
                className="boost-button flex items-center space-x-2 text-sm px-3 py-2"
              >
                <User className="h-4 w-4" />
                <span>Начать</span>
              </Link>
            )}
          </div>
        </div>
      </header>
      
      <UserProfileModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        user={userData}
        onLogout={handleLogout}
        onChangeMinor={handleMinorChangedSuccess}
        onChangePassword={handleChangePassword}
      />
    </>
  );
};

export default Header;