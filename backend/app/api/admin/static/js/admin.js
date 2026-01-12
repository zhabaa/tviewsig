/**
 * Основной JavaScript файл админки
 */

import { notification, loading } from './utils/api.js';

class AdminApp {
    constructor() {
        this.init();
    }

    init() {
        this.bindGlobalEvents();
        this.initComponents();
        this.setupAutoRefresh();
    }

    bindGlobalEvents() {
        // Обновление страницы
        document.getElementById('refresh-page')?.addEventListener('click', () => {
            location.reload();
        });

        // Подтверждение действий
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-confirm]')) {
                const message = e.target.dataset.confirm || 'Вы уверены?';
                if (!confirm(message)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        });

        // Формы с подтверждением
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.hasAttribute('data-confirm')) {
                const message = form.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                    return false;
                }
            }
        });

        // Таблицы с сортировкой
        document.addEventListener('click', (e) => {
            if (e.target.matches('th[data-sort]')) {
                this.sortTable(e.target);
            }
        });
    }

    initComponents() {
        // Инициализация тултипов Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Инициализация попапов
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => {
            return new bootstrap.Popover(popoverTriggerEl);
        });

        // Инициализация модальных окон
        const modalElements = document.querySelectorAll('.modal');
        modalElements.forEach(modalEl => {
            const modal = new bootstrap.Modal(modalEl);
            // Сохраняем ссылку на модальное окно в элементе
            modalEl.bootstrapModal = modal;
        });
    }

    sortTable(th) {
        const table = th.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const colIndex = th.cellIndex;
        const sortDirection = th.getAttribute('data-sort-direction') || 'asc';

        rows.sort((a, b) => {
            const aVal = a.cells[colIndex].textContent.trim();
            const bVal = b.cells[colIndex].textContent.trim();

            // Пробуем преобразовать в числа для сортировки
            const aNum = parseFloat(aVal.replace(/[^\d.-]/g, ''));
            const bNum = parseFloat(bVal.replace(/[^\d.-]/g, ''));

            if (!isNaN(aNum) && !isNaN(bNum)) {
                return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
            }

            // Сортировка строк
            return sortDirection === 'asc' 
                ? aVal.localeCompare(bVal)
                : bVal.localeCompare(aVal);
        });

        // Очищаем и добавляем отсортированные строки
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));

        // Обновляем направление сортировки
        const newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        th.setAttribute('data-sort-direction', newDirection);

        // Обновляем иконку сортировки
        table.querySelectorAll('th').forEach(header => {
            header.classList.remove('sorting-asc', 'sorting-desc');
        });
        th.classList.add(`sorting-${sortDirection}`);
    }

    setupAutoRefresh() {
        // Автообновление каждые 5 минут для дашборда
        if (window.location.pathname === '/admin/') {
            setInterval(() => {
                const event = new CustomEvent('dashboard-refresh');
                window.dispatchEvent(event);
            }, 300000); // 5 минут
        }
    }

    // Утилитные методы
    static formatNumber(num) {
        return new Intl.NumberFormat('ru-RU').format(num);
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static formatPrice(price) {
        if (price >= 1000) {
            return `$${this.formatNumber(Math.round(price))}`;
        } else if (price >= 1) {
            return `$${price.toFixed(2)}`;
        } else {
            return `$${price.toFixed(4)}`;
        }
    }

    static async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            notification.success('Скопировано в буфер обмена');
            return true;
        } catch (err) {
            console.error('Failed to copy:', err);
            notification.error('Не удалось скопировать');
            return false;
        }
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    window.adminApp = new AdminApp();
    
    // Добавляем глобальные утилиты
    window.AdminUtils = AdminApp;
});

export default AdminApp;
