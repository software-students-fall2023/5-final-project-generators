/** @type {import('tailwindcss').Config} */

module.exports = {
    content: ["./templates/**/*.html"],
    theme: {
      extend: {
        colors: {
          primary: {
            50: '#90E0EF',
            100: '#00B4D8',
            200: '#0077B6',
            300: '#023E8A',
            400: '#03045E',
          },
          secondary: {
            100: '#F2CC8F',
            200: '#F0EBD8',
            800: '#333333',
          },
        },
  
        textColor: {
          primary: {
            50: '#90E0EF',
            100: '#00B4D8',
            200: '#0077B6',
            300: '#023E8A',
            400: '#03045E',
          },
          secondary: {
            100: '#F2CC8F',
            200: '#F0EBD8',
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