/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './lib/**/*.{js,ts,jsx,tsx}',
    './pages/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        ink: '#241D20',
        muted: '#6E6468',
        paper: '#F6F2EA',
        paper2: '#FBF8F3',
        plum: '#6E1D4C',
        plumDeep: '#4C1234',
        rose: '#C89AAE',
        roseBright: '#EF779F',
        sage: '#6B8E23',
        sageDark: '#5A721C',
        line: 'rgba(76, 18, 52, .14)',
        white: '#FFFFFF',
      },
      // Same two stacks the prototype uses, kept in sync with the --font-*
      // custom properties in styles/globals.css.
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        serif: ['Georgia', 'Times New Roman', 'serif'],
      },
      boxShadow: {
        shadow: '0 24px 70px rgba(59, 35, 45, .10)',
        shadowSoft: '0 12px 36px rgba(59, 35, 45, .07)',
      },
      borderRadius: {
        xl: '32px',
        lg: '24px',
        md: '18px',
      },
      maxWidth: {
        shell: '1180px',
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}
