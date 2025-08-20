console.log("Main JavaScript file loaded.");

// Example of a simple interactive feature:
// Add a class to the body when the sidebar is toggled.
document.addEventListener("DOMContentLoaded", function() {
    const sidebarWrapper = document.getElementById("sidebar-wrapper");
    const navbarToggler = document.querySelector(".navbar-toggler");

    if (navbarToggler && sidebarWrapper) {
        navbarToggler.addEventListener("click", function() {
            document.body.classList.toggle("sidebar-toggled");
        });
    }
});
