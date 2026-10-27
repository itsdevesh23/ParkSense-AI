/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0B1528',
          800: '#0F2042',
          700: '#1E3A8A',
          600: '#2563EB',
          50: '#F0F5FF',
        },
        slate: {
          850: '#152033',
        }
      }
    },
  },
  plugins: [],
}
