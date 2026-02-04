// Global variables
let charts = {};

// Tab navigation function
function showReportTab(tabName) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show the selected tab pane
    document.getElementById(tabName + '-tab').classList.add('active');

    // Add active class to the clicked tab button
    // Find button by onclick attribute since we don't have direct reference in arguments
    const button = document.querySelector(`.tab-button[onclick="showReportTab('${tabName}')"]`);
    if (button) button.classList.add('active');

    // If chart doesn't exist, initialize it
    if (!charts[tabName + 'Chart']) {
        initializeChart(tabName);
    }
}

// Initialize specific chart
function initializeChart(sectionId) {
    switch (sectionId) {
        case 'monthly':
            initializeMonthlyChart();
            break;
        case 'yearly':
            initializeYearlyChart();
            break;
        case 'product':
            initializeProductChart();
            break;
        case 'category':
            initializeCategoryChart();
            break;
        case 'customer':
            initializeCustomerChart();
            break;
        case 'daily':
            initializeDailyChart();
            break;
    }
}

// Monthly Sales Chart
function initializeMonthlyChart() {
    const ctx = document.getElementById('monthlySalesChart').getContext('2d');
    const chartColors = [
        '#667eea', '#764ba2', '#6B8AFF', '#FF6384', '#36A2EB',
        '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
    ];

    charts.monthlySalesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: window.reportConfig.data.monthly.labels,
            datasets: [{
                label: 'Sales (₹)',
                data: window.reportConfig.data.monthly.data,
                backgroundColor: chartColors.slice(0, window.reportConfig.data.monthly.data.length),
                borderColor: chartColors.slice(0, window.reportConfig.data.monthly.data.length),
                borderWidth: 1,
                borderRadius: 8,
                maxBarThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return 'Revenue: ₹' + context.parsed.y.toLocaleString('en-IN');
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        borderDash: [5, 5],
                        drawBorder: false
                    },
                    ticks: {
                        callback: function (value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            weight: '600'
                        }
                    }
                }
            }
        }
    });
}

// Yearly Sales Chart
function initializeYearlyChart() {
    const ctx = document.getElementById('yearlySalesChart').getContext('2d');
    const chartColors = ['#4A90E2', '#6366f1', '#8b5cf6', '#ec4899'];

    charts.yearlySalesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: window.reportConfig.data.yearly.labels,
            datasets: [{
                label: 'Sales (₹)',
                data: window.reportConfig.data.yearly.data,
                backgroundColor: chartColors.slice(0, window.reportConfig.data.yearly.data.length),
                borderColor: chartColors.slice(0, window.reportConfig.data.yearly.data.length),
                borderWidth: 1,
                borderRadius: 8,
                maxBarThickness: 60
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return 'Revenue: ₹' + context.parsed.y.toLocaleString('en-IN');
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        borderDash: [5, 5],
                        drawBorder: false
                    },
                    ticks: {
                        callback: function (value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            weight: '600'
                        }
                    }
                }
            }
        }
    });
}

// Product Sales Chart
function initializeProductChart() {
    const ctx = document.getElementById('productSalesChart').getContext('2d');
    const chartColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];

    charts.productSalesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: window.reportConfig.data.product.labels,
            datasets: [{
                label: 'Quantity Sold',
                data: window.reportConfig.data.product.data,
                backgroundColor: chartColors.slice(0, window.reportConfig.data.product.data.length),
                borderColor: chartColors.slice(0, window.reportConfig.data.product.data.length),
                borderWidth: 1,
                borderRadius: 8,
                maxBarThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        borderDash: [5, 5],
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            weight: '600'
                        }
                    }
                }
            }
        }
    });
}

// Category Sales Chart
function initializeCategoryChart() {
    const ctx = document.getElementById('categorySalesChart').getContext('2d');
    charts.categorySalesChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: window.reportConfig.data.category.labels,
            datasets: [{
                data: window.reportConfig.data.category.data,
                backgroundColor: [
                    '#FF6384',    // Bright Pink
                    '#36A2EB',    // Bright Blue
                    '#FFCE56',    // Bright Yellow
                    '#4BC0C0',    // Teal
                    '#9966FF',    // Purple
                    '#FF9F40',    // Orange
                    '#8AC926',    // Green
                    '#1F77B4'     // Dark Blue
                ],
                borderColor: '#ffffff',
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 11,
                            weight: '600'
                        },
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((context.parsed / total) * 100);
                            return context.label + ': ₹' + context.parsed.toLocaleString('en-IN', {
                                maximumFractionDigits: 2,
                                minimumFractionDigits: 2
                            }) + ' (' + percentage + '%)';
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1000
            }
        }
    });
}

// Customer Purchases Chart
function initializeCustomerChart() {
    const ctx = document.getElementById('customerPurchasesChart').getContext('2d');
    const chartColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];

    charts.customerPurchasesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: window.reportConfig.data.customer.labels,
            datasets: [{
                label: 'Amount Spent (₹)',
                data: window.reportConfig.data.customer.data,
                backgroundColor: chartColors.slice(0, window.reportConfig.data.customer.data.length),
                borderColor: chartColors.slice(0, window.reportConfig.data.customer.data.length),
                borderWidth: 1,
                borderRadius: 8,
                maxBarThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        borderDash: [5, 5],
                        drawBorder: false
                    },
                    ticks: {
                        callback: function (value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            weight: '600'
                        }
                    }
                }
            }
        }
    });
}

// Daily Comparison Chart
function initializeDailyChart() {
    const ctx = document.getElementById('dailyComparisonChart').getContext('2d');
    const chartColors = ['#FF6384', '#FFCE56', '#4BC0C0'];

    charts.dailyComparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Today', 'Yesterday', 'Last 7 Days'],
            datasets: [{
                label: 'Sales (₹)',
                data: [
                    window.reportConfig.data.daily.today,
                    window.reportConfig.data.daily.yesterday,
                    window.reportConfig.data.daily.last7Days
                ],
                backgroundColor: chartColors,
                borderColor: chartColors,
                borderWidth: 1,
                borderRadius: 8,
                maxBarThickness: 60
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        borderDash: [5, 5],
                        drawBorder: false
                    },
                    ticks: {
                        callback: function (value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            weight: '600'
                        }
                    }
                }
            }
        }
    });
}


// Apply filters
function applyFilters() {
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    const year = document.getElementById('yearFilter').value;

    const params = new URLSearchParams();
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    if (year) params.set('year', year);

    window.location.href = window.reportConfig.urls.reports + '?' + params.toString();
}

// Reset filters
function resetFilters() {
    window.location.href = window.reportConfig.urls.reports;
}

// Export report
function exportReport(reportId, format) {
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    const year = document.getElementById('yearFilter').value;

    // Build URL with parameters
    const params = new URLSearchParams();
    params.set('report', reportId);
    params.set('format', format);
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    if (year) params.set('year', year);

    // Redirect to download URL
    window.location.href = window.reportConfig.urls.reports + '?' + params.toString();
}

// Initialize first chart when page loads
document.addEventListener('DOMContentLoaded', function () {
    // Initialize the first chart (monthly)
    initializeChart('monthly');
});
