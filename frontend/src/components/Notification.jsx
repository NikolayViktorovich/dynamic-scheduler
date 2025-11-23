import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';

const Notification = ({ message, type = 'info', onClose, duration = 5000 }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(onClose, 300); // Ждем завершения анимации
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertCircle,
    info: Info,
  };

  const colors = {
    success: 'bg-green-500 dark:bg-green-600 border-green-600 dark:border-green-700',
    error: 'bg-red-500 dark:bg-red-600 border-red-600 dark:border-red-700',
    warning: 'bg-yellow-500 dark:bg-yellow-600 border-yellow-600 dark:border-yellow-700',
    info: 'bg-blue-500 dark:bg-blue-600 border-blue-600 dark:border-blue-700',
  };

  const Icon = icons[type] || Info;

  if (!isVisible) return null;

  return (
    <div
      className={`min-w-[300px] max-w-md rounded-lg shadow-lg border-2 ${colors[type]} text-white transform transition-all duration-300 ${
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      }`}
    >
      <div className="flex items-start p-4">
        <Icon className="h-5 w-5 flex-shrink-0 mt-0.5 mr-3" />
        <div className="flex-1">
          <p className="text-sm font-medium">{message}</p>
        </div>
        <button
          onClick={handleClose}
          className="ml-3 flex-shrink-0 text-white/80 hover:text-white transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

export default Notification;

