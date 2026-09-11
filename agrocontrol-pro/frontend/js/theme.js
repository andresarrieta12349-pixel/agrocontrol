(() => {
  const themeKey = "agrocontrol_tema";
  const root = document.documentElement;

  function applyTheme(theme) {
    root.dataset.theme = theme;
    const button = document.getElementById("btn-tema");
    if (button) {
      const darkMode = theme === "oscuro";
      button.textContent = darkMode ? "Modo claro" : "Modo oscuro";
      button.setAttribute("aria-pressed", String(darkMode));
    }
    const texto = document.getElementById("texto-tema");
    if (texto) {
      texto.textContent = theme === "oscuro" ? "Modo claro" : "Modo oscuro";
    }
  }

  window.toggleTheme = () => {
    const nextTheme = root.dataset.theme === "oscuro" ? "claro" : "oscuro";
    localStorage.setItem(themeKey, nextTheme);
    applyTheme(nextTheme);
  };

  applyTheme(localStorage.getItem(themeKey) || "claro");
})();