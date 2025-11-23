import React, { useState, useEffect } from 'react'
import { Search, Plus, Minus, Target, BookOpen, Star, Clock, Filter, AlertTriangle } from 'lucide-react'
import SkillRadar from '../components/SkillRadar'
import { useData } from '../context/DataContext'

const WhatIf = () => {
  const { 
    SKILLS, 
    SPECIALTIES, 
    COURSES, 
    passedCourseIds, 
    currentSkills, 
    calculateSkillDeficit, 
    generateRoadmap,
    selectedSpecialtyId
  } = useData()

  const [whatIfSpecialtyId, setWhatIfSpecialtyId] = useState(selectedSpecialtyId)
  const [whatIfDeficit, setWhatIfDeficit] = useState({})
  const [whatIfRoadmap, setWhatIfRoadmap] = useState([])
  const [analysisDone, setAnalysisDone] = useState(false)
  const currentSpecialty = SPECIALTIES.find(s => s.id === selectedSpecialtyId) || SPECIALTIES[0];
  const whatIfSpecialty = SPECIALTIES.find(s => s.id === whatIfSpecialtyId) || currentSpecialty;

  useEffect(() => {
    const deficit = calculateSkillDeficit(currentSkills, whatIfSpecialty.targetSkills);
    setWhatIfDeficit(deficit);
    const roadmap = generateRoadmap(whatIfSpecialtyId, passedCourseIds, []);
    setWhatIfRoadmap(roadmap);
    setAnalysisDone(true);
  }, [whatIfSpecialtyId, currentSkills, passedCourseIds, calculateSkillDeficit, generateRoadmap])

  const relevantSkills = SKILLS.filter(s => whatIfSpecialty.targetSkills[s.id] > 0);
  const deficitSkillsArray = Object.values(whatIfDeficit);

  const calculateCoverage = () => {
    let totalCoverage = 0;
    let maxPossible = 0;

    relevantSkills.forEach(skill => {
      const current = currentSkills[skill.id] || 0;
      const required = whatIfSpecialty.targetSkills[skill.id] || 0;
      totalCoverage += Math.min(current, required);
      maxPossible += required;
    });

    return maxPossible > 0 ? Math.round((totalCoverage / maxPossible) * 100) : 0;
  };
  
  const coverage = calculateCoverage();
  const totalCoursesNeeded = whatIfRoadmap.reduce((sum, semester) => sum + semester.courses.length, 0);
  const semestersNeeded = whatIfRoadmap.filter(s => s.courses.length > 0).length;


  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <header className="mb-10 fade-in">
        <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 dark:text-white">
          Функция «Что, если?»
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 mt-2">
          Моделирование итогового профиля навыков при выборе другой специальности.
        </p>
      </header>
      <div className="bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-2xl p-6 shadow-lg mb-12 slide-up">
        <div className="flex items-center space-x-4">
          <Star className="h-6 w-6 text-[#FF3B77] flex-shrink-0" />
          <label className="text-lg font-semibold text-gray-900 dark:text-white flex-shrink-0">
            Специальность для моделирования:
          </label>
          <select 
            value={whatIfSpecialtyId} 
            onChange={(e) => setWhatIfSpecialtyId(e.target.value)}
            className="custom-select max-w-sm"
          >
            {SPECIALTIES.map(s => (
              <option key={s.id} value={s.id}>
                {s.name} {s.id === selectedSpecialtyId ? '(Текущая)' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {analysisDone && (
        <div className="space-y-12">

          <section className="grid md:grid-cols-3 gap-6 fade-in">
            <div className="p-6 rounded-2xl bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] shadow-md">
                <h4 className="text-sm font-medium text-gray-500 dark:text-[#A0A0A0] mb-2">Общее покрытие навыков</h4>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{coverage}%</p>
                <p className="text-sm text-gray-600 dark:text-[#A0A0A0] mt-2">Ваш текущий профиль относительно <span className="font-semibold text-[#7E3BF2]">{whatIfSpecialty.name}</span>.</p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] shadow-md">
                <h4 className="text-sm font-medium text-gray-500 dark:text-[#A0A0A0] mb-2">Требуется курсов</h4>
                <p className="text-3xl font-bold text-gray-900 dark:text-white text-[#FF3B77]">{totalCoursesNeeded}</p>
                <p className="text-sm text-gray-600 dark:text-[#A0A0A0] mt-2">Общее количество обязательных и рекомендованных курсов.</p>
            </div>

            <div className="p-6 rounded-2xl bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] shadow-md">
                <h4 className="text-sm font-medium text-gray-500 dark:text-[#A0A0A0] mb-2">Продолжительность</h4>
                <p className="text-3xl font-bold text-gray-900 dark:text-white text-[#7E3BF2]">{semestersNeeded} сем.</p>
                <p className="text-sm text-gray-600 dark:text-[#A0A0A0] mt-2">Примерное количество семестров для прохождения оставшихся курсов.</p>
            </div>
          </section>

          <section className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <SkillRadar 
                skills={relevantSkills}
                currentLevels={currentSkills}
                targetLevels={whatIfSpecialty.targetSkills}
                title={`Целевой профиль: ${whatIfSpecialty.name}`}
              />
            </div>
            
            <div className="lg:col-span-1 bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-2xl p-6 transition-colors shadow-lg">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2 text-red-500" /> Дефицит навыков ({deficitSkillsArray.length})
                </h3>
                <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
                    {deficitSkillsArray.map((d) => {
                        const { name, current, target, gap, priority } = d;
                        const progress = Math.min(100, (current / target) * 100);

                        return (
                        <div key={name} className="p-3 border rounded-lg bg-gray-50 dark:bg-[#1A1A1A] border-gray-200 dark:border-[#333333]">
                            <div className="flex justify-between items-center text-sm font-medium mb-1">
                            <span className="text-gray-900 dark:text-white">{name}</span>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                                priority === 'high' 
                                ? 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-300' 
                                : priority === 'medium' 
                                    ? 'bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-300'
                                    : 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300'
                            }`}>
                                {priority === 'high' ? 'Критичный' : priority === 'medium' ? 'Средний' : 'Низкий'}
                            </span>
                            </div>
                            <div className="text-xs text-gray-500 dark:text-[#A0A0A0] pt-1">
                                Требуется: <span className="font-semibold text-[#FF3B77]">{gap} ур.</span>
                            </div>
                        </div>
                        )
                    })}
                </div>
            </div>
          </section>
          
          <section>
            <div className="bg-white dark:bg-[#111111] rounded-2xl shadow-lg dark:shadow-none p-6 gradient-border border border-gray-200 dark:border-[#333333]">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                    Прогнозируемая Дорожная карта для специальности: <span className="text-[#7E3BF2]">{whatIfSpecialty.name}</span>
                </h3>
                <div className="space-y-8">
                {whatIfRoadmap.map(semesterData => (
                    <div key={semesterData.semester} className="border-l-4 border-[#FF3B77] pl-4">
                        <h4 className="font-extrabold text-2xl text-gray-800 dark:text-white mb-4">
                            Семестр {semesterData.semester}
                        </h4>
                        
                        <div className="space-y-3">
                            {semesterData.courses.length === 0 ? (
                                <p className="text-gray-500 dark:text-[#666666] text-sm italic">
                                    Нет курсов для этого семестра.
                                </p>
                            ) : (
                                semesterData.courses.map(course => (
                                    <div 
                                        key={course.id}
                                        className={`p-4 rounded-xl border-2 transition-all duration-300 ${
                                            course.type === 'obligatory' 
                                                ? 'bg-blue-50 dark:bg-blue-900/10 border-blue-300 dark:border-blue-700/30' 
                                                : 'bg-purple-50 dark:bg-purple-900/10 border-purple-300 dark:border-purple-700/30'
                                        }`}
                                    >
                                        <div className="flex justify-between items-center">
                                            <div className="flex items-center space-x-3">
                                                <BookOpen className="h-5 w-5 text-[#FF3B77]" />
                                                <span className="font-medium text-gray-800 dark:text-white">{course.name}</span>
                                            </div>
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                                course.type === 'obligatory' 
                                                    ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300' 
                                                    : 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300'
                                            }`}>
                                                {course.type === 'obligatory' ? 'Обязательный' : 'Элективный'}
                                            </span>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                ))}
                </div>
            </div>
          </section>
        </div>
      )}
    </div>
  )
}

export default WhatIf