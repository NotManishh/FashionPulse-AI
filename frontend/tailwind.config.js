/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0b0d11",
        surface: "#12161f",
        surfaceHover: "#181e2b",
        border: "#202838",
        accent: {
          gold: "#e6c687",
          amber: "#f59e0b",
          emerald: "#10b981",
          violet: "#8b5cf6",
          rose: "#f43f5e"
        }
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        serif: ['"Playfair Display"', 'Georgia', 'serif']
      }
    },
  },
  plugins: [],
}
