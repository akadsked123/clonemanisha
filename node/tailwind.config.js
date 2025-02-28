module.exports = {
  content: [
    '../templates/**/*.{html,js}',
    '../**/templates/**/*.{html,js}',
    '../**/forms.py',
    '../node_modules/flowbite/**/*.js',
    '../node_modules/preline/dist/*.js',

  ],
  theme: {
    extend: {
      colors: {
        primary: {
          "50": "#ecfdf5",
          "100": "#d1fae5",
          "200": "#a7f3d0",
          "300": "#6ee7b7",
          "400": "#34d399",
          "500": "#10b981",
          "600": "#059669",
          "700": "#047857",
          "800": "#065f46",
          "900": "#064e3b",
          "950": "#022c22"
        },
      },
      fontFamily: {
        inter: ["Inter", "sans-serif"]
      }
    }
  },
  plugins: [
    require('flowbite/plugin'),
    require('preline/plugin'),
    require('tailwind-scrollbar'),
  ]
};
