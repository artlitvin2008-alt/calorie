/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // iOS-style colors
        primary: {
          DEFAULT: '#007AFF',
          dark: '#0A84FF',
        },
        secondary: {
          DEFAULT: '#5856D6',
          dark: '#5E5CE6',
        },
        success: {
          DEFAULT: '#34C759',
          dark: '#30D158',
        },
        warning: {
          DEFAULT: '#FF9500',
          dark: '#FF9F0A',
        },
        danger: {
          DEFAULT: '#FF3B30',
          dark: '#FF453A',
        },
        background: {
          light: '#F2F2F7',
          dark: '#000000',
        },
        surface: {
          light: '#FFFFFF',
          dark: '#1C1C1E',
        },
        text: {
          primary: {
            light: '#000000',
            dark: '#FFFFFF',
          },
          secondary: {
            light: '#3C3C43',
            dark: '#EBEBF5',
          },
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Text', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'ios': '10px',
        'ios-lg': '14px',
      },
      boxShadow: {
        'ios': '0 2px 8px rgba(0, 0, 0, 0.1)',
        'ios-lg': '0 4px 16px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
