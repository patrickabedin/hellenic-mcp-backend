import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#3B82F6',
          dark: '#2563EB',
          blue: '#3B82F6',
          'blue-dark': '#2563EB',
          surface: '#111113',
          'text-secondary': '#A1A1AA',
        },
        surface: {
          DEFAULT: '#111113',
          elevated: '#18181B',
        },
        bg: {
          DEFAULT: '#09090B',
        },
        border: {
          DEFAULT: '#27272A',
        },
      },
    },
  },
  plugins: [],
};
export default config;
