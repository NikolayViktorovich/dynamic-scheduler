import React, { useState, useEffect } from 'react';
import { X, Check, Target, Zap, ArrowRight, CornerUpLeft } from 'lucide-react';
import { useData } from '../context/DataContext';
import { useNotifications } from '../context/NotificationContext';
import { minorsAPI } from '../api';

const ChangeMinorModal = ({ isOpen, onClose, onMinorChanged }) => {
  const { selectedMinorId, setMinor } = useData();
  const [localSelectedId, setLocalSelectedId] = useState(selectedMinorId);
  const [showModal, setShowModal] = useState(false);
  const [recommendedMinors, setRecommendedMinors] = useState([]);
  const [allMinors, setAllMinors] = useState([]);
  const [currentMinor, setCurrentMinor] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const { showSuccess, showError } = useNotifications();

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => setShowModal(true), 10);
      setLocalSelectedId(selectedMinorId);
      fetchMinors();
    } else {
      setShowModal(false);
    }
  }, [isOpen, selectedMinorId]);

  const fetchMinors = async () => {
    try {
      setIsLoading(true);
      // Получаем похожие майнеры, если есть текущий
      if (selectedMinorId) {
        try {
          const similarResponse = await minorsAPI.getSimilar({ 
            current_minor_id: selectedMinorId,
            limit: 10 
          });
          setRecommendedMinors(similarResponse.data.recommendations || []);
        } catch (err) {
          console.error('Ошибка загрузки похожих майнеров:', err);
        }
      }
      
      // Получаем все майнеры
      const allMinorsResponse = await minorsAPI.getAll({ include_inactive: false });
      setAllMinors(allMinorsResponse.data || []);

      // Получаем текущий майнер
      if (selectedMinorId) {
        try {
          const currentMinorResponse = await minorsAPI.getById(selectedMinorId);
          setCurrentMinor(currentMinorResponse.data);
        } catch (err) {
          console.error('Ошибка загрузки текущего майнера:', err);
        }
      }
    } catch (err) {
      console.error('Ошибка загрузки майнеров:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const handleClose = () => {
    setShowModal(false);
    setTimeout(onClose, 300);
  };

  const handleSelect = (id) => {
    setLocalSelectedId(id);
  };

  const handleSave = async () => {
    if (localSelectedId && localSelectedId !== selectedMinorId) {
      try {
        await minorsAPI.select({ minor_id: localSelectedId });
        setMinor(localSelectedId);
        onMinorChanged(localSelectedId);
        showSuccess('Майнер успешно изменен');
        handleClose();
      } catch (err) {
        console.error('Ошибка выбора майнера:', err);
        const errorMessage = err.response?.data?.detail 
          ? (Array.isArray(err.response.data.detail) 
              ? err.response.data.detail.map(e => e.msg || e.message).join(', ')
              : err.response.data.detail)
          : 'Не удалось сменить майнер. Попробуйте позже.';
        showError(errorMessage);
      }
    } else {
      handleClose();
    }
  };

  // Объединяем рекомендованные и все майнеры, убирая дубликаты
  const allMinorsToShow = [
    ...recommendedMinors.map(m => ({ ...m, id: m.minor_id, name: m.minor_name })),
    ...allMinors.filter(m => !recommendedMinors.some(rm => rm.minor_id === m.id))
  ];

  return (
    <div 
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-md transition-opacity duration-300 ${
        showModal ? 'opacity-100' : 'opacity-0'
      }`}
      onClick={handleClose}
    >
      <div 
        className={`w-full max-w-2xl mx-4 bg-white dark:bg-[#111111] rounded-2xl shadow-xl border border-gray-200 dark:border-[#222222] transition-all duration-300 ${
          showModal ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-4'
        }`}
        onClick={e => e.stopPropagation()}
      >
        <div className="p-6">
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#222222] transition-colors"
          >
            <X className="h-5 w-5" />
          </button>

          <div className="flex items-center space-x-2 mb-4">
            <Target className="h-6 w-6 text-[#7E3BF2]" />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Смена майнера</h2>
          </div>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            Текущий выбор: <span className="font-semibold">"{currentMinor?.name || 'Не выбран'}"</span>
          </p>

          {isLoading && (
            <div className="text-center py-8">
              <div className="inline-block w-8 h-8 border-4 border-[#7E3BF2] border-t-transparent rounded-full animate-spin"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Загрузка майнеров...</p>
            </div>
          )}

          <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
            {allMinorsToShow.map(minor => {
              const isSelected = localSelectedId === minor.id;
              const isCurrent = selectedMinorId === minor.id;

              return (
                <div
                  key={minor.id}
                  onClick={() => handleSelect(minor.id)}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-[#7E3BF2]/10 border-[#7E3BF2] shadow-lg' // ИЗМЕНЕНИЕ: Убран градиент
                      : 'bg-white dark:bg-[#1A1A1A] border-gray-200 dark:border-[#333333] hover:border-[#7E3BF2]/50'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white">{minor.name}</h3>
                        {isCurrent && (
                          <span className="px-2 py-1 text-xs bg-green-500/20 text-green-700 dark:text-green-300 rounded-full">
                            Текущий
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-300">{minor.description || minor.minor_description}</p>
                    </div>
                    {isSelected && <Check className="h-5 w-5 text-[#7E3BF2] flex-shrink-0 ml-4" />}
                  </div>
                  
                  {(minor.matching_tags || minor.tags) && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {(minor.matching_tags || minor.tags || []).map((tag, idx) => (
                        <span 
                          key={idx}
                          className="px-2 py-1 text-xs bg-purple-100 dark:bg-[#2A2A2A] text-purple-700 dark:text-gray-300 rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
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

        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200 dark:border-[#222222]">
          <button
            onClick={handleClose}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-xl text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-[#1A1A1A] transition-colors"
          >
            <CornerUpLeft className="h-4 w-4" />
            <span>Отмена</span>
          </button>
          <button
            onClick={handleSave}
            disabled={!localSelectedId || localSelectedId === selectedMinorId}
            className="boost-button-primary flex items-center space-x-2 px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>Сохранить</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChangeMinorModal;