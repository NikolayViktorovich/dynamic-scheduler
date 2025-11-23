import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Создаем экземпляр axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерцептор для добавления токена к запросам
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Интерцептор для обработки ошибок и обновления токена
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Если получили 401 и это не запрос на обновление токена
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          })

          const { access_token, refresh_token: newRefreshToken } = response.data
          localStorage.setItem('access_token', access_token)
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken)
          }

          // Повторяем оригинальный запрос с новым токеном
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Если обновление токена не удалось, очищаем хранилище и перенаправляем на страницу входа
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('isAuthenticated')
        window.location.href = '/onboarding/auth'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// ============================================
// AUTH API
// ============================================
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  refresh: (data) => api.post('/api/auth/refresh', data),
  getMe: () => api.get('/api/auth/me'),
  changePassword: (data) => api.post('/api/auth/change-password', data),
}

// ============================================
// SPECIALIZATIONS API
// ============================================
export const specializationsAPI = {
  getAll: () => api.get('/api/specializations/'),
  create: (data) => api.post('/api/specializations/', data),
  getById: (id) => api.get(`/api/specializations/${id}`),
  getRoadmap: (id) => api.get(`/api/specializations/${id}/roadmap`),
  getSkillsMatrix: (id) => api.get(`/api/specializations/${id}/skills-matrix`),
}

// ============================================
// COURSES API
// ============================================
export const coursesAPI = {
  getAll: (params) => api.get('/api/courses/', { params }),
  getMy: () => api.get('/api/courses/my'),
  getById: (id) => api.get(`/api/courses/${id}`),
  getSkills: (id) => api.get(`/api/courses/${id}/skills`),
  enroll: (id, data) => api.post(`/api/courses/${id}/enroll`, data),
  complete: (id, data) => api.put(`/api/courses/${id}/complete`, data),
}

// ============================================
// SKILLS API
// ============================================
export const skillsAPI = {
  getAll: () => api.get('/api/skills/'),
  getTree: () => api.get('/api/skills/tree'),
  getMy: () => api.get('/api/skills/my-skills'),
  getGapAnalysis: (params) => api.get('/api/skills/gap-analysis', { params }),
}

// ============================================
// STUDENTS API
// ============================================
export const studentsAPI = {
  getProfile: () => api.get('/api/students/me/profile'),
  updateProfile: (data) => api.put('/api/students/me/profile', data),
  setSpecialization: (specializationId) => api.put('/api/students/me/specialization', null, {
    params: { specialization_id: specializationId }
  }),
  getCourses: () => api.get('/api/students/me/courses'),
  getProgress: () => api.get('/api/students/me/progress'),
  getResume: () => api.get('/api/students/me/resume'),
}

// ============================================
// RECOMMENDATIONS API
// ============================================
export const recommendationsAPI = {
  getCourses: (params) => api.get('/api/recommendations/courses', { params }),
  whatIf: (data) => api.post('/api/recommendations/what-if', data),
}

// ============================================
// MINORS API
// ============================================
export const minorsAPI = {
  getAll: (params) => api.get('/api/minors/', { params }),
  getById: (id) => api.get(`/api/minors/${id}`),
  getRecommendations: (params) => api.get('/api/minors/recommendations/for-me', { params }),
  getSimilar: (params) => api.get('/api/minors/recommendations/similar', { params }),
  select: (data) => api.post('/api/minors/select', data),
  complete: (id) => api.post(`/api/minors/${id}/complete`),
  getMyHistory: () => api.get('/api/minors/my/history'),
}

// ============================================
// ORBIT API
// ============================================
export const orbitAPI = {
  getMy: () => api.get('/api/orbit/'),
}

// ============================================
// RESUME API
// ============================================
export const resumeAPI = {
  getMy: () => api.get('/api/resume/'),
}

// ============================================
// LEGACY API (для обратной совместимости)
// ============================================
export const studentAPI = {
  getProfile: () => studentsAPI.getProfile(),
  getSkills: () => skillsAPI.getMy(),
  getCourses: () => coursesAPI.getAll(),
  updateCourseSelection: (data) => coursesAPI.enroll(data.courseId, data),
  simulateSpecialty: (specialtyId) => recommendationsAPI.whatIf({ new_specialization_id: specialtyId }),
}

export default api
