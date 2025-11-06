// Authentication related JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeAuthForms();
    initializePasswordToggle();
});

function initializeAuthForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const resetForm = document.getElementById('resetForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegisterSubmit);
    }
    
    if (resetForm) {
        resetForm.addEventListener('submit', handleResetSubmit);
    }
}

function handleLoginSubmit(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showError('Please enter both username and password');
        return;
    }
    
    // Form will submit normally after validation
    e.target.submit();
}

function handleRegisterSubmit(e) {
    e.preventDefault();
    
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword')?.value;
    
    if (password.length < 8) {
        showError('Password must be at least 8 characters long');
        return;
    }
    
    if (confirmPassword && password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }
    
    // Form will submit normally after validation
    e.target.submit();
}

function handleResetSubmit(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    
    if (!validateEmail(email)) {
        showError('Please enter a valid email address');
        return;
    }
    
    // Form will submit normally after validation
    e.target.submit();
}

function initializePasswordToggle() {
    const passwordToggles = document.querySelectorAll('.password-toggle');
    
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordInput = this.previousElementSibling;
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            this.textContent = type === 'password' ? '👁️' : '👁️‍🗨️';
        });
    });
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-error';
    errorDiv.textContent = message;
    
    const form = document.querySelector('form');
    form.insertBefore(errorDiv, form.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success';
    successDiv.textContent = message;
    
    const form = document.querySelector('form');
    form.insertBefore(successDiv, form.firstChild);
    
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}

