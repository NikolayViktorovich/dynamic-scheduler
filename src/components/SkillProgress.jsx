import React from 'react';

const SkillProgress = React.memo(({ skills, currentLevels, targetLevels, title = "Профиль навыков" }) => {
  return (
    <div className="bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-xl p-5">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">{title}</h3>
      <div className="space-y-4">
        {skills.map(skill => {
          const current = currentLevels[skill.id] || 0;
          const target = targetLevels[skill.id] || 0;
          const gap = target - current;
          const progress = target > 0 ? Math.min(100, (current / target) * 100) : 0;
          
          return (
            <div key={skill.id} className="group">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium text-gray-900 dark:text-white text-sm">
                  {skill.name}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {current} / {target}
                  </span>
                  {gap > 0 && (
                    <span className="text-xs bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-300 px-2 py-1 rounded">
                      +{gap}
                    </span>
                  )}
                </div>
              </div>
              
              <div className="relative">
                <div className="w-full bg-gray-100 dark:bg-[#1A1A1A] rounded-full h-2 overflow-hidden">
                  <div 
                    className="h-2 rounded-full transition-all duration-700 ease-out"
                    style={{
                      width: `${current}%`,
                      background: 'linear-gradient(90deg, #FF3B77 0%, #7E3BF2 100%)',
                    }}
                  />
                  
                  {target > current && (
                    <div 
                      className="absolute top-0 h-2 w-0.5 bg-white dark:bg-[#0A0A0A] rounded-full border border-[#7E3BF2]"
                      style={{ left: `${target}%`, transform: 'translateX(-50%)' }}
                    />
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
});

export default SkillProgress;