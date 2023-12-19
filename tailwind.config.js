/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./web-app/src/templates/**/*.{html,htm}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#D8F3DC',
          100: '#B7E4C7',
          200: '#95D5B2',
          300: '#74C69D',
          400: '#52B788',
        },
        secondary: {
          100: '#DAD7CD',
          200: '#C2C5AA',
          800: '#333333',
        },
      },

      textColor: {
        primary: {
          50: '#D8F3DC',
          100: '#B7E4C7',
          200: '#95D5B2',
          300: '#74C69D',
          400: '#52B788',
        },
        secondary: {
          100: '#DAD7CD',
          200: '#C2C5AA',
          800: '#333333',
        },
      },

      fontFamily: {
        'head': ['DM Serif Display'],
        'body': ['Roboto']
      }
    },
  },
  variants: {},
  plugins: [],
}