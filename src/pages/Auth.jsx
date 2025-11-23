import React, { useState } from 'react'
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, SkipForward } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useData } from '../context/DataContext'
import { authAPI } from '../api'

// --- НОВЫЙ КОМПОНЕНТ ДЛЯ СПИННЕРА ---
const LoadingSpinner = () => (
  <svg 
    className="animate-spin -ml-1 mr-3 h-5 w-5" 
    xmlns="http://www.w3.org/2000/svg" 
    fill="none" 
    viewBox="0 0 24 24"
  >
    <circle 
      className="opacity-25" 
      cx="12" 
      cy="12" 
      r="10" 
      stroke="currentColor" 
      strokeWidth="4"
    ></circle>
    <path 
      className="opacity-75" 
      fill="url(#gradient)" 
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    ></path>
    <defs>
      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style={{stopColor: '#FF3B77', stopOpacity: 1}} />
        <stop offset="100%" style={{stopColor: '#7E3BF2', stopOpacity: 1}} />
      </linearGradient>
    </defs>
  </svg>
);
// --- КОНЕЦ НОВОГО КОМПОНЕНТА ---


const Auth = () => {
  const navigate = useNavigate()
  const { setIsUrFUStudent } = useData()

  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  })
  
  const handleRegister = async () => {
    setIsLoading(true)
    setError('')

    try {
      const response = await authAPI.register({
        email: formData.email,
        full_name: formData.name,
        password: formData.password
      })

      const { access_token, refresh_token } = response.data
      
      // Сохраняем токены
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      
      setIsUrFUStudent(true)
      localStorage.setItem('isUrFUStudent', 'true')
      localStorage.setItem('isAuthenticated', 'true')
      
      // Проверяем, есть ли уже выбранная специальность
      try {
        const userResponse = await authAPI.getMe();
        if (userResponse.data.specialization_id) {
          // Если есть специальность, проверяем майнер
          if (userResponse.data.minor_ids && userResponse.data.minor_ids.length > 0) {
            navigate('/dashboard');
          } else {
            navigate('/onboarding/minor');
          }
        } else {
          navigate('/onboarding/specialty');
        }
      } catch (err) {
        navigate('/onboarding/specialty');
      }

    } catch (error) {
      console.error('Ошибка регистрации:', error)
      const errorMessage = error.response?.data?.detail 
        ? (Array.isArray(error.response.data.detail) 
            ? error.response.data.detail.map(e => e.msg).join(', ')
            : error.response.data.detail)
        : error.message || 'Произошла ошибка при регистрации'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogin = async () => {
    setIsLoading(true)
    setError('')

    try {
      const response = await authAPI.login({
        email: formData.email,
        password: formData.password
      })

      const { access_token, refresh_token } = response.data
      
      // Сохраняем токены
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      
      setIsUrFUStudent(true)
      localStorage.setItem('isUrFUStudent', 'true')
      localStorage.setItem('isAuthenticated', 'true')
      
      // Проверяем, есть ли уже выбранная специальность
      try {
        const userResponse = await authAPI.getMe();
        if (userResponse.data.specialization_id) {
          // Если есть специальность, проверяем майнер
          if (userResponse.data.minor_ids && userResponse.data.minor_ids.length > 0) {
            navigate('/dashboard');
          } else {
            navigate('/onboarding/minor');
          }
        } else {
          navigate('/onboarding/specialty');
        }
      } catch (err) {
        navigate('/onboarding/specialty');
      }

    } catch (error) {
      console.error('Ошибка входа:', error)
      const errorMessage = error.response?.data?.detail 
        ? (Array.isArray(error.response.data.detail) 
            ? error.response.data.detail.map(e => e.msg).join(', ')
            : error.response.data.detail)
        : error.message || 'Неверный email или пароль'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAuthSubmit = async (e) => {
    e.preventDefault()
    
    if (isLogin) {
      await handleLogin()
    } else {
      await handleRegister()
    }
  }

  // --- ФУНКЦИЯ handleSkip УДАЛЕНА ---

  const toggleMode = () => {
    setIsLogin(!isLogin)
    setFormData({ name: '', email: '', password: '' })
    setError('')
  }

  return (
    <div className="min-h-[calc(100vh-64px)] relative flex items-center justify-center p-4 overflow-hidden">
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-[#FF3B77]/20 blur-[100px] animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-[#7E3BF2]/20 blur-[100px] animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 w-full max-w-md bg-white/70 dark:bg-[#111]/70 backdrop-blur-xl border border-white/20 dark:border-white/10 shadow-2xl rounded-3xl p-8 transition-all duration-300">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#FF3B77] to-[#7E3BF2] mb-2">
            {isLogin ? 'Вход' : 'Регистрация'}
          </h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            Используйте email и пароль
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-300 text-sm">
            {error}
          </div>
        )}

        <form className="space-y-5" onSubmit={handleAuthSubmit}>
          {!isLogin && (
            <div className="space-y-1">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300 ml-1">Имя</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400 group-focus-within:text-[#FF3B77] transition-colors" />
                </div>
                <input
                  type="text"
                  placeholder="Иван Петров"
                  className="block w-full pl-10 pr-3 py-3 border border-gray-200 dark:border-[#333] rounded-xl bg-gray-50/50 dark:bg-[#1A1A1A]/50 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#FF3B77]/20 focus:border-[#FF3B77] transition-all"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required={!isLogin}
                  disabled={isLoading}
                />
              </div>
            </div>
          )}
          <div className="space-y-1">
            <label className="text-xs font-medium text-gray-700 dark:text-gray-300 ml-1">Email</label>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-gray-400 group-focus-within:text-[#7E3BF2] transition-colors" />
              </div>
              <input
                type="email"
                placeholder="student@urfu.ru"
                className="block w-full pl-10 pr-3 py-3 border border-gray-200 dark:border-[#333] rounded-xl bg-gray-50/50 dark:bg-[#1A1A1A]/50 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#7E3BF2]/20 focus:border-[#7E3BF2] transition-all"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
                disabled={isLoading}
              />
            </div>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium text-gray-700 dark:text-gray-300 ml-1">Пароль</label>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-[#7E3BF2] transition-colors" />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                className="block w-full pl-10 pr-10 py-3 border border-gray-200 dark:border-[#333] rounded-xl bg-gray-50/50 dark:bg-[#1A1A1A]/50 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#7E3BF2]/20 focus:border-[#7E3BF2] transition-all"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
                disabled={isLoading}
                minLength={6}
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" />
                )}
              </button>
            </div>
          </div>

          {isLogin && (
            <div className="flex justify-end">
              <a href="#" className="text-xs font-medium text-[#7E3BF2] hover:text-[#FF3B77] transition-colors">
                Забыли пароль?
              </a>
            </div>
          )}

          <button 
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-[#FF3B77] to-[#7E3BF2] text-white font-bold py-3.5 px-4 rounded-xl shadow-lg shadow-[#7E3BF2]/25 hover:shadow-[#FF3B77]/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 flex items-center justify-center group disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {/* ИСПОЛЬЗУЕМ НОВЫЙ КОМПОНЕНТ LoadingSpinner */}
            {isLoading ? (
              <div className="flex items-center">
                <LoadingSpinner />
                <span>Загрузка...</span>
              </div>
            ) : (
              <>
                <span>{isLogin ? 'Войти' : 'Зарегистрироваться'}</span>
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </form>
        {/* БЛОК С КНОПКОЙ ПРОПУСКА УДАЛЕН */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-[#333]">
        {/* ПУСТОЙ DIV ОСТАВЛЕН, ЧТОБЫ СОХРАНИТЬ РАЗДЕЛИТЕЛЬНУЮ ЛИНИЮ */}
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {isLogin ? 'Еще нет аккаунта?' : 'Уже есть аккаунт?'}
            <button 
              onClick={toggleMode}
              disabled={isLoading}
              className="ml-1 font-semibold text-[#FF3B77] hover:text-[#7E3BF2] transition-colors disabled:opacity-50"
            >
              {isLogin ? 'Зарегистрироваться' : 'Войти'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Auth