/**
 * Dashboard Data Handler
 * Maneja la inicialización de datos desde Django
 */

// Función para inicializar datos del dashboard
function initializeDashboardData(metrics = {}) {
    window.dashboardData = {
        chartData: {
            users_monthly: [
                { month: 'Ene', value: metrics.newUsersThisMonth || 45 },
                { month: 'Feb', value: metrics.totalUsers || 52 },
                { month: 'Mar', value: 68 },
                { month: 'Abr', value: 84 },
                { month: 'May', value: 102 },
                { month: 'Jun', value: 125 }
            ],
            orgs_monthly: [
                { month: 'Ene', value: 12 },
                { month: 'Feb', value: 15 },
                { month: 'Mar', value: 18 },
                { month: 'Abr', value: 22 },
                { month: 'May', value: 28 },
                { month: 'Jun', value: 35 }
            ],
            revenue_monthly: [
                { month: 'Ene', value: 8500 },
                { month: 'Feb', value: 9200 },
                { month: 'Mar', value: 11200 },
                { month: 'Abr', value: 13800 },
                { month: 'May', value: 15200 },
                { month: 'Jun', value: 18400 }
            ]
        },
        metrics: {
            totalUsers: metrics.totalUsers || 0,
            totalOrganizations: metrics.totalOrganizations || 0,
            totalSubscriptions: metrics.totalSubscriptions || 0,
            userGrowth: metrics.userGrowth || 0,
            orgGrowth: metrics.orgGrowth || 0,
            newUsersThisMonth: metrics.newUsersThisMonth || 0,
            newOrgsThisMonth: metrics.newOrgsThisMonth || 0,
            subscriptionRate: metrics.subscriptionRate || 0,
            pendingUpgrades: metrics.pendingUpgrades || 0
        },
        timestamps: {
            lastUpdate: new Date().toISOString(),
            nextUpdate: new Date(Date.now() + 30000).toISOString() // 30 segundos
        }
    };
    
    console.log('Dashboard data initialized:', window.dashboardData);
}

// Función para actualizar métricas en tiempo real
function updateDashboardMetrics(newMetrics) {
    if (!window.dashboardData) {
        initializeDashboardData(newMetrics);
        return;
    }
    
    // Actualizar métricas
    Object.assign(window.dashboardData.metrics, newMetrics);
    
    // Actualizar timestamp
    window.dashboardData.timestamps.lastUpdate = new Date().toISOString();
    
    // Disparar evento personalizado para notificar cambios
    window.dispatchEvent(new CustomEvent('dashboardDataUpdated', {
        detail: { metrics: newMetrics }
    }));
}

// Función para obtener datos simulados para demo
function getSimulatedData() {
    return {
        totalUsers: 1247,
        totalOrganizations: 89,
        totalSubscriptions: 156,
        userGrowth: 15.2,
        orgGrowth: 8.7,
        newUsersThisMonth: 45,
        newOrgsThisMonth: 12,
        subscriptionRate: 12.5,
        pendingUpgrades: 7
    };
}

// Inicializar con datos por defecto si no hay datos del servidor
if (typeof window !== 'undefined') {
    // Si no hay datos del servidor, usar datos simulados
    if (!window.serverData) {
        const simulatedData = getSimulatedData();
        initializeDashboardData(simulatedData);
    }
}

// Exportar funciones para uso global
window.initializeDashboardData = initializeDashboardData;
window.updateDashboardMetrics = updateDashboardMetrics;
window.getSimulatedData = getSimulatedData; 