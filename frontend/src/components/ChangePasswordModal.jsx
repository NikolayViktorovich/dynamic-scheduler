import React, { useState, useEffect, useCallback } from 'react';
import { Lock, Eye, EyeOff, ArrowRight, X } from 'lucide-react';
import { useNotifications } from '../context/NotificationContext';

const PasswordField = React.memo(({ label, name, value, show, fieldKey, onToggle, onChange, disabled }) => (
  <div className="space-y-2">
    <label className="text-xs font-medium text-gray-700 dark:text-gray-300 ml-1">{label}</label>
    <div className="relative group">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-[#7E3BF2] transition-colors" />
      </div>
      <input
        type={show ? 'text' : 'password'}
        name={name}
        placeholder={label}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="block w-full pl-10 pr-10 py-3 border border-gray-200 dark:border-[#333] rounded-xl bg-gray-50/50 dark:bg-[#1A1A1A]/50 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#7E3BF2]/20 focus:border-[#7E3BF2] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        required
      />
      <button
        type="button"
        className="absolute inset-y-0 right-0 pr-3 flex items-center"
        onClick={() => onToggle(fieldKey)}
        disabled={disabled}
      >
        {show ? (
          <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" />
        ) : (
          <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" />
        )}
      </button>
    </div>
  </div>
));

const ChangePasswordModal = ({ isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const { showError: showNotificationError } = useNotifications();
  // 1. Новое состояние для управления анимацией
  const [showModal, setShowModal] = useState(false);
  
  // 2. useEffect для запуска анимации открытия/закрытия
  useEffect(() => {
    if (isOpen) {
      // Открытие: задержка для применения начальных классов
      setTimeout(() => setShowModal(true), 10);
      // Очищаем форму и ошибки при открытии
      setFormData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setError(null);
    } else {
      // Закрытие: запуск анимации закрытия
      setShowModal(false);
    }
  }, [isOpen]);

  const handleChange = useCallback((e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  }, []);

  const handleClose = useCallback(() => {
    setShowModal(false);
    // Задержка закрытия после завершения анимации (300 мс)
    setTimeout(onClose, 300); 
  }, [onClose]);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setError(null);
    
    // Валидация
    if (!formData.currentPassword) {
      setError('Введите текущий пароль');
      return;
    }
    
    if (formData.newPassword.length < 6) {
      setError('Новый пароль должен содержать минимум 6 символов');
      return;
    }
    
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Новый пароль и его подтверждение не совпадают');
      return;
    }
    
    if (formData.currentPassword === formData.newPassword) {
      setError('Новый пароль должен отличаться от текущего');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Вызываем onSubmit, который обработает API запрос
      await onSubmit(formData);
      // Если успешно, очищаем форму и закрываем модальное окно
      setFormData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setShowModal(false);
      setTimeout(() => {
        onClose();
      }, 300);
    } catch (err) {
      // Ошибка уже обработана в onSubmit, просто показываем её
      const errorMessage = err.response?.data?.detail 
        ? (Array.isArray(err.response.data.detail) 
            ? err.response.data.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
            : typeof err.response.data.detail === 'string'
              ? err.response.data.detail
              : JSON.stringify(err.response.data.detail))
        : err.message || 'Ошибка при смене пароля';
      setError(errorMessage);
      showNotificationError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [formData, onSubmit, onClose]);

  const togglePasswordVisibility = useCallback((field) => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field] }));
  }, []);

  // Рендерим модальное окно, только если оно должно быть открыто, 
  // чтобы позволить анимации закрытия завершиться.
  if (!isOpen) return null;

  return (
    // 3. Анимация для фона
    <div 
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-md transition-opacity duration-300 ${
        showModal ? 'opacity-100' : 'opacity-0'
      }`}
      onClick={handleClose}
    >
      <div 
        // 4. Анимация для содержимого модального окна
        className={`w-full max-w-md mx-4 bg-white/70 dark:bg-[#111]/70 backdrop-blur-xl border border-white/20 dark:border-white/10 shadow-2xl rounded-3xl p-6 transition-all duration-300 ${
          showModal ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-4'
        }`}
        onClick={e => e.stopPropagation()}
      >
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#222222] transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#FF3B77] to-[#7E3BF2] mb-2">
            Смена пароля
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Введите текущий и новый пароль
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <PasswordField
            label="Текущий пароль"
            name="currentPassword"
            value={formData.currentPassword}
            show={showPasswords.current}
            fieldKey="current"
            onToggle={togglePasswordVisibility}
            onChange={handleChange}
            disabled={isLoading}
          />

          <PasswordField
            label="Новый пароль"
            name="newPassword"
            value={formData.newPassword}
            show={showPasswords.new}
            fieldKey="new"
            onToggle={togglePasswordVisibility}
            onChange={handleChange}
            disabled={isLoading}
          />

          <PasswordField
            label="Подтвердите новый пароль"
            name="confirmPassword"
            value={formData.confirmPassword}
            show={showPasswords.confirm}
            fieldKey="confirm"
            onToggle={togglePasswordVisibility}
            onChange={handleChange}
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-[#FF3B77] to-[#7E3BF2] text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-[#7E3BF2]/25 hover:shadow-[#FF3B77]/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 flex items-center justify-center group disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                <span>Сохранение...</span>
              </>
            ) : (
              <>
                <span>Сохранить новый пароль</span>
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default React.memo(ChangePasswordModal);