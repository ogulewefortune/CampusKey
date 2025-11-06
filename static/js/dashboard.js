// Dashboard specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    initializeBiometric();
    loadDashboardStats();
    loadRecentActivity();
});

function initializeDashboard() {
    // Initialize dashboard widgets
    setupRealTimeUpdates();
    setupQuickActions();
}

function setupRealTimeUpdates() {
    // Set up real-time updates if needed
    setInterval(function() {
        updateDashboardStats();
    }, 30000); // Update every 30 seconds
}

function setupQuickActions() {
    const quickActionButtons = document.querySelectorAll('.quick-action-btn');
    quickActionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.getAttribute('data-action');
            handleQuickAction(action);
        });
    });
}

function handleQuickAction(action) {
    switch(action) {
        case 'scan':
            openBiometricScanner();
            break;
        case 'history':
            window.location.href = '/history';
            break;
        case 'profile':
            window.location.href = '/profile';
            break;
        default:
            console.log('Unknown action:', action);
    }
}

function loadDashboardStats() {
    // Load dashboard statistics
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateStatsDisplay(data);
        })
        .catch(error => {
            console.error('Error loading stats:', error);
        });
}

function updateStatsDisplay(stats) {
    const statValues = document.querySelectorAll('.stat-value');
    if (statValues.length > 0 && stats) {
        // Update stat values if API endpoint exists
        statValues.forEach((stat, index) => {
            const statKeys = ['total_access', 'today_access', 'weekly_access', 'monthly_access'];
            if (stats[statKeys[index]]) {
                stat.textContent = stats[statKeys[index]];
            }
        });
    }
}

function updateDashboardStats() {
    // Update dashboard stats periodically
    loadDashboardStats();
}

function loadRecentActivity() {
    // Load recent activity logs
    fetch('/api/recent-activity')
        .then(response => response.json())
        .then(data => {
            updateActivityDisplay(data);
        })
        .catch(error => {
            console.error('Error loading activity:', error);
        });
}

function updateActivityDisplay(activities) {
    const activityContainer = document.querySelector('.recent-activity');
    if (!activityContainer || !activities) return;
    
    // Update activity list if needed
    activities.forEach(activity => {
        // Add activity items to the container
    });
}

function initializeBiometric() {
    const biometricButton = document.getElementById('biometricScan');
    if (biometricButton) {
        biometricButton.addEventListener('click', openBiometricScanner);
    }
}

function openBiometricScanner() {
    window.location.href = '/biometric';
}

function recordAccess(type, location) {
    fetch('/api/access', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: type,
            location: location
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Access recorded successfully', 'success');
            loadRecentActivity();
        }
    })
    .catch(error => {
        console.error('Error recording access:', error);
        showNotification('Error recording access', 'error');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transition = 'opacity 0.3s ease';
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

