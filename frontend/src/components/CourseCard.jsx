import React, { useCallback } from 'react';
import { Book, Check, TrendingUp } from 'lucide-react';

const CourseCard = React.memo(({ course, isSelected, onSelect }) => {
  const handleSelect = useCallback(() => {
    onSelect(course.id);
  }, [course.id, onSelect]);

  return (
    <div className={`p-5 rounded-xl border-2 transition-all ${
      isSelected 
        ? 'bg-white dark:bg-[#111111] border-red-500 shadow-lg' 
        : 'bg-white dark:bg-[#111111] border-gray-200 dark:border-[#333333] hover:shadow-md'
    }`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="font-semibold text-lg text-gray-900 dark:text-white mb-2">{course.name}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{course.description}</p>
        </div>
        {isSelected ? (
          <Check className="h-5 w-5 text-red-500 flex-shrink-0 ml-3" />
        ) : (
          <Book className="h-5 w-5 text-gray-400 flex-shrink-0 ml-3" />
        )}
      </div>

      {(course.skills || course.missingSkills) && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-[#333333]">
          <h4 className="text-sm font-medium text-white flex items-center mb-2">
            <TrendingUp className="h-4 w-4 mr-2 text-white" />
            {course.missingSkills ? 'Недостающие навыки:' : 'Развиваемые навыки:'}
          </h4>
          <div className="flex flex-wrap gap-2">
            {course.skills ? (
              course.skills.map((skill, idx) => (
                <span 
                  key={skill.id || skill.skill_id || idx}
                  className="px-2 py-1 text-xs bg-transparent text-white rounded-lg border border-white/50"
                >
                  {skill.name || skill.skill_name} {skill.level ? `+${skill.level}` : ''}
                </span>
              ))
            ) : course.missingSkills ? (
              course.missingSkills.map((skillName, idx) => (
                <span 
                  key={idx}
                  className="px-2 py-1 text-xs bg-transparent text-white rounded-lg border border-white/50"
                >
                  {skillName}
                </span>
              ))
            ) : null}
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200 dark:border-[#333333]">
        <span className="text-sm text-gray-500 dark:text-gray-400 opacity-50">Уровень: Базовая</span>
        <button
          onClick={handleSelect}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-md ${
            isSelected 
              ? 'bg-red-500 text-white hover:bg-red-600' 
              : 'bg-transparent border border-white/50 text-white hover:border-white hover:bg-white/10'
          }`}
        >
          {isSelected ? 'Убрать из плана' : 'Добавить в план'}
        </button>
      </div>
    </div>
  );
});

export default CourseCard;