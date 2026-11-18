/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./apps/**/forms.py",
    "./static/js/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          navy: "#313338",
          primary: "#5865F2",
          crystal: "#4752C4",
          surface: "#F2F3F5",
          white: "#FFFFFF"
        }
      }
    }
  },
  plugins: []
}
