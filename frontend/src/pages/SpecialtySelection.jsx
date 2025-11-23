import React, { useState, useEffect } from 'react';
import { ArrowRight, Check, GraduationCap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { specializationsAPI, studentsAPI, authAPI } from '../api';

const SpecialtySelection = () => {
  const navigate = useNavigate();
  const { setSpecialty, setSelectedSpecialtyId } = useData();
  const [localSelectedId, setLocalSelectedId] = useState(null);
  const [specializations, setSpecializations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSpecializations = async () => {
      try {
        setIsLoading(true);
        const response = await specializationsAPI.getAll();
        setSpecializations(response.data);
      } catch (err) {
        console.error('Ошибка загрузки специальностей:', err);
        setError('Не удалось загрузить список специальностей');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSpecializations();
  }, []);

  const handleSelect = (id) => {
    setLocalSelectedId(id);
  };

  const handleContinue = async () => {
    console.log('handleContinue called, localSelectedId:', localSelectedId);
    
    if (!localSelectedId) {
      console.log('No localSelectedId, returning');
      return;
    }
    
    try {
      // Сохраняем выбор в контекст
      console.log('Setting specialty to:', localSelectedId);
      setSpecialty(localSelectedId);
      setSelectedSpecialtyId(localSelectedId);
      
      // Пытаемся установить через API, если пользователь авторизован
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          console.log('User is authenticated, calling API');
          await studentsAPI.setSpecialization(localSelectedId);
          console.log('Specialization set via API');
          
          // Проверяем, есть ли уже выбранный майнер
          try {
            const userResponse = await authAPI.getMe();
            if (userResponse.data.minor_ids && userResponse.data.minor_ids.length > 0) {
              console.log('User has minor, navigating to dashboard');
              navigate('/dashboard');
              return;
            }
          } catch (err) {
            console.error('Ошибка проверки майнера:', err);
          }
        } catch (err) {
          console.error('Ошибка выбора специальности:', err);
          // Продолжаем даже при ошибке API
        }
      } else {
        console.log('User not authenticated, skipping API call');
      }
      
      // Переходим к выбору майнера
      console.log('Navigating to /onboarding/minor');
      navigate('/onboarding/minor');
    } catch (error) {
      console.error('Error in handleContinue:', error);
      // Все равно переходим к выбору майнера
      navigate('/onboarding/minor');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <div className="text-center mb-8">
        <span className="text-sm font-semibold text-[#FF3B77] uppercase tracking-wider">Шаг 2 из 3</span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white mt-2">
          Выберите основную специальность
        </h1>
        <p className="text-base text-gray-600 dark:text-gray-400 mt-3">
          Это ваш главный трек обучения, который определит базовые навыки и диплом.
        </p>
      </div>

      {isLoading && (
        <div className="text-center py-8">
          <div className="inline-block w-8 h-8 border-4 border-[#FF3B77] border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Загрузка специальностей...</p>
        </div>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="space-y-4 mb-8">
        {specializations.map(specialty => {
          const isSelected = localSelectedId === specialty.id;
          return (
            <div
              key={specialty.id}
              onClick={() => handleSelect(specialty.id)}
              className={`p-5 rounded-xl border-2 transition-all cursor-pointer ${
                isSelected
                  ? 'bg-[#FF3B77]/10 border-[#FF3B77]'
                  : 'bg-white dark:bg-[#111111] border-gray-200 dark:border-[#333333] hover:border-[#FF3B77]/50'
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{specialty.name}</h3>
                  {specialty.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{specialty.description}</p>
                  )}
                </div>
                {isSelected && <Check className="h-5 w-5 text-[#FF3B77] flex-shrink-0 ml-3" />}
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <GraduationCap className="h-4 w-4 mr-1" />
                  {specialty.duration_years ? `${specialty.duration_years} лет` : 'Профиль'}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex justify-center">
        <button 
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Button clicked, localSelectedId:', localSelectedId);
            handleContinue();
          }}
          disabled={!localSelectedId || isLoading}
          className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-[#FF3B77] to-[#7E3BF2] text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          <span>Продолжить к выбору майнера</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default SpecialtySelection;