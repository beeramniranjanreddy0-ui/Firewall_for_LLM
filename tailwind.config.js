export default {
  content: [
    "./frontend/index.html",
    "./frontend/src/**/*.{ts,tsx}",
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        firewall: {
          bg: "#0F172A",
          primary: "#3B82F6",
          danger: "#EF4444",
          success: "#10B981",
        },
      },
      boxShadow: {
        glow: "0 0 32px rgba(59, 130, 246, 0.18)",
      },
    },
  },
  plugins: [],
};
