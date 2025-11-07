import { defineStore } from "pinia";
import { ref } from "vue";

export type Theme = "light" | "dark";

export const useThemeStore = defineStore("theme", () => {
  // 状态
  const currentTheme = ref<Theme>("light");

  // 从 localStorage 获取保存的主题，如果没有则检测系统主题
  const getInitialTheme = (): Theme => {
    const savedTheme = localStorage.getItem("theme") as Theme | null;
    if (savedTheme) {
      return savedTheme;
    }

    // 检测系统主题偏好
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      return "dark";
    }

    return "light";
  };

  // 应用主题到 DOM
  const applyTheme = (theme: Theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    currentTheme.value = theme;
  };

  // 初始化主题
  const initTheme = () => {
    const initialTheme = getInitialTheme();
    applyTheme(initialTheme);

    // 监听系统主题变化（可选功能）
    if (window.matchMedia) {
      const darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
      darkModeQuery.addEventListener("change", (e) => {
        // 只有在用户没有手动设置过主题时才自动跟随系统
        if (!localStorage.getItem("theme")) {
          applyTheme(e.matches ? "dark" : "light");
        }
      });
    }
  };

  // 切换主题
  const toggleTheme = () => {
    const newTheme: Theme = currentTheme.value === "light" ? "dark" : "light";
    applyTheme(newTheme);
    localStorage.setItem("theme", newTheme);
  };

  // 设置指定主题
  const setTheme = (theme: Theme) => {
    applyTheme(theme);
    localStorage.setItem("theme", theme);
  };

  // Getters
  const isDark = () => currentTheme.value === "dark";

  return {
    currentTheme,
    initTheme,
    toggleTheme,
    setTheme,
    isDark,
  };
});
