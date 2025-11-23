import React, { createContext, useContext, useState, useMemo, useEffect } from 'react';
import { authAPI, specializationsAPI, minorsAPI } from '../api';

const SKILLS = [
  { id: 'dev', name: 'Web Development' },
  { id: 'data', name: 'Data Analysis' },
  { id: 'pm', name: 'Project Management' },
  { id: 'design', name: 'UX/UI Design' },
  { id: 'soft', name: 'Communication' },
  { id: 'finance', name: 'Financial Modeling' },
];

const SPECIALTIES = [
  { id: 'cs', name: 'Информационные системы', tags: ['IT', 'Dev', 'Logic'], targetSkills: { dev: 100, soft: 40, pm: 50, data: 70 } },
  { id: 'eco', name: 'Экономическая безопасность', tags: ['Finance', 'Law', 'Risk'], targetSkills: { finance: 90, data: 40, soft: 60 } },
  { id: 'design', name: 'Промышленный дизайн', tags: ['Art', 'Design', '3D'], targetSkills: { design: 100, soft: 70 } },
];

const MINORS = [
  {
    id: 'data_science',
    name: 'Майнер: Data Science',
    description: 'Глубокое погружение в методы машинного обучения и анализа больших данных.',
    tags: ['Data', 'IT', 'Algorithm', 'Углубление'],
    targetSkills: { dev: 20, data: 120, pm: 10, soft: 10 },
    courses: ['c_data1', 'c_data2', 'c_data3', 'c_soft1']
  },
  {
    id: 'product_manager',
    name: 'Майнер: Product Manager',
    description: 'Развитие навыков управления продуктом, от идеи до запуска.',
    tags: ['PM', 'Soft', 'Business', 'Смена области'],
    targetSkills: { pm: 110, soft: 80, design: 30, finance: 10 },
    courses: ['c_pm1', 'c_pm2', 'c_soft2']
  },
  {
    id: 'ux_design',
    name: 'Майнер: UX/UI Design',
    description: 'Переход в область дизайна пользовательских интерфейсов.',
    tags: ['Design', 'Art', 'Soft', 'Смена области'],
    targetSkills: { design: 130, soft: 60, dev: 10 },
    courses: ['c_design1', 'c_design2']
  }
];

const COURSES = [
  { id: 'c_base1', name: 'Введение в программирование', type: 'obligatory', semester: 1, credits: 6, skillsGained: [{ skillId: 'dev', level: 30 }] },
  { id: 'c_base2', name: 'Основы математики', type: 'obligatory', semester: 1, credits: 4, skillsGained: [{ skillId: 'data', level: 20 }] },
  { id: 'c_data1', name: 'Машинное обучение I', type: 'elective', semester: 3, credits: 5, skillsGained: [{ skillId: 'data', level: 40 }, { skillId: 'dev', level: 10 }] },
  { id: 'c_data2', name: 'Статистический анализ', type: 'elective', semester: 4, credits: 5, skillsGained: [{ skillId: 'data', level: 40 }] },
  { id: 'c_data3', name: 'Python для Data Science', type: 'elective', semester: 2, credits: 4, skillsGained: [{ skillId: 'data', level: 20 }] },
  { id: 'c_pm1', name: 'Гибкие методологии (Agile)', type: 'elective', semester: 3, credits: 3, skillsGained: [{ skillId: 'pm', level: 40 }, { skillId: 'soft', level: 20 }] },
  { id: 'c_pm2', name: 'Customer Development', type: 'elective', semester: 4, credits: 4, skillsGained: [{ skillId: 'pm', level: 40 }] },
  { id: 'c_soft1', name: 'Навыки презентации', type: 'elective', semester: 2, credits: 3, skillsGained: [{ skillId: 'soft', level: 30 }] },
  { id: 'c_soft2', name: 'Финансовая грамотность', type: 'elective', semester: 3, credits: 3, skillsGained: [{ skillId: 'finance', level: 20 }] },
  { id: 'c_design1', name: 'Основы проектирования интерфейсов', type: 'elective', semester: 4, credits: 5, skillsGained: [{ skillId: 'design', level: 50 }] },
  { id: 'c_design2', name: 'Исследование пользователей', type: 'elective', semester: 5, credits: 4, skillsGained: [{ skillId: 'design', level: 40 }, { skillId: 'soft', level: 10 }] },
];

const DataContext = createContext();

export const DataProvider = ({ children }) => {
  // Навигация и Аутентификация
  const [isUrFUStudent, setIsUrFUStudent] = useState(null);
  const [isLoadingUser, setIsLoadingUser] = useState(true);

  const [selectedSpecialtyId, setSelectedSpecialtyId] = useState(null);
  const [selectedMinorId, setSelectedMinorId] = useState(null); 
  
  // Пройденные курсы (включая обязательные и курсы из внешнего обучения)
  const [passedCourseIds, setPassedCourseIds] = useState([]); 
  
  // Выбранные элективы на будущие семестры
  const [selectedElectives, setSelectedElectives] = useState([]);
  
  // Загрузка данных пользователя при инициализации
  useEffect(() => {
    const loadUserData = async () => {
      const token = localStorage.getItem('access_token');
      const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
      
      // Если нет токена или не авторизован, сразу сбрасываем состояние
      if (!token || !isAuthenticated) {
        setIsUrFUStudent(false);
        setSelectedSpecialtyId(null);
        setSelectedMinorId(null);
        setIsLoadingUser(false);
        return;
      }
      
      // Если есть токен, пытаемся загрузить данные
      try {
        setIsLoadingUser(true);
        
        // Загружаем данные пользователя
        const userResponse = await authAPI.getMe();
        const userData = userResponse.data;
        
        setIsUrFUStudent(true);
        
        // Устанавливаем выбранную специальность
        if (userData.specialization_id) {
          setSelectedSpecialtyId(userData.specialization_id);
        } else {
          setSelectedSpecialtyId(null);
        }
        
        // Загружаем выбранный майнер
        if (userData.minor_ids && userData.minor_ids.length > 0) {
          try {
            const minorsHistoryResponse = await minorsAPI.getMyHistory();
            const selectedMinor = minorsHistoryResponse.data.find(
              (m) => m.status === 'selected'
            );
            
            if (selectedMinor) {
              setSelectedMinorId(selectedMinor.minor_id);
            } else {
              setSelectedMinorId(null);
            }
          } catch (err) {
            console.error('Ошибка загрузки майнеров:', err);
            setSelectedMinorId(null);
          }
        } else {
          setSelectedMinorId(null);
        }
      } catch (err) {
        console.error('Ошибка загрузки данных пользователя:', err);
        // Если токен невалидный, очищаем данные
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('isUrFUStudent');
        setIsUrFUStudent(false);
        setSelectedSpecialtyId(null);
        setSelectedMinorId(null);
      } finally {
        setIsLoadingUser(false);
      }
    };
    
    loadUserData();
  }, []); 

  // Выбранная основная специальность (используем ID из API, не моковые данные)
  const primarySpecialty = useMemo(() => {
    // Возвращаем объект с ID для совместимости, но данные будут загружаться из API
    return selectedSpecialtyId ? { id: selectedSpecialtyId, name: 'Загрузка...' } : null;
  }, [selectedSpecialtyId]);
  
  // Выбранный майнер (используем ID из API, не моковые данные)
  const selectedMinor = useMemo(() => {
    return selectedMinorId ? { id: selectedMinorId, name: 'Загрузка...' } : null;
  }, [selectedMinorId]);
  
  // Целевой профиль навыков для Орбиты (будет загружаться из API)
  const orbitTargetSkills = useMemo(() => {
    // Возвращаем пустой объект, данные будут загружаться из API орбиты
    return {};
  }, []);

  // =================================================================
  // 3. CORE LOGIC FUNCTIONS
  // =================================================================

  // Расчет текущих навыков (будет загружаться из API)
  const currentSkills = useMemo(() => {
    // Возвращаем пустой объект, данные будут загружаться из API навыков студента
    return {};
  }, []);

  // Расчет дефицита навыков (для рекомендаций курсов)
  const skillDeficit = useMemo(() => {
    const deficit = {};
    Object.entries(orbitTargetSkills).forEach(([skillId, target]) => {
      const current = currentSkills[skillId] || 0;
      const gap = target - current;
      if (gap > 0) {
        deficit[skillId] = gap;
      }
    });
    return deficit;
  }, [currentSkills, orbitTargetSkills]);

  // Получение рекомендованных курсов (из выбранного майнера)
  const getRecommendedCourses = () => {
    const deficitSkillIds = Object.keys(skillDeficit);
    
    // 1. Фильтруем курсы по майнеру и тем, что еще не пройдены
    let availableCourses = COURSES.filter(c => 
        selectedMinor.courses.includes(c.id) && !passedCourseIds.includes(c.id)
    );
    
    // 2. Сортируем по максимальному покрытию дефицитных навыков
    const scoredCourses = availableCourses.map(course => {
      let score = 0;
      course.skillsGained.forEach(gainedSkill => {
        if (deficitSkillIds.includes(gainedSkill.skillId)) {
          // Курс тем лучше, чем больше он закрывает дефицит
          score += gainedSkill.level * (skillDeficit[gainedSkill.skillId] / 100); 
        }
      });
      return { ...course, score };
    });
    
    // 3. Выбираем топ-5
    return scoredCourses
        .sort((a, b) => b.score - a.score)
        .slice(0, 5)
        .map(c => ({...c, skills: c.skillsGained.map(s => ({...s, name: SKILLS.find(sk => sk.id === s.skillId)?.name || s.skillId}))}));
  };

  // Генерация дорожной карты (обязательные курсы + выбранные элективы)
  const generateRoadmap = () => {
    const allCourses = COURSES.filter(c => 
      c.type === 'obligatory' || selectedElectives.includes(c.id) || passedCourseIds.includes(c.id)
    );
    
    const roadmap = Array.from({ length: 8 }, (_, i) => ({ semester: i + 1, courses: [] }));

    allCourses.forEach(course => {
      if (course.semester && course.semester <= 8) {
        roadmap[course.semester - 1].courses.push(course);
      }
    });

    return roadmap.map(semesterData => ({
      ...semesterData,
      courses: semesterData.courses.sort((a, b) => {
        if (a.type === 'obligatory' && b.type !== 'obligatory') return -1;
        if (a.type !== 'obligatory' && b.type === 'obligatory') return 1;
        return 0;
      }),
    }));
  };
  
  // Система рекомендаций майнеров (MVP: простое совпадение тегов)
  const getRecommendedMinors = () => {
    const userTags = primarySpecialty.tags;
    
    const scoredMinors = MINORS.map(minor => {
      let score = 0;
      
      // Считаем совпадение тегов
      minor.tags.forEach(minorTag => {
        if (userTags.includes(minorTag)) {
          score += 2; // Основные теги дают больше очков
        }
        if (minorTag === 'Углубление' && userTags.includes('IT')) {
             score += 1;
        }
        if (minorTag === 'Смена области' && !userTags.includes('Design')) {
             score += 1;
        }
      });
      
      // Дополнительный бонус за родственные навыки
      Object.entries(minor.targetSkills).forEach(([skillId, level]) => {
          if (primarySpecialty.targetSkills[skillId] > 0) {
              score += 0.5; // Небольшой бонус за родство
          }
      });
      
      return { ...minor, score };
    });
    
    return scoredMinors.sort((a, b) => b.score - a.score);
  };
  
  // Генерация Резюме Навыков
  const generateSkillResume = () => {
      const skillsList = Object.entries(currentSkills).map(([id, level]) => {
          const skillName = SKILLS.find(s => s.id === id)?.name || id;
          const target = orbitTargetSkills[id] || 0;
          return { id, name: skillName, level, target, isMinorSkill: selectedMinor.targetSkills[id] > 0 };
      }).filter(s => s.level > 0).sort((a, b) => b.level - a.level);
      
      const minorCourses = COURSES.filter(c => passedCourseIds.includes(c.id) && selectedMinor.courses.includes(c.id));
      const coreCourses = COURSES.filter(c => passedCourseIds.includes(c.id) && !selectedMinor.courses.includes(c.id));
      
      const coverage = calculateCoverage();

      return {
          studentName: 'Иванов Иван Иванович', // Мок-имя
          primarySpecialty: primarySpecialty.name,
          minor: selectedMinor.name,
          coverage: coverage,
          totalSkills: skillsList.length,
          skills: skillsList,
          minorCourses,
          coreCourses,
          date: new Date().toLocaleDateString('ru-RU'),
          isFull: coverage >= 95 
      };
  };

  // Расчет общего покрытия навыков
  const calculateCoverage = () => {
    let totalCoverage = 0;
    let maxPossible = 0;

    Object.entries(orbitTargetSkills).forEach(([skillId, required]) => {
      const current = currentSkills[skillId] || 0;
      totalCoverage += Math.min(current, required);
      maxPossible += required;
    });

    return maxPossible > 0 ? Math.round((totalCoverage / maxPossible) * 100) : 0;
  };
  
  // Функция для обновления выбора элективов
  const toggleCourseSelection = (courseId) => {
    setSelectedElectives(prev => 
      prev.includes(courseId)
        ? prev.filter(id => id !== courseId)
        : [...prev, courseId]
    );
  };
  
  // Установка основной специальности
  const setSpecialty = (id) => {
      console.log('setSpecialty called with id:', id);
      setSelectedSpecialtyId(id);
      // Не устанавливаем майнер автоматически - пользователь должен выбрать сам
  };
  
  // Установка майнера
  const setMinor = (id) => {
      setSelectedMinorId(id);
  };
  
  const value = {
    // Константы
    SKILLS,
    SPECIALTIES,
    MINORS,
    COURSES,
    // Состояние пользователя
    isUrFUStudent,
    setIsUrFUStudent,
    isLoadingUser,
    selectedSpecialtyId,
    setSelectedSpecialtyId,
    selectedMinorId,
    passedCourseIds,
    setPassedCourseIds,
    selectedElectives,
    // Основные сущности
    primarySpecialty,
    selectedMinor,
    // Данные для Орбиты
    orbitTargetSkills,
    currentSkills,
    skillDeficit,
    // Функции
    setSpecialty,
    setMinor,
    toggleCourseSelection,
    getRecommendedCourses,
    getRecommendedMinors,
    generateRoadmap,
    generateSkillResume,
    calculateCoverage
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

export const useData = () => useContext(DataContext);