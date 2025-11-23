import React, { useRef, useState, useEffect, useCallback } from 'react'; 
import { Briefcase, Target, BookOpen, Clock, User, CheckCircle2, TrendingUp, Download, X } from 'lucide-react'; 

const ResumeModal = ({ resumeData, onClose }) => {
    // 1. Новое состояние для управления анимацией
    const [showModal, setShowModal] = useState(false);

    // 2. useEffect для запуска анимации открытия/закрытия
    useEffect(() => {
        if (resumeData) { // Модальное окно считается открытым, если есть resumeData
            setTimeout(() => setShowModal(true), 10);
        } else {
            setShowModal(false);
        }
    }, [resumeData]);

    const resumeRef = useRef(null);

    // Если resumeData нет и анимация закрытия завершена, не рендерим ничего
    if (!resumeData && !showModal) return null;

    const { 
        studentName, 
        primarySpecialty, 
        minor, 
        coverage, 
        skills, 
        minorCourses, 
        coreCourses, 
        date,
        isFull
    } = resumeData || {}; // Добавим деструктуризацию с пустым объектом, если resumeData еще нет

    // *** КЛЮЧЕВОЙ ФИКС: Используем || [] для обеспечения того, что переменные являются массивами ***
    const safeSkills = skills || [];
    const safeMinorCourses = minorCourses || [];
    const safeCoreCourses = coreCourses || [];
    // ******************************************************************************************

    const status = isFull 
        ? { icon: CheckCircle2, color: 'text-green-500', label: 'Полное покрытие' }
        : { icon: TrendingUp, color: 'text-blue-500', label: 'В разработке' };
    
    const handlePrintPDF = () => {
        const modalContainer = resumeRef.current.closest('.fixed');
        if (modalContainer) {
            modalContainer.classList.add('print-mode');
        }
        
        window.print();
        if (modalContainer) {
            modalContainer.classList.remove('print-mode');
        }
    };

    // Обновленная функция onClose для обработки анимации
    const handleClose = useCallback(() => {
        setShowModal(false);
        setTimeout(onClose, 300); // 300ms - длительность анимации
    }, [onClose]);
    
    return (
        // 3. Анимация для фона
        <div 
            className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity duration-300 ${
                showModal ? 'opacity-100' : 'opacity-0'
            }`}
            onClick={handleClose} // Закрытие по клику вне модального окна
        >
            <div 
                // 4. Анимация для содержимого модального окна
                className={`bg-white dark:bg-[#111111] rounded-3xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl transition-all duration-300 ${
                    showModal ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-4'
                } p-8 md:p-10`}
                onClick={e => e.stopPropagation()} // Предотвращаем закрытие при клике внутри модального окна
            >
                <div className="flex justify-between items-center border-b pb-4 mb-6 border-gray-200 dark:border-[#222] print:hidden">
                    <h2 className="text-3xl font-extrabold gradient-text">Резюме навыков</h2>
                    <div className='flex items-center space-x-3'>
                        
                        <button 
                            onClick={handlePrintPDF}
                            className="flex items-center space-x-2 px-4 py-2 bg-dark text-white rounded-lg text-sm font-semibold transition-colors shadow-md"
                        >
                            <Download className="h-4 w-4" />
                            <span>Скачать PDF</span>
                        </button>
                        
                        <button 
                            onClick={handleClose}
                            className="p-2 rounded-full text-gray-500 hover:text-[#FF3B77] hover:bg-gray-100 dark:hover:bg-[#1A1A1A] transition-colors"
                        >
                            <X className="h-5 w-5" /> {/* Иконка X вместо символа &times; */}
                        </button>
                    </div>
                </div>
                <div ref={resumeRef} className="print:p-0 print:m-0">
                    <div className="hidden print:block mb-6">
                         <h2 className="text-3xl font-extrabold text-gray-900 dark:text-white">Резюме навыков</h2>
                         <p className="text-sm text-gray-500 mt-1">
                            {date} | Сгенерировано на основе: {primarySpecialty} и {minor}
                         </p>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 mb-6 print:hidden">
                        {date} | Сгенерировано на основе: {primarySpecialty} и {minor}
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 print:grid-cols-3 print:gap-4">
                        <div className="col-span-1 p-4 bg-gray-50 dark:bg-[#1A1A1A] rounded-xl flex flex-col justify-center print:bg-gray-100 print:p-3 print:border">
                            <div className="flex items-center text-sm font-semibold text-gray-500 dark:text-gray-400 mb-1">
                                <User className="h-4 w-4 mr-2" /> Студент
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">{studentName}</p>
                        </div>
                        <div className="col-span-1 p-4 bg-gray-50 dark:bg-[#1A1A1A] rounded-xl print:bg-gray-100 print:p-3 print:border">
                            <div className="flex items-center text-sm font-semibold text-gray-500 dark:text-gray-400 mb-1">
                                <Briefcase className="h-4 w-4 mr-2" /> Основная Специальность
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">{primarySpecialty}</p>
                        </div>
                        <div className="col-span-1 p-4 bg-gray-50 dark:bg-[#1A1A1A] rounded-xl print:bg-gray-100 print:p-3 print:border">
                            <div className="flex items-center text-sm font-semibold text-gray-500 dark:text-gray-400 mb-1">
                                <Target className="h-4 w-4 mr-2" /> Майнер (Орбита)
                            </div>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">{minor}</p>
                        </div>
                    </div>

                    {/* Навыки */}
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center print:text-lg print:border-b print:pb-1">
                        <TrendingUp className="h-5 w-5 mr-2 text-[#FF3B77] print:h-4 print:w-4 print:text-black" /> Навыки и Компетенции
                        <span className={`ml-4 text-sm font-medium px-3 py-1 rounded-full ${status.color} bg-opacity-10 dark:bg-opacity-20 flex items-center print:bg-transparent print:text-black print:p-0 print:ml-2`}>
                            <status.icon className="h-4 w-4 mr-1 print:h-3 print:w-3 print:text-black" />
                            Покрытие: {coverage}% ({status.label})
                        </span>
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-8 print:grid-cols-3 print:gap-2">
                        {/* ФИКС: Используем safeSkills */}
                        {safeSkills.map(skill => (
                            <div key={skill.id} className="p-3 bg-white dark:bg-[#1A1A1A] border border-gray-200 dark:border-[#333] rounded-lg print:p-2 print:border print:shadow-none">
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200 print:text-xs print:font-semibold">{skill.name}</span>
                                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                                        skill.isMinorSkill ? 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300' : 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300'
                                    } print:bg-gray-300 print:text-gray-900 print:px-1 print:py-0`}>
                                        Ур. {skill.level}
                                    </span>
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400 print:text-[10px] print:text-gray-600">
                                    {skill.isMinorSkill ? 'Усиление Майнера' : 'Базовый профиль'}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Курсы */}
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center print:text-lg print:border-b print:pb-1">
                        <BookOpen className="h-5 w-5 mr-2 text-[#7E3BF2] print:h-4 print:w-4 print:text-black" /> Пройденные Курсы
                    </h3>
                    
                    <div className="space-y-4 print:space-y-2">
                        {/* Курсы Майнера */}
                        <div className="p-4 rounded-xl border border-purple-300/50 dark:border-purple-700/50 bg-purple-50/20 dark:bg-purple-900/10 print:p-2 print:border print:border-purple-300">
                            <p className="font-bold text-purple-700 dark:text-purple-300 mb-2 print:text-sm print:text-black print:font-semibold">{minor} (Доп. трек):</p>
                            <div className="flex flex-wrap gap-2">
                                {/* ФИКС: Используем safeMinorCourses */}
                                {safeMinorCourses.map(course => (
                                    <span key={course.id} className="px-3 py-1 text-sm rounded-full bg-purple-200 dark:bg-purple-700 text-purple-900 dark:text-white flex items-center print:bg-purple-100 print:text-purple-900 print:text-xs">
                                        <Clock className="h-3 w-3 mr-1" /> {course.name}
                                    </span>
                                ))}
                            </div>
                        </div>
                        
                        {/* Курсы Основной Специальности */}
                        <div className="p-4 rounded-xl border border-blue-300/50 dark:border-blue-700/50 bg-blue-50/20 dark:bg-blue-900/10 print:p-2 print:border print:border-blue-300">
                            <p className="font-bold text-blue-700 dark:text-blue-300 mb-2 print:text-sm print:text-black print:font-semibold">{primarySpecialty} (База):</p>
                            <div className="flex flex-wrap gap-2">
                                {/* ФИКС: Используем safeCoreCourses */}
                                {safeCoreCourses.map(course => (
                                    <span key={course.id} className="px-3 py-1 text-sm rounded-full bg-blue-200 dark:bg-blue-700 text-blue-900 dark:text-white flex items-center print:bg-blue-100 print:text-blue-900 print:text-xs">
                                        <Clock className="h-3 w-3 mr-1" /> {course.name}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResumeModal;