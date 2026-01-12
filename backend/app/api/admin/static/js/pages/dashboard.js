/**
 * JavaScript для дашборда
 */

import { api, notification, loading } from '../utils/api.js';

class Dashboard {
    constructor() {
        this.stats = {
            total_signals: 0,
            today_signals: 0,
            active_bots: 0,
            last_signal: 'Нет данных'
        };
        
        this.autoUpdateInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadDashboardData();
        this.startAutoUpdate();
    }

    bindEvents() {
        // Обновление по кнопке
        const refreshBtn = document.getElementById('refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDashboardData());
        }

        // Автообновление чекбокс
        const autoUpdateCheckbox = document.getElementById('auto-update');
        if (autoUpdateCheckbox) {
            autoUpdateCheckbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoUpdate();
                } else {
                    this.stopAutoUpdate();
                }
            });
        }
    }

    async loadDashboardData() {
        try {
            const data = await loading.withLoading(
                () => api.get('/quick-stats'),
                'Загрузка статистики...'
            );

            if (data.error) {
                throw new Error(data.error);
            }

            this.updateStats(data);
            this.updateRecentSignals();
            
            notification.success('Данные обновлены');
        } catch (error) {
            console.error('Error loading dashboard:', error);
            notification.error('Ошибка загрузки данных');
        }
    }

    updateStats(data) {
        this.stats = {
            total_signals: data.total_signals || 0,
            today_signals: data.today_signals || 0,
            active_bots: data.active_bots || 0,
            last_signal: data.last_signal || 'Нет данных'
        };

        // Обновляем DOM
        document.querySelectorAll('[data-stat="total_signals"]').forEach(el => {
            el.textContent = this.stats.total_signals.toLocaleString();
        });
        
        document.querySelectorAll('[data-stat="today_signals"]').forEach(el => {
            el.textContent = this.stats.today_signals.toLocaleString();
        });
        
        document.querySelectorAll('[data-stat="active_bots"]').forEach(el => {
            el.textContent = this.stats.active_bots.toLocaleString();
        });
        
        document.querySelectorAll('[data-stat="last_signal"]').forEach(el => {
            el.textContent = this.stats.last_signal;
        });
    }

    async updateRecentSignals() {
        try {
            const response = await api.get('/api/signals?limit=10');
            
            if (response && Array.isArray(response)) {
                this.renderRecentSignals(response);
            }
        } catch (error) {
            console.error('Error loading recent signals:', error);
        }
    }

    renderRecentSignals(signals) {
        const container = document.getElementById('recent-signals-container');
        if (!container) return;

        if (signals.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-bell-slash fs-1 text-muted"></i>
                    <p class="text-muted mt-3">Нет последних сигналов</p>
                </div>
            `;
            return;
        }

        const html = signals.map(signal => `
            <div class="signal-item mb-3 p-3 border rounded fade-in">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="badge bg-dark me-2">${signal.bot_name}</span>
                        <strong>${signal.symbol}</strong>
                    </div>
                    <div>
                        ${this.getActionBadge(signal.action)}
                        <span class="ms-2 text-muted small">
                            ${new Date(signal.timestamp).toLocaleTimeString()}
                        </span>
                    </div>
                </div>
                <div class="mt-2">
                    <span class="fw-bold">$${parseFloat(signal.price).toFixed(2)}</span>
                    ${signal.comment ? `<span class="ms-3 text-muted">${signal.comment}</span>` : ''}
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    getActionBadge(action) {
        const badges = {
            'BUY': 'bg-success',
            'SELL': 'bg-danger',
            'HOLD': 'bg-secondary',
            'STRONG_BUY': 'bg-success',
            'STRONG_SELL': 'bg-danger'
        };
        
        const className = badges[action] || 'bg-secondary';
        return `<span class="badge ${className}">${action}</span>`;
    }

    startAutoUpdate(interval = 30000) {
        this.stopAutoUpdate(); // Останавливаем предыдущий интервал
        
        this.autoUpdateInterval = setInterval(() => {
            this.loadDashboardData();
        }, interval);
        
        // Обновляем индикатор автообновления
        const indicator = document.getElementById('auto-update-indicator');
        if (indicator) {
            indicator.classList.remove('d-none');
            indicator.innerHTML = `<i class="bi bi-arrow-clockwise"></i> Автообновление каждые ${interval / 1000} сек`;
        }
    }

    stopAutoUpdate() {
        if (this.autoUpdateInterval) {
            clearInterval(this.autoUpdateInterval);
            this.autoUpdateInterval = null;
            
            const indicator = document.getElementById('auto-update-indicator');
            if (indicator) {
                indicator.classList.add('d-none');
            }
        }
    }

    destroy() {
        this.stopAutoUpdate();
        // Убираем все обработчики событий
        const refreshBtn = document.getElementById('refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.replaceWith(refreshBtn.cloneNode(true));
        }
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new Dashboard();
    
    // Экспортируем для отладки
    window.dashboard = dashboard;
    
    // Очистка при разгрузке страницы
    window.addEventListener('beforeunload', () => {
        dashboard.destroy();
    });
});

export default Dashboard;
