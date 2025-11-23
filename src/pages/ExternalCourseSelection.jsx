import React, { useState } from 'react'
import { Check, ArrowRight, BookOpen } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useData } from '../context/DataContext'

const ExternalCourseSelection = () => {
  const navigate = useNavigate()
  const { COURSES, passedCourseIds, setPassedCourses } = useData()
  const availableCourses = COURSES.filter(c => c.type === 'obligatory' || c.id.startsWith('e_')); 
  const [selectedCourses, setSelectedCourses] = useState(passedCourseIds)

  const toggleCourse = (courseId) => {
    setSelectedCourses(prev => 
      prev.includes(courseId)
        ? prev.filter(id => id !== courseId)
        : [...prev, courseId]
    )
  }

  const handleContinue = () => {
    setPassedCourses(selectedCourses)
    navigate('/onboarding/specialty')
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <div className="text-center mb-10 fade-in">
        <span className="text-sm font-semibold text-[#FF3B77] uppercase tracking-wider">Шаг 1 из 2</span>
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mt-2">
          Какие курсы вы уже прошли?
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 mt-3 max-w-2xl mx-auto">
          Выберите курсы, которые вы изучили в другом вузе или на онлайн-платформах. Это поможет нам рассчитать ваш текущий профиль навыков.
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {availableCourses.map(course => (
          <div 
            key={course.id}
            onClick={() => toggleCourse(course.id)}
            className={`p-5 rounded-2xl border-2 transition-all duration-300 cursor-pointer ${
              selectedCourses.includes(course.id)
                ? 'bg-gradient-to-r from-[#7E3BF2]/10 to-[#FF3B77]/10 border-[#7E3BF2] shadow-xl'
                : 'bg-white dark:bg-[#111111] border-gray-200 dark:border-[#333333] hover:shadow-md'
            }`}
          >
            <div className="flex justify-between items-start">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{course.name}</h3>
              {selectedCourses.includes(course.id) ? (
                <Check className="h-6 w-6 text-[#7E3BF2] flex-shrink-0" />
              ) : (
                <BookOpen className="h-6 w-6 text-gray-400 flex-shrink-0" />
              )}
            </div>
            <p className="text-sm text-gray-600 dark:text-[#A0A0A0]">{course.description}</p>

            <div className="mt-3 flex flex-wrap gap-2">
                {course.skillsGained.map(skill => (
                    <span 
                      key={skill.skillId}
                      className="px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-300"
                    >
                      {useData().SKILLS.find(s => s.id === skill.skillId)?.name} +{skill.level}
                    </span>
                ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="flex justify-center mt-12 fade-in">
        <button 
          onClick={handleContinue}
          disabled={selectedCourses.length === 0}
          className="boost-button flex items-center space-x-2 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>Продолжить ({selectedCourses.length} выбрано)</span>
          <ArrowRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  )
}

export default ExternalCourseSelection