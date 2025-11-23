// main.js - Funcionalidades globales

document.addEventListener('DOMContentLoaded', function() {
    // --- Lógica del Modo Oscuro ---
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Función para aplicar el tema
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
        } else {
            body.classList.remove('dark-mode');
        }
    };

    // Cargar tema guardado o preferido por el sistema
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme) {
        applyTheme(savedTheme);
    } else if (prefersDark) {
        applyTheme('dark');
    }

    // --- CORRECCIÓN AQUÍ: Validamos si el botón existe antes de usarlo ---
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isDark = body.classList.contains('dark-mode');
            if (isDark) {
                applyTheme('light');
                localStorage.setItem('theme', 'light');
            } else {
                applyTheme('dark');
                localStorage.setItem('theme', 'dark');
            }
        });
    }

    // Auto-cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        });
    }
    
    // Confirmar acciones importantes
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    if (confirmButtons.length > 0) {
        confirmButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const message = this.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Tooltips simples
    const tooltips = document.querySelectorAll('[data-tooltip]');
    if (tooltips.length > 0) {
        tooltips.forEach(element => {
            element.addEventListener('mouseenter', function() {
                const text = this.getAttribute('data-tooltip');
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = text;
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
                tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + 'px';
            });
            
            element.addEventListener('mouseleave', function() {
                const tooltip = document.querySelector('.tooltip');
                if (tooltip) tooltip.remove();
            });
        });
    }
});

// Función para formatear números con comas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Función para mostrar mensajes
function showMessage(message, type = 'info') {
    const container = document.querySelector('.flash-container') || createFlashContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span class="alert-icon">${getIcon(type)}</span>
        <span class="alert-message">${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
    return container;
}

function getIcon(type) {
    const icons = {
        'success': '✅',
        'danger': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[type] || icons['info'];
}

// Animación de fadeOut para alertas
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(400px); }
    }
    
    .tooltip {
        position: fixed;
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        z-index: 9999;
        pointer-events: none;
    }
`;
document.head.appendChild(style);