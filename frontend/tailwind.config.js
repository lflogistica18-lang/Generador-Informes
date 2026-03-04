/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          900: '#263238',
          800: '#37474F',
          700: '#455A64',
          600: '#546E7A',
          500: '#607D8B',
          400: '#78909C',
          300: '#90A4AE',
          200: '#B0BEC5',
          100: '#CFD8DC',
          50: '#ECEFF1',
        },
        sanitas: {
          light: '#4DB6AC',
          DEFAULT: '#009688',
          dark: '#00796B',
        },
      },
    },
  },
  plugins: [],
}
