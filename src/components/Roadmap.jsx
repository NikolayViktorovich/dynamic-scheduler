import React, { useCallback } from 'react';
import { CheckCircle, BookOpen, Clock } from 'lucide-react';
import { useData } from '../context/DataContext';

const Roadmap = React.memo(({ roadmapData, onCourseClick }) => {
  const { selectedElectives, passedCourseIds } = useData();
  
  const isSelectedForFuture = useCallback((courseId) => 
    selectedElectives.includes(courseId),
    [selectedElectives]
  );

  return (
    <div className="bg-white dark:bg-[#111111] rounded-xl border border-gray-200 dark:border-[#333333] p-5">
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Дорожная карта обучения</h3>
      <div className="space-y-6">
        {roadmapData.map(semesterData => (
          <div key={semesterData.semester} className="border-l-4 border-[#7E3BF2] pl-4">
            <h4 className="font-bold text-lg text-gray-800 dark:text-white mb-3">
                Семестр {semesterData.semester}
            </h4>
            
            <div className="space-y-3">
              {semesterData.courses.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-sm italic">
                    План на этот семестр будет сформирован позже.
                </p>
              ) : (
                semesterData.courses.map(course => {
                  const isCompleted = passedCourseIds.includes(course.id);
                  const isSelected = isSelectedForFuture(course.id);
                  const isElective = course.type === 'elective';
                  
                  return (
                    <div 
                      key={course.id}
                      onClick={() => isElective && !isCompleted && onCourseClick(course)}
                      className={`p-3 rounded-lg border transition-all ${
                        isCompleted 
                          ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-500/30' 
                          : isSelected 
                            ? 'bg-[#7E3BF2]/10 border-[#7E3BF2]'
                            : isElective 
                              ? 'bg-gray-50 dark:bg-[#1A1A1A] border-gray-200 dark:border-[#333333] hover:border-[#7E3BF2] cursor-pointer'
                              : 'bg-gray-50 dark:bg-[#1A1A1A] border-gray-200 dark:border-[#333333] opacity-80'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                          <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                            isCompleted ? 'bg-green-500' : isSelected ? 'bg-[#7E3BF2]' : 'bg-gray-400'
                          }`}></span>
                          <div className="text-sm font-medium text-gray-800 dark:text-white">
                            {course.name}
                            {isCompleted && (
                              <span className="ml-2 text-xs text-green-600 dark:text-green-400 flex items-center">
                                <CheckCircle className="h-3 w-3 mr-1" /> Пройден
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 flex-shrink-0">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            course.type === 'obligatory' 
                              ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300' 
                              : 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300'
                          }`}>
                            {course.type === 'obligatory' ? 'Обязательный' : 'Элективный'}
                          </span>
                          <span className="text-xs text-gray-600 dark:text-gray-400 flex items-center">
                            <Clock className="h-3 w-3 mr-1" /> {course.credits} кр.
                          </span>
                        </div>
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
});

export default Roadmap;