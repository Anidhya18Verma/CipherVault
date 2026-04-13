// ── auth.js ─ Token helpers & nav state ──────────────────────────────────────

function getToken() {
    return localStorage.getItem('cv_token');
}

function getUser() {
    try {
        return JSON.parse(localStorage.getItem('cv_user'));
    } catch { return null; }
}

function logout() {
    localStorage.removeItem('cv_token');
    localStorage.removeItem('cv_user');
    window.location.href = '/';
}

function updateNavForAuth() {
    const token = getToken();
    const loginBtn = document.getElementById('nav-login-btn');
    const registerBtn = document.getElementById('nav-register-btn');
    const dashboardBtn = document.getElementById('nav-dashboard-btn');
    const logoutBtn = document.getElementById('nav-logout-btn');

    if (token) {
        if (loginBtn) loginBtn.classList.add('hidden');
        if (registerBtn) registerBtn.classList.add('hidden');
        if (dashboardBtn) dashboardBtn.classList.remove('hidden');
        if (logoutBtn) logoutBtn.classList.remove('hidden');
    } else {
        if (loginBtn) loginBtn.classList.remove('hidden');
        if (registerBtn) registerBtn.classList.remove('hidden');
        if (dashboardBtn) dashboardBtn.classList.add('hidden');
        if (logoutBtn) logoutBtn.classList.add('hidden');
    }
}

// Run on every page load
document.addEventListener('DOMContentLoaded', updateNavForAuth);
