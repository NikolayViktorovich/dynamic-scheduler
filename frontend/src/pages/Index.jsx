import React, { useState, useEffect, useCallback } from 'react';
import { 
    Target, 
    BookOpen, 
    TrendingUp, 
    Calendar, 
    Star, 
    Users, 
    Clock, 
    Filter, 
    AlertTriangle, 
    BookMarked, 
    User 
} from 'lucide-react';
import SkillRadar from '../components/SkillRadar';
import Roadmap from '../components/Roadmap';
import CourseCard from '../components/CourseCard';
import ResumeModal from '../components/ResumeModal';
import { useData } from '../context/DataContext';
import { orbitAPI, recommendationsAPI, resumeAPI, specializationsAPI, coursesAPI, authAPI } from '../api';
import { useNotifications } from '../context/NotificationContext';

const Dashboard = () => {
    const { 
        SKILLS, 
        primarySpecialty, 
        selectedMinorId,
    } = useData();

    const [isResumeModalOpen, setIsResumeModalOpen] = useState(false);
    const [currentResume, setCurrentResume] = useState(null);
    const [orbitData, setOrbitData] = useState(null);
    const [recommendedCourses, setRecommendedCourses] = useState([]);
    const [roadmap, setRoadmap] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [specializationId, setSpecializationId] = useState(null);
    const { showSuccess, showError: showNotificationError } = useNotifications();

    // Функция загрузки всех данных — вынесена отдельно, чтобы переиспользовать
    const fetchDashboardData = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);

            // 1. Профиль пользователя (для specialization_id)
            let userSpecializationId = null;
            try {
                const userResponse = await authAPI.getMe();
                userSpecializationId = userResponse.data.specialization_id;
                setSpecializationId(userSpecializationId);
            } catch (err) {
                console.error('Ошибка загрузки профиля:', err);
            }

            // 2. Орбита
            const orbitResponse = await orbitAPI.getMy();
            setOrbitData(orbitResponse.data);

            // 3. Рекомендованные курсы
            const recommendationsResponse = await recommendationsAPI.getCourses({ limit: 5 });
            setRecommendedCourses(recommendationsResponse.data.recommended_courses || []);

            // 4. Roadmap (если есть specialization_id)
            if (userSpecializationId && typeof userSpecializationId === 'number') {
                try {
                    const roadmapResponse = await specializationsAPI.getRoadmap(userSpecializationId);
                    const roadmapData = roadmapResponse.data;

                    const semestersArray = Object.entries(roadmapData.semesters || {})
                        .map(([semester, courses]) => ({
                            semester: parseInt(semester),
                            courses: courses.map(course => ({
                                id: course.id,
                                name: course.name,
                                semester: course.semester,
                                type: course.is_elective ? 'elective' : 'obligatory',
                                credits: course.credits
                            }))
                        }))
                        .sort((a, b) => a.semester - b.semester);

                    setRoadmap({
                        ...roadmapData,
                        semestersArray
                    });
                } catch (err) {
                    console.error('Ошибка загрузки roadmap:', err);
                    setRoadmap(null);
                }
            } else {
                setRoadmap(null);
            }

        } catch (err) {
            console.error('Ошибка загрузки данных Dashboard:', err);
            setError('Не удалось загрузить данные. Проверьте подключение к серверу.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Первичная загрузка
    useEffect(() => {
        fetchDashboardData();
    }, [fetchDashboardData]);

    // Обработчик генерации резюме
    const handleGenerateResume = async () => {
        try {
            const resumeResponse = await resumeAPI.getMy();
            setCurrentResume(resumeResponse.data);
            setIsResumeModalOpen(true);
        } catch (err) {
            console.error('Ошибка загрузки резюме:', err);
            showNotificationError('Не удалось загрузить резюме');
        }
    };

    // Главный обработчик записи на курс — обновляет ВСЁ сразу
    const handleCourseClick = async (course) => {
        try {
            await coursesAPI.enroll(course.course_id || course.id, { difficulty_level: 1 });
            showSuccess(`Вы записались на курс "${course.course_name || course.name}"`);

            // МГНОВЕННОЕ ОБНОВЛЕНИЕ всех данных
            await fetchDashboardData();

        } catch (err) {
            console.error('Ошибка записи на курс:', err);
            const errorMessage = err.response?.data?.detail 
                ? (Array.isArray(err.response.data.detail) 
                    ? err.response.data.detail.map(e => e.msg || e.message).join(', ')
                    : err.response.data.detail)
                : 'Не удалось записаться на курс';
            showNotificationError(errorMessage);
        }
    };

    // Вычисляемые данные
    const coverage = orbitData?.progress_percentage || 0;
    const targetSkills = orbitData?.target_skills || [];
    const relevantSkills = targetSkills.map(ts => ({
        id: ts.skill_id,
        name: ts.skill_name
    }));

    const circleSize = 180;
    const strokeWidth = 14;
    const radius = (circleSize - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference * (1 - coverage / 100);

    // Лоадеры и ошибки
    if (isLoading) {
        return (
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
                <div className="text-center py-12">
                    <div className="inline-block w-12 h-12 border-4 border-[#FF3B77] border-t-transparent rounded-full animate-spin"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Загрузка данных...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
                <div className="p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300">
                    {error}
                </div>
            </div>
        );
    }

    if (!orbitData) {
        return (
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
                <div className="text-center py-12">
                    <p className="text-gray-600 dark:text-gray-400">У вас не выбран майнор. Пожалуйста, выберите майнор в настройках профиля.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
            <div className="animate-fade-in">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white mb-2">
                    Ваша Орбита: <span className="gradient-text">{orbitData.minor_name}</span>
                </h1>
                <p className="text-base text-gray-600 dark:text-gray-400 mb-6">
                    Основной трек: <span className="font-semibold">{primarySpecialty?.name || 'Не выбрана'}</span>
                </p>
            </div>

            {/* Секция 1: Обзор Орбиты */}
            <section className="grid lg:grid-cols-3 gap-6 mb-8">
                <div className="bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-xl p-6 flex flex-col justify-between items-center text-center shadow-lg h-full">
                    <div className="flex flex-col items-center mb-6">
                        <Target className="h-8 w-8 mb-3 gradient-text" />
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white">Покрытие навыков</h3>
                    </div>

                    <div className="flex-grow flex items-center justify-center py-4">
                        <div className="relative" style={{ width: `${circleSize}px`, height: `${circleSize}px` }}>
                            <svg className="w-full h-full transform -rotate-90" viewBox={`0 0 ${circleSize} ${circleSize}`}>
                                <circle
                                    className="text-gray-200 dark:text-[#333333]"
                                    strokeWidth={strokeWidth}
                                    stroke="currentColor"
                                    fill="transparent"
                                    r={radius}
                                    cx={circleSize / 2}
                                    cy={circleSize / 2}
                                />
                                <circle
                                    className="text-[#FF3B77] transition-all duration-700 ease-out"
                                    strokeWidth={strokeWidth}
                                    strokeDasharray={circumference}
                                    strokeDashoffset={strokeDashoffset}
                                    strokeLinecap="round"
                                    stroke="currentColor"
                                    fill="transparent"
                                    r={radius}
                                    cx={circleSize / 2}
                                    cy={circleSize / 2}
                                />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <h3 className="text-4xl font-extrabold gradient-text">{coverage}%</h3>
                            </div>
                        </div>
                    </div>

                    <div className="w-full mt-6 pt-4 border-t border-gray-100 dark:border-[#333333]">
                        <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">
                            <span className="font-bold text-gray-900 dark:text-white">
                                {targetSkills.length}
                            </span> целевых навыков в Орбите
                        </p>
                        <p className="text-xs mt-2 text-gray-500 dark:text-gray-400">
                            Пройдено курсов: {orbitData.completed_courses} / {orbitData.total_courses}
                        </p>
                        {coverage >= 100 && (
                            <p className="text-xs mt-2 text-green-500 dark:text-green-400 flex items-center justify-center">
                                <Star className="h-4 w-4 mr-1 fill-current" />
                                Цель Орбиты достигнута!
                            </p>
                        )}
                    </div>
                </div>

                <div className="lg:col-span-2">
                    <SkillRadar 
                        skills={relevantSkills}
                        currentLevels={{}} // если у тебя есть актуальные уровни — передавай их сюда
                        targetLevels={targetSkills.reduce((acc, ts) => {
                            acc[ts.skill_id] = ts.required_level;
                            return acc;
                        }, {})}
                    />
                </div>
            </section>

            {/* Секция 2: Рекомендации и Резюме */}
            <section className="grid lg:grid-cols-12 gap-6 mb-8">
                <div className="lg:col-span-4 flex flex-col space-y-4">
                    <div className="bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-xl p-5 h-full flex flex-col justify-between shadow-lg">
                        <div>
                            <User className="h-6 w-6 mb-3 text-red-500" />
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                                Резюме навыков
                            </h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                                Генерируйте текущее резюме, основанное на вашей основной специальности и прогрессе по Орбите.
                            </p>
                        </div>
                        <button
                            onClick={handleGenerateResume}
                            className="mt-4 flex items-center justify-center text-sm py-2 px-4 rounded-lg font-semibold bg-red-500 text-white hover:bg-red-600 transition-colors shadow-md"
                        >
                            Сгенерировать резюме
                        </button>
                    </div>

                    <div className="bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-xl p-5 shadow-lg">
                        <div className='flex items-center'>
                            <BookOpen className="h-6 w-6 mr-3 text-[#7E3BF2]" />
                            <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                                Учебный план
                            </h3>
                        </div>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                            Основная специальность: <span className='font-semibold'>{primarySpecialty?.name || 'Не выбрана'}</span>
                        </p>
                    </div>
                </div>

                <div className="lg:col-span-8">
                    <div className="p-5 bg-white dark:bg-[#111111] border border-gray-200 dark:border-[#333333] rounded-xl h-full shadow-lg">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center">
                            <BookOpen className="h-5 w-5 mr-2 text-red-500" /> Рекомендованные курсы
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                            Курсы для закрытия дефицита навыков
                        </p>

                        <div className="space-y-4">
                            {recommendedCourses.length > 0 ? (
                                recommendedCourses.map(course => (
                                    <CourseCard 
                                        key={course.course_id} 
                                        course={{
                                            id: course.course_id,
                                            name: course.course_name,
                                            description: course.reason,
                                            missingSkills: course.missing_skills
                                        }} 
                                        isSelected={false}
                                        onSelect={() => handleCourseClick(course)}
                                    />
                                ))
                            ) : (
                                <div className="text-center py-6 text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-[#1A1A1A] rounded-lg border border-dashed border-gray-300 dark:border-[#333333]">
                                    <p className="font-semibold">Отличная работа!</p>
                                    <p className="text-sm">Покрытие навыков достаточно высокое. Дефицит отсутствует.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </section>

            {/* Roadmap */}
            {roadmap && roadmap.semestersArray && (
                <section className="mb-8">
                    <Roadmap 
                        roadmapData={roadmap.semestersArray} 
                        onCourseClick={handleCourseClick}
                    />
                </section>
            )}

            {isResumeModalOpen && <ResumeModal resumeData={currentResume} onClose={() => setIsResumeModalOpen(false)} />}
        </div>
    );
};

export default Dashboard;