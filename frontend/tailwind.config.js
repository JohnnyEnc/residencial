/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef7f4',
          100: '#d5ebe3',
          200: '#aad7c7',
          300: '#76bba7',
          400: '#4a9a86',
          500: '#317e6c',
          600: '#266557',
          700: '#215247',
          800: '#1d423a',
          900: '#193731',
        },
        ink: '#14231f',
        sand: '#f3efe6',
        coral: '#c45c3e',
      },
      fontFamily: {
        display: ['"Fraunces"', 'Georgia', 'serif'],
        sans: ['"Source Sans 3"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 10px 30px -12px rgba(20, 35, 31, 0.25)',
      },
    },
  },
  plugins: [],
}
