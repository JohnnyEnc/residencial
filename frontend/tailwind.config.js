/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        lagoon: {
          50: '#eef8f4',
          100: '#d5efe6',
          200: '#a9decd',
          300: '#6fc4ab',
          400: '#3ea388',
          500: '#25876e',
          600: '#1a6c59',
          700: '#165748',
          800: '#14463b',
          900: '#0f2f28',
          950: '#081c18',
        },
        // aliases so vistas existentes sigan compilando
        brand: {
          50: '#eef8f4',
          100: '#d5efe6',
          200: '#a9decd',
          300: '#6fc4ab',
          400: '#3ea388',
          500: '#25876e',
          600: '#1a6c59',
          700: '#165748',
          800: '#14463b',
          900: '#0f2f28',
        },
        ink: '#0c1f1b',
        paper: '#f5f7f2',
        mist: '#e7eee9',
        sand: '#f5f7f2',
        lime: '#c6f04d',
        ember: '#e4572e',
        coral: '#e4572e',
        dusk: '#1b3a34',
      },
      fontFamily: {
        display: ['"Syne"', 'Georgia', 'sans-serif'],
        sans: ['"Literata"', 'Georgia', 'serif'],
      },
      boxShadow: {
        lift: '0 18px 40px -24px rgba(8, 28, 24, 0.45)',
        insetline: 'inset 0 0 0 1px rgba(15, 47, 40, 0.08)',
      },
      keyframes: {
        rise: {
          '0%': { opacity: '0', transform: 'translateY(18px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        drift: {
          '0%, 100%': { transform: 'translate3d(0,0,0) scale(1)' },
          '50%': { transform: 'translate3d(2%, -1%, 0) scale(1.04)' },
        },
        sheen: {
          '0%': { backgroundPosition: '0% 50%' },
          '100%': { backgroundPosition: '100% 50%' },
        },
      },
      animation: {
        rise: 'rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) both',
        drift: 'drift 14s ease-in-out infinite',
        sheen: 'sheen 8s linear infinite',
      },
    },
  },
  plugins: [],
}
