// Custom JavaScript for FastAPI Admin Panel

// Flash message handling (automatically close flash messages after 5 seconds)
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert:not(.alert-no-auto-close)');
    
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
});

// Form validation with visual feedback
const validateForms = () => {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
};

// Initialize tooltips and popovers
const initTooltips = () => {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    validateForms();
    initTooltips();
    
    // Add active class to current nav item based on URL
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav a.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentLocation === linkPath || 
            (linkPath !== '/' && currentLocation.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
});

// HTMX related utilities
document.addEventListener('htmx:configRequest', (event) => {
    // Add CSRF token to all HTMX requests if available
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        event.detail.headers['X-CSRF-Token'] = csrfToken.content;
    }
});

// Show loading indicator on HTMX requests
document.addEventListener('htmx:beforeRequest', function(event) {
    const target = event.detail.target;
    if (target && target.tagName !== 'FORM') {
        const loadingSpinner = document.createElement('div');
        loadingSpinner.className = 'spinner-border spinner-border-sm text-primary htmx-indicator';
        loadingSpinner.setAttribute('role', 'status');
        
        const span = document.createElement('span');
        span.className = 'visually-hidden';
        span.textContent = 'Načítání...';
        
        loadingSpinner.appendChild(span);
        target.appendChild(loadingSpinner);
    }
});

// Handle HTMX errors
document.addEventListener('htmx:responseError', function(event) {
    console.error('HTMX Error:', event);
    const errorMessage = document.createElement('div');
    errorMessage.className = 'alert alert-danger mt-3';
    errorMessage.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i> Nastala chyba při komunikaci se serverem. Prosím, zkuste to znovu.';
    
    const target = event.detail.target;
    if (target) {
        target.appendChild(errorMessage);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            errorMessage.remove();
        }, 5000);
    }
});

// Confirmation dialog for delete actions
const confirmDelete = (message = 'Opravdu chcete smazat tuto položku?') => {
    return confirm(message);
};

// Helper function for dark mode toggle (not active by default)
const toggleDarkMode = () => {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');
};

// Check for saved dark mode preference
const checkDarkModePreference = () => {
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
    }
};
