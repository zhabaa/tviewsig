/**
 * Утилиты для работы с графиками
 */

class ChartManager {
    constructor() {
        this.charts = new Map();
    }

    createLineChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index',
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        borderDash: [2],
                    },
                },
            },
        };

        const chart = new Chart(ctx, {
            type: 'line',
            data: data,
            options: { ...defaultOptions, ...options },
        });

        this.charts.set(canvasId, chart);
        return chart;
    }

    createBarChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        borderDash: [2],
                    },
                },
            },
        };

        const chart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: { ...defaultOptions, ...options },
        });

        this.charts.set(canvasId, chart);
        return chart;
    }

    createPieChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                },
            },
        };

        const chart = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: { ...defaultOptions, ...options },
        });

        this.charts.set(canvasId, chart);
        return chart;
    }

    createDoughnutChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                },
            },
            cutout: '60%',
        };

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: { ...defaultOptions, ...options },
        });

        this.charts.set(canvasId, chart);
        return chart;
    }

    updateChart(canvasId, data) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.data = data;
            chart.update();
        }
    }

    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }

    destroyAll() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }

    // Генератор цветов для графиков
    static generateColors(count) {
        const colors = [
            '#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6',
            '#1abc9c', '#d35400', '#c0392b', '#16a085', '#8e44ad',
            '#2c3e50', '#f1c40f', '#e67e22', '#e74c3c', '#95a5a6',
            '#7f8c8d', '#34495e', '#2c3e50', '#1abc9c', '#3498db'
        ];
        
        return colors.slice(0, count);
    }

    static createDataset(label, data, colorIndex = 0) {
        const colors = this.generateColors(20);
        const color = colors[colorIndex % colors.length];
        
        return {
            label: label,
            data: data,
            borderColor: color,
            backgroundColor: color + '20',
            borderWidth: 2,
            pointRadius: 3,
            pointBackgroundColor: color,
            pointBorderColor: '#fff',
            pointBorderWidth: 1,
            tension: 0.4,
            fill: true,
        };
    }
}

// Экспортируем менеджер графиков
const chartManager = new ChartManager();

export { chartManager, ChartManager };
