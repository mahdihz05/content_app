document.addEventListener("DOMContentLoaded", () => {

    // -------------------------
    // 1) MENU INTERACTIONS
    // -------------------------
    const menuItems = document.querySelectorAll(".menu-item");

    menuItems.forEach(item => {
        const title = item.querySelector(".menu-title");

        title.addEventListener("click", () => {
            menuItems.forEach(i => {
                if (i !== item) {
                    i.classList.remove("active");
                }
            });

            item.classList.toggle("active");
        });
    });

    // Auto-open based on current URL
    const currentPath = window.location.pathname;
    const allLinks = document.querySelectorAll(".submenu a");

    allLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            const menuItem = link.closest(".menu-item");
            if (menuItem) menuItem.classList.add("active");
        }
    });

    // -------------------------
    // 2) THEME MANAGEMENT
    // -------------------------
    const themeToggle = document.getElementById("theme-toggle");
    const body = document.body;

    // Load saved theme
    const savedTheme = localStorage.getItem("theme-mode") || "dark";
    body.setAttribute("data-theme", savedTheme);

    // Update toggle icons
    updateThemeIcons(savedTheme);

    // Toggle theme
    themeToggle.addEventListener("click", () => {
        const current = body.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";

        body.setAttribute("data-theme", next);
        localStorage.setItem("theme-mode", next);

        updateThemeIcons(next);
    });

    // Update the visibility of sun/moon icons
    function updateThemeIcons(theme) {
        const sunIcon = document.querySelector(".theme-toggle .sun-icon");
        const moonIcon = document.querySelector(".theme-toggle .moon-icon");

        if (theme === "light") {
            sunIcon.style.opacity = "1";
            sunIcon.style.transform = "rotate(0deg) scale(1)";
            moonIcon.style.opacity = "0";
            moonIcon.style.transform = "rotate(-180deg) scale(0)";
        } else {
            sunIcon.style.opacity = "0";
            sunIcon.style.transform = "rotate(180deg) scale(0)";
            moonIcon.style.opacity = "1";
            moonIcon.style.transform = "rotate(0deg) scale(1)";
        }
    }
});
