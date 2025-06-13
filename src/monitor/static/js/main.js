/**
 * PisoPrint Monitor - Main JavaScript
 * Common functionality used across all pages
 */

// Format currency
function formatCurrency(amount) {
    return '₱' + amount.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Format date
function formatDate(dateString) {
    return moment(dateString).format('MMM D, YYYY');
}

// Format time
function formatTime(dateString) {
    return moment(dateString).format('h:mm A');
}

// Format date and time
function formatDateTime(dateString) {
    return moment(dateString).format('MMM D, YYYY, h:mm A');
}

// Show notifications
function showNotification(title, message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `toast show`;
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'assertive');
    notification.setAttribute('aria-atomic', 'true');
    
    // Set background color based on type
    let bgColor = 'bg-info';
    if (type === 'success') bgColor = 'bg-success';
    if (type === 'warning') bgColor = 'bg-warning';
    if (type === 'danger') bgColor = 'bg-danger';
    
    // Create notification content
    notification.innerHTML = `
        <div class="toast-header ${bgColor} text-white">
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    // Add to notification container
    const container = document.querySelector('.toast-container');
    if (container) {
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Check if sensors are in critical state
function checkSensorAlerts(sensorData) {
    if (!sensorData) return;
    
    // Check paper level
    if (sensorData.paper_percentage < 10) {
        showNotification('Paper Alert', 'Paper level critically low! Please refill paper.', 'danger');
    } else if (sensorData.paper_percentage < 20) {
        showNotification('Paper Alert', 'Paper level low. Consider refilling soon.', 'warning');
    }
    
    // Check ink levels
    for (const [color, level] of Object.entries(sensorData.ink_levels)) {
        if (level < 10) {
            showNotification('Ink Alert', `${color.charAt(0).toUpperCase() + color.slice(1)} ink critically low! Please refill.`, 'danger');
        } else if (level < 20) {
            showNotification('Ink Alert', `${color.charAt(0).toUpperCase() + color.slice(1)} ink low. Consider refilling soon.`, 'warning');
        }
    }
}

// Create a notification container if it doesn't exist
document.addEventListener('DOMContentLoaded', function() {
    if (!document.querySelector('.toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Mobile menu toggle - completely rewritten for reliability
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (menuToggle) {
        // Remove any previous event listeners
        menuToggle.replaceWith(menuToggle.cloneNode(true));
        
        // Get the new menuToggle after replacing
        const newMenuToggle = document.querySelector('.menu-toggle');
        
        // Add click event listener
        newMenuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            navMenu.classList.toggle('active');
            console.log('Menu toggle clicked'); // For debugging
        });
        
        // Close when clicking outside
        document.addEventListener('click', function(e) {
            if (navMenu.classList.contains('active') && 
                !e.target.closest('.nav-menu') && 
                !e.target.closest('.menu-toggle')) {
            navMenu.classList.remove('active');
        }
    });
    
        // Close when link is clicked
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
                navMenu.classList.remove('active');
            });
        });
    }
    
    // Handle refresh button
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            // Show loading indicator
            this.innerHTML = '<i class="bi bi-arrow-repeat"></i> Refreshing...';
            this.disabled = true;
            
            // Refresh data
            updateDashboardData();
            
            // Reset button after 1 second
            setTimeout(() => {
                this.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
                this.disabled = false;
            }, 1000);
        });
    }
    
    // Force initial data load for dashboard
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        console.log("Dashboard detected, loading data...");
        setTimeout(updateDashboardData, 500); // Slight delay to ensure DOM is ready
    }
    
    // Check for extremely small screens
    function checkScreenSize() {
        if (window.innerWidth <= 320) {
            document.body.classList.add('extremely-small');
        } else {
            document.body.classList.remove('extremely-small');
        }
    }
    
    // Call on load and on resize
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
});

// Function to update dashboard data
function updateDashboardData() {
    console.log("Updating dashboard data..."); // Debug logging
    
    // Fetch system status
    fetch('/api/system-status')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log("Data received:", data); // Debug logging
            
            if (data.status === 'ok') {
                // Update system info
                const systemInfo = data.system_info;
                const sensorData = data.sensor_data;
                
                // Update dashboard cards with data validation
                if (document.getElementById('totalRevenue')) {
                    document.getElementById('totalRevenue').textContent = '₱' + formatNumber(systemInfo.total_revenue || 0);
                }
                
                if (document.getElementById('totalPages')) {
                    document.getElementById('totalPages').textContent = formatNumber(systemInfo.total_pages || 0);
                }
                
                if (document.getElementById('recentJobs')) {
                    document.getElementById('recentJobs').textContent = formatNumber(systemInfo.recent_jobs_count || 0);
                }
                
                // Update printer status with more detailed information
                updatePrinterStatus({
                    detected: systemInfo.printer_detected,
                    online: systemInfo.printer_online,
                    name: systemInfo.printer_name,
                    error_message: systemInfo.printer_error
                });
                
                // Update maintenance info
                if (document.getElementById('maintenanceDays')) {
                    document.getElementById('maintenanceDays').textContent = systemInfo.days_since_maintenance + ' days';
                    
                    // Set color based on maintenance status
                    if (systemInfo.days_since_maintenance > 30) {
                        document.getElementById('maintenanceDays').className = 'text-danger';
                    } else if (systemInfo.days_since_maintenance > 15) {
                        document.getElementById('maintenanceDays').className = 'text-warning';
                    } else {
                        document.getElementById('maintenanceDays').className = 'text-success';
                    }
                }
                
                if (document.getElementById('lastMaintenance')) {
                    document.getElementById('lastMaintenance').textContent = formatDate(systemInfo.last_maintenance);
                }
                
                // Update sensor data display
                if (sensorData) {
                    updateSensorDataDisplay(sensorData);
                }
            } else {
                console.error("API returned error status:", data);
                showNotification('Data Error', 'Could not load dashboard data', 'warning');
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            showNotification('Connection Error', 'Could not connect to the server', 'danger');
        });
        
    // Fetch transaction data for chart
    fetch('/api/transactions?days=14')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok' && window.revenueChart) {
                // Update chart data
                const chartData = data.chart_data;
                
                // Process data for chart
                const labels = chartData.map(item => item.date);
                const revenueData = chartData.map(item => item.revenue);
                
                // Update chart
                window.revenueChart.data.labels = labels;
                window.revenueChart.data.datasets[0].data = revenueData;
                window.revenueChart.update();
            }
        })
        .catch(error => console.error('Error:', error));
}

// Helper function to format numbers
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Helper function to format dates
function formatDate(dateString) {
    if (!dateString) return '--';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Update the function that handles sensor data to handle undefined values
function updateSensorDataDisplay(sensorData) {
    // Check if we have valid sensor data and Arduino connection
    const arduinoConnected = sensorData && sensorData.arduino_connected === true;
    
    // Update Arduino connection status first
    updateArduinoConnectionStatus(arduinoConnected);
    
    // If Arduino is not connected, show disconnection for all sensors
    if (!arduinoConnected) {
        showFullDisconnectionStatus();
        return;
    }
    
    // Handle paper level when Arduino is connected
    const paperPercentage = sensorData.paper_percentage !== undefined ? sensorData.paper_percentage : "N/A";
    const paperCount = sensorData.paper_level !== undefined ? sensorData.paper_level : "N/A";
    
    if (typeof paperPercentage === 'number') {
        // Update paper level display with valid numeric data
        $('#paperValue').text(paperPercentage + '%');
        $('#paperLevelText').text(`${paperCount || 0} / ${sensorData.paper_capacity || 50} sheets`);
        $('#paperLevelBar').css('width', paperPercentage + '%').text(paperPercentage + '%');
        
        // Set appropriate color based on level
        if (paperPercentage < 10) {
            $('#paperLevelBar').removeClass('bg-success bg-warning').addClass('bg-danger');
        } else if (paperPercentage < 30) {
            $('#paperLevelBar').removeClass('bg-success bg-danger').addClass('bg-warning');
        } else {
            $('#paperLevelBar').removeClass('bg-warning bg-danger').addClass('bg-success');
        }
    } else {
        // Show error for paper sensor when Arduino is connected but sensor is not working
        $('#paperValue').text('Sensor Error');
        $('#paperLevelText').text('Paper sensor not responding');
        $('#paperLevelBar').css('width', '100%')
                          .removeClass('bg-success bg-warning')
                          .addClass('bg-danger')
                          .text('Sensor Error');
    }
    
    // Handle ink levels when Arduino is connected
    if (sensorData.ink_levels && typeof sensorData.ink_levels === 'object') {
        for (const [color, level] of Object.entries(sensorData.ink_levels)) {
            if (typeof level === 'number') {
                // Update ink level with valid data
                $(`#${color}InkLevel`).text(level + '%');
                $(`#${color}Progress`).css('width', level + '%');
                
                // Set appropriate color based on level
                if (level < 10) {
                    $(`#${color}Progress`).removeClass('bg-success bg-warning').addClass('bg-danger');
                    $(`#${color}Status`).text('CRITICAL').addClass('text-danger');
                } else if (level < 25) {
                    $(`#${color}Progress`).removeClass('bg-success bg-danger').addClass('bg-warning');
                    $(`#${color}Status`).text('LOW').addClass('text-warning');
                } else {
                    $(`#${color}Progress`).removeClass('bg-warning bg-danger').addClass('bg-success');
                    $(`#${color}Status`).text('OK').removeClass('text-warning text-danger');
                }
            } else {
                // Show error for ink sensor
                $(`#${color}InkLevel`).text('Sensor Error');
                $(`#${color}Progress`).css('width', '100%')
                                    .removeClass('bg-success bg-warning')
                                    .addClass('bg-danger');
                $(`#${color}Status`).text('ERROR').addClass('text-danger');
            }
        }
    } else {
        // All ink sensors error
        $('.ink-status').text('Sensor Error').addClass('text-danger');
        $('.ink-progress').css('width', '100%')
                         .removeClass('bg-success bg-warning')
                         .addClass('bg-danger');
    }
}

// Function to show full disconnection status when Arduino is disconnected
function showFullDisconnectionStatus() {
    // Update paper level indicators
    $('#paperValue').text('Arduino Disconnected');
    $('#paperLevelText').text('Connect Arduino to read paper level');
    $('#paperLevelBar').css('width', '100%')
                      .removeClass('bg-success bg-warning bg-danger')
                      .addClass('bg-secondary')
                      .text('Arduino Not Connected');
    
    // Update ink level indicators
    $('.ink-level').text('Arduino Disconnected');
    $('.ink-progress').css('width', '100%')
                     .removeClass('bg-success bg-warning bg-danger')
                     .addClass('bg-secondary');
    $('.ink-status').text('NO CONNECTION').addClass('text-secondary');
    
    // Update status cards
    $('#paperStatus').html('<span class="badge bg-secondary">Disconnected</span>');
    $('#blackInkStatus, #cyanInkStatus, #magentaInkStatus, #yellowInkStatus').html(
        '<span class="badge bg-secondary">Disconnected</span>'
    );
}

// Function to update Arduino connection status
function updateArduinoConnectionStatus(isConnected) {
    const statusElement = $('#arduinoStatus');
    if (statusElement.length) {
        if (isConnected) {
            statusElement.html('<span class="badge bg-success">Connected</span>');
            $('#connectArduinoBtn').addClass('d-none');
        } else {
            statusElement.html('<span class="badge bg-danger">Disconnected</span>');
            $('#connectArduinoBtn').removeClass('d-none');
        }
    }
}

// Update the printer status display to be more descriptive
function updatePrinterStatus(printerInfo) {
    if (!printerInfo) {
        $('#printerStatus').html('<span class="badge bg-secondary">Unknown</span>');
        return;
    }

    if (printerInfo.detected === false) {
        $('#printerStatus').html('<span class="badge bg-danger">No Printer Detected</span>');
        return;
    }
    
    if (printerInfo.online === true && printerInfo.detected === true) {
        // Printer is detected and online
        $('#printerStatus').html(`<span class="badge bg-success">${printerInfo.name || 'Printer'} Ready</span>`);
    } else if (printerInfo.detected === true && printerInfo.online === false) {
        // Printer is detected but offline/error
        const errorMessage = printerInfo.error_message || 'Not Ready';
        $('#printerStatus').html(`<span class="badge bg-warning">${printerInfo.name || 'Printer'}: ${errorMessage}</span>`);
    } else {
        // Fallback for any other status
        $('#printerStatus').html('<span class="badge bg-secondary">Status Unknown</span>');
    }
}