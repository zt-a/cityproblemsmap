import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary colors
        primary: {
          DEFAULT: '#3B82F6',
          hover: '#60A5FA',
          dark: '#2563EB',
        },
        accent: {
          DEFAULT: '#2563EB',
          hover: '#3B82F6',
        },

        // Dark theme backgrounds
        dark: {
          bg: '#0B1220',
          card: '#111827',
          hover: '#1F2937',
          input: '#1F2937',
        },

        // Text colors
        text: {
          primary: '#E5E7EB',
          secondary: '#9CA3AF',
          muted: '#6B7280',
        },

        // Semantic colors
        success: '#10B981',
        warning: '#F59E0B',
        danger: '#EF4444',
        info: '#3B82F6',

        // Border colors
        border: {
          DEFAULT: '#374151',
          hover: '#4B5563',
          focus: '#3B82F6',
        },

        // Status colors (для проблем)
        status: {
          pending: '#EF4444',
          'in-progress': '#F59E0B',
          resolved: '#10B981',
          rejected: '#6B7280',
        },
      },

      borderRadius: {
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '20px',
        '2xl': '24px',
      },

      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.3)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.4)',
        'lg': '0 10px 15px rgba(0, 0, 0, 0.5)',
        'xl': '0 20px 25px rgba(0, 0, 0, 0.6)',
        'glow': '0 0 0 2px rgba(59, 130, 246, 0.5)',
      },

      backdropBlur: {
        'glass': '12px',
      },

      transitionDuration: {
        'fast': '200ms',
      },

      spacing: {
        'sidebar': '88px',
        'problem-list': '420px',
      },
    },
  },
  plugins: [],
} satisfies Config
