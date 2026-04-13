import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const Register = () => {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    city: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationError, setValidationError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    setValidationError('');
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError('');
    clearError();

    if (formData.password !== formData.confirmPassword) {
      setValidationError('Пароли не совпадают');
      return;
    }

    if (formData.password.length < 6) {
      setValidationError('Пароль должен быть не менее 6 символов');
      return;
    }

    setIsSubmitting(true);

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        city: formData.city || null,
      });
      navigate('/', { replace: true });
    } catch (err) {
      // Error handled in store
    } finally {
      setIsSubmitting(false);
    }
  };

  const displayError = validationError || error;

  return (
    <div className="min-h-screen bg-[#0B1220] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-[#9CA3AF] hover:text-[#E5E7EB] mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Назад
        </button>
        <div className="bg-[#111827] rounded-xl p-8 shadow-xl">
          <h1 className="text-3xl font-bold text-[#E5E7EB] mb-2">Регистрация</h1>
          <p className="text-[#9CA3AF] mb-6">Создайте новый аккаунт</p>

          {displayError && (
            <div className="bg-[#EF4444]/10 border border-[#EF4444] text-[#EF4444] px-4 py-3 rounded-lg mb-4">
              {displayError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-[#E5E7EB] mb-2">
                Имя пользователя
              </label>
              <input
                id="username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] placeholder-[#6B7280] focus:outline-none focus:border-[#3B82F6] transition-colors"
                placeholder="username"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-[#E5E7EB] mb-2">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] placeholder-[#6B7280] focus:outline-none focus:border-[#3B82F6] transition-colors"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label htmlFor="city" className="block text-sm font-medium text-[#E5E7EB] mb-2">
                Город (опционально)
              </label>
              <input
                id="city"
                name="city"
                type="text"
                value={formData.city}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] placeholder-[#6B7280] focus:outline-none focus:border-[#3B82F6] transition-colors"
                placeholder="Бишкек"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-[#E5E7EB] mb-2">
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] placeholder-[#6B7280] focus:outline-none focus:border-[#3B82F6] transition-colors"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-[#E5E7EB] mb-2">
                Подтвердите пароль
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] placeholder-[#6B7280] focus:outline-none focus:border-[#3B82F6] transition-colors"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-[#3B82F6] hover:bg-[#2563EB] disabled:bg-[#374151] text-white font-medium py-3 rounded-lg transition-colors"
            >
              {isSubmitting ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-[#9CA3AF]">
              Уже есть аккаунт?{' '}
              <Link to="/login" className="text-[#3B82F6] hover:text-[#60A5FA] transition-colors">
                Войти
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
