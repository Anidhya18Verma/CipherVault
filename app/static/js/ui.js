// ── ui.js ─ Navbar scroll, hamburger, misc UI ────────────────────────────────

function toggleMenu() {
    const links = document.getElementById('nav-links');
    const actions = document.getElementById('nav-actions');
    const ham = document.getElementById('hamburger');
    links?.classList.toggle('open');
    actions?.classList.toggle('open');
    ham?.classList.toggle('open');
}

// Navbar shrink on scroll
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
    }
});

// Close mobile menu on link click
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            document.getElementById('nav-links')?.classList.remove('open');
            document.getElementById('nav-actions')?.classList.remove('open');
            document.getElementById('hamburger')?.classList.remove('open');
        });
    });
});
