import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, error, clearError } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = (location.state as any)?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setIsSubmitting(true);

    try {
      await login({ email, password });
      navigate(from, { replace: true });
    } catch (err) {
      // Error handled in store
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B1220] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-[#9CA3AF] hover:text-[#E5E7EB] mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Назад
        </button>
        <div className="bg-[#111827] rounded-xl p-8 shadow-xl">
          <h1 className="text-3xl font-bold text-[#E5E7EB] mb-2">Вход</h1>
          <p className="text-[#9CA3AF] mb-6">Войдите в свой аккаунт</p>

          {error && (
            <div className="bg-[#EF4444]/10 border border-[#EF4444] text-[#EF4444] px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-[#E5E7EB] mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] placeholder-[#6B7280] focus:outline-none focus:border-[#3B82F6] transition-colors"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-[#E5E7EB] mb-2">
                Пароль
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
              {isSubmitting ? 'Вход...' : 'Войти'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-[#9CA3AF]">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-[#3B82F6] hover:text-[#60A5FA] transition-colors">
                Зарегистрироваться
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
