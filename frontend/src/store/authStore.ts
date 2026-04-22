import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AuthService } from '../api/generated/services/AuthService';
import { UsersService } from '../api/generated/services/UsersService';
import type { UserPublic } from '../api/generated/models/UserPublic';
import type { UserLogin } from '../api/generated/models/UserLogin';
import type { UserRegister } from '../api/generated/models/UserRegister';
import { saveTokens, clearTokens, getStoredToken } from '../api/client';

interface AuthState {
  user: UserPublic | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (credentials: UserLogin) => Promise<void>;
  register: (data: UserRegister) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: UserLogin) => {
        set({ isLoading: true, error: null });
        try {
          const response = await AuthService.loginApiV1AuthLoginPost(credentials);
          saveTokens(response.access_token, response.refresh_token);
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error: any) {
          const errorMessage = error?.body?.detail || 'Ошибка входа';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      register: async (data: UserRegister) => {
        set({ isLoading: true, error: null });
        try {
          const response = await AuthService.registerApiV1AuthRegisterPost(data);
          saveTokens(response.access_token, response.refresh_token);
          set({
            user: response.user,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error: any) {
          const errorMessage = error?.body?.detail || 'Ошибка регистрации';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            await AuthService.logoutApiV1AuthLogoutPost({ refresh_token: refreshToken });
          }
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          clearTokens();
          set({ user: null, isAuthenticated: false });
        }
      },

      checkAuth: async () => {
        const token = getStoredToken();
        if (!token) {
          clearTokens();
          set({ isAuthenticated: false, user: null });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await UsersService.getMeApiV1UsersMeGet();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error: any) {
          if (error?.status === 401) {
            clearTokens();
            set({ user: null, isAuthenticated: false, isLoading: false });
          } else {
            console.error('Auth check failed:', error);
            set({ isLoading: false });
          }
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
      }),
    }
  )
);
