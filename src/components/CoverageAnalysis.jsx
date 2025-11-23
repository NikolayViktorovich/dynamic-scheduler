import React, { useMemo } from 'react';
import { Target, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';

const CoverageAnalysis = React.memo(({ skills, currentLevels, targetLevels, selectedSpecialty }) => {
  const metrics = useMemo(() => {
    let totalCurrent = 0;
    let totalTarget = 0;
    
    const skillMetrics = skills.map(skill => {
      const current = currentLevels[skill.id] || 0;
      const target = targetLevels[skill.id] || 0;
      const percentage = target > 0 ? Math.min(100, (current / target) * 100) : 100;
      
      totalCurrent += Math.min(current, target);
      totalTarget += target;

      return { ...skill, current, target, percentage };
    });

    const totalCoverage = totalTarget > 0 ? (totalCurrent / totalTarget) * 100 : 0;
    
    return { skillMetrics, totalCoverage };
  }, [skills, currentLevels, targetLevels]);

  const getStatus = useCallback((coverage) => {
    if (coverage >= 90) return { icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-500/10', label: 'Оптимально' };
    if (coverage >= 70) return { icon: TrendingUp, color: 'text-blue-500', bg: 'bg-blue-500/10', label: 'Хорошо' };
    return { icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-500/10', label: 'Есть пробелы' };
  }, []);

  const status = getStatus(metrics.totalCoverage);
  const StatusIcon = status.icon;

  if (!selectedSpecialty) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center border-2 border-dashed border-gray-200 dark:border-[#333] rounded-xl bg-gray-50/50 dark:bg-[#111]/50">
        <Target className="h-10 w-10 text-gray-300 dark:text-[#444] mb-3" />
        <p className="text-gray-500 dark:text-gray-400 font-medium">Выберите специальность для анализа</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-xl p-5">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">Покрытие навыков</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Соответствие требованиям рынка</p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold gradient-text">{metrics.totalCoverage.toFixed(0)}%</span>
        </div>
      </div>

      <div className={`flex items-center p-3 mb-6 rounded-lg ${status.bg} border border-transparent`}>
        <StatusIcon className={`h-5 w-5 ${status.color} mr-3`} />
        <div>
          <p className={`font-semibold ${status.color}`}>{status.label}</p>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
            {metrics.totalCoverage >= 70 
              ? 'Ваш профиль соответствует большинству требований' 
              : 'Рекомендуем добавить профильные курсы'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {metrics.skillMetrics.map(skill => {
          const isComplete = skill.percentage >= 100;
          return (
            <div key={skill.id} className="p-3 rounded-lg bg-gray-50 dark:bg-[#1A1A1A] border border-gray-100 dark:border-[#2A2A2A]">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{skill.name}</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                  isComplete 
                    ? 'text-green-600 bg-green-100 dark:bg-green-500/20 dark:text-green-400' 
                    : 'text-gray-500 bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
                }`}>
                  {skill.current}/{skill.target}
                </span>
              </div>
              <div className="h-1.5 w-full bg-gray-200 dark:bg-[#333] rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ease-out ${
                    isComplete ? 'bg-green-500' : 'bg-gradient-to-r from-[#FF3B77] to-[#7E3BF2]'
                  }`}
                  style={{ width: `${skill.percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
});

export default CoverageAnalysis;