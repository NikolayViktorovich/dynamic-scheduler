import React, { useState, useMemo, useEffect } from 'react';
import { ArrowRight, BookOpen, TrendingUp, Target, Zap, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useData } from '../context/DataContext';
import { minorsAPI } from '../api';

const MinorSelection = () => {
  const navigate = useNavigate();
  const { selectedMinorId, setMinor, setSelectedMinorId, primarySpecialty } = useData();
  const [localSelectedId, setLocalSelectedId] = useState(selectedMinorId);
  const [recommendedMinors, setRecommendedMinors] = useState([]);
  const [allMinors, setAllMinors] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMinors = async () => {
      try {
        setIsLoading(true);
        // Получаем рекомендации
        const recommendationsResponse = await minorsAPI.getRecommendations({ limit: 10 });
        const recommendations = recommendationsResponse.data.recommendations || [];
        setRecommendedMinors(recommendations);

        // Получаем все майнеры
        const allMinorsResponse = await minorsAPI.getAll({ include_inactive: false });
        setAllMinors(allMinorsResponse.data || []);
      } catch (err) {
        console.error('Ошибка загрузки майнеров:', err);
        setError('Не удалось загрузить список майнеров');
      } finally {
        setIsLoading(false);
      }
    };

    fetchMinors();
  }, []);

  // Разделяем на рекомендованные и остальные
  const recommendedIds = new Set(recommendedMinors.map(m => m.minor_id));
  const suitableMinors = recommendedMinors.slice(0, 3);
  const allOtherMinors = allMinors.filter(m => !recommendedIds.has(m.id));

  const handleSelect = (id) => {
    setLocalSelectedId(id);
  };

  const handleContinue = async () => {
    if (localSelectedId) {
      try {
        // Выбираем майнер через API
        await minorsAPI.select({ minor_id: localSelectedId });
        setMinor(localSelectedId);
        setSelectedMinorId(localSelectedId);
        // Обновляем страницу, чтобы загрузить все данные
        window.location.href = '/dashboard';
      } catch (err) {
        console.error('Ошибка выбора майнера:', err);
        // Все равно продолжаем, если API недоступен
        setMinor(localSelectedId);
        navigate('/dashboard');
      }
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      <div className="text-center mb-8">
        <span className="text-sm font-semibold text-[#FF3B77] uppercase tracking-wider">Шаг 3 из 3</span>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white mt-2">
          Выберите Майнер (ваша Орбита)
        </h1>
        <p className="text-base text-gray-600 dark:text-gray-400 mt-3">
          Орбита — это ваш дополнительный трек, который усилит вашу основную специальность <span className="font-semibold text-[#7E3BF2] dark:text-[#9F3BF2]">"{primarySpecialty?.name || 'специальность'}"</span>
        </p>
      </div>

      {isLoading && (
        <div className="text-center py-8">
          <div className="inline-block w-8 h-8 border-4 border-[#7E3BF2] border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Загрузка майнеров...</p>
        </div>
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Рекомендованные Майнеры */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-[#FF3B77]" /> Майнеры, подходящие вам
        </h2>
        <div className="grid lg:grid-cols-3 gap-4">
          {suitableMinors.map(minor => {
            const minorId = minor.minor_id || minor.id;
            return (
              <div 
                key={minorId}
                className={`p-5 rounded-xl border-2 transition-all cursor-pointer ${
                  localSelectedId === minorId 
                    ? 'bg-[#7E3BF2]/10 border-[#7E3BF2]'
                    : 'bg-white dark:bg-[#111111] border-gray-200 dark:border-[#333333]'
                }`}
                onClick={() => handleSelect(minorId)}
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">{minor.minor_name || minor.name}</h3>
                  {localSelectedId === minorId && <Check className="h-5 w-5 text-[#7E3BF2]" />}
                </div>
                
                {(minor.description || minor.minor_description) && (
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                    {minor.description || minor.minor_description}
                  </p>
                )}
                
                {minor.matching_tags && minor.matching_tags.length > 0 && (
                  <>
                    <h4 className="font-semibold text-gray-800 dark:text-white flex items-center mb-2 text-sm">
                      <Zap className="h-4 w-4 mr-2 text-[#7E3BF2]" /> Совпадающие теги:
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {minor.matching_tags.map((tag, idx) => (
                        <span 
                          key={idx}
                          className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 dark:bg-[#1A1A1A] text-purple-700 dark:text-gray-300"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </>
                )}
                {minor.reason && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 italic">
                    {minor.reason}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Все Майнеры */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center">
            <BookOpen className="h-5 w-5 mr-2 text-[#7E3BF2]" /> Показать все майнеры
        </h2>
        <div className="grid lg:grid-cols-4 gap-3">
            {allOtherMinors.map(minor => (
                <div 
                    key={minor.id}
                    className={`p-3 rounded-lg border transition-all cursor-pointer ${
                        localSelectedId === minor.id 
                            ? 'bg-purple-100/30 dark:bg-purple-900/30 border-[#7E3BF2]'
                            : 'bg-white dark:bg-[#111111] border-gray-200 dark:border-[#333333]'
                    }`}
                    onClick={() => handleSelect(minor.id)}
                >
                    <div className="flex justify-between items-center">
                        <span className="font-medium text-gray-800 dark:text-white text-sm">{minor.name}</span>
                        {localSelectedId === minor.id && <Check className="h-4 w-4 text-[#7E3BF2]" />}
                    </div>
                    {minor.description && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                        {minor.description}
                      </p>
                    )}
                </div>
            ))}
        </div>
      </div>

      <div className="flex justify-center">
        <button 
          onClick={handleContinue}
          disabled={!localSelectedId}
          className="flex items-center space-x-2 px-6 py-3 text-white rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span>Перейти к Орбите</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default MinorSelection;