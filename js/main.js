// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then((registration) => {
        console.log('ServiceWorker registered:', registration);
        
        // Request notification permission
        requestNotificationPermission();
      })
      .catch((error) => {
        console.log('ServiceWorker registration failed:', error);
      });
  });
}

// Register service worker for offline functionality
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then((registration) => {
        console.log('ServiceWorker registration successful with scope: ', registration.scope);
      })
      .catch((error) => {
        console.log('ServiceWorker registration failed: ', error);
      });
  });
}

// Request permission for notifications
function requestNotificationPermission() {
  if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
    Notification.requestPermission().then((permission) => {
      if (permission === 'granted') {
        subscribeToPushNotifications();
      }
    });
  } else if (Notification.permission === 'granted') {
    subscribeToPushNotifications();
  }
}

// Subscribe to push notifications
function subscribeToPushNotifications() {
  navigator.serviceWorker.ready.then((registration) => {
    // Here you would typically send the subscription to your server
    // This is a simplified example
    const publicVapidKey = 'YOUR_GENERATED_PUBLIC_KEY';
    
    registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
    })
    .then((subscription) => {
      // Send subscription to your backend
      console.log('Push subscription:', subscription);
      fetch('/api/subscribe', {
        method: 'POST',
        body: JSON.stringify(subscription),
        headers: {
          'Content-Type': 'application/json'
        }
      });
    })
    .catch((error) => {
      console.error('Push subscription error:', error);
    });
  });
}

// Helper function to convert base64 to Uint8Array
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');
  
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Initialize resource monitor
let resourceMonitor;

function initResourceMonitor() {
  // Make sure we have the class available
  if (typeof PrinterResourceMonitor !== 'undefined') {
    resourceMonitor = new PrinterResourceMonitor(window.location.origin);
    resourceMonitor.start();
    
    // Set up event listener for dashboard updates
    window.addEventListener('resourceUpdate', function(event) {
      updateDashboardUI(event.detail.data, event.detail.alerts);
    });
  } else {
    console.error('PrinterResourceMonitor not available');
  }
}

// Function to update dashboard UI with resource data
function updateDashboardUI(data, alerts) {
  // Update UI elements with the latest data
  // This is just a starter example - customize for your UI
  
  if (!data) return;
  
  // Update consumables section
  if (data.filament) {
    const filamentElement = document.getElementById('filament-level');
    if (filamentElement) {
      filamentElement.textContent = `${data.filament.level}%`;
      filamentElement.className = data.filament.level < 15 ? 'status-error' : 
                                 (data.filament.level < 30 ? 'status-warning' : 'status-normal');
    }
  }
  
  // Update system resources
  if (data.system) {
    const memoryElement = document.getElementById('memory-usage');
    if (memoryElement) {
      memoryElement.textContent = `${data.system.memoryUsage}%`;
      memoryElement.className = data.system.memoryUsage > 90 ? 'status-error' : 
                               (data.system.memoryUsage > 75 ? 'status-warning' : 'status-normal');
    }
    
    const diskElement = document.getElementById('disk-space');
    if (diskElement) {
      diskElement.textContent = `${data.system.diskSpace}%`;
      diskElement.className = data.system.diskSpace < 10 ? 'status-error' : 
                             (data.system.diskSpace < 25 ? 'status-warning' : 'status-normal');
    }
  }
  
  // Display alerts in a notification area if present
  if (alerts && alerts.length > 0) {
    const alertsContainer = document.getElementById('alerts-container');
    if (alertsContainer) {
      // Clear previous alerts
      // alertsContainer.innerHTML = '';
      
      // Add new alerts
      alerts.forEach(alert => {
        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${alert.type === 'error' ? 'danger' : 'warning'}`;
        alertEl.textContent = alert.message;
        
        // Add dismiss button
        const dismissBtn = document.createElement('button');
        dismissBtn.className = 'close';
        dismissBtn.innerHTML = '&times;';
        dismissBtn.addEventListener('click', () => alertEl.remove());
        
        alertEl.appendChild(dismissBtn);
        alertsContainer.appendChild(alertEl);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
          if (alertEl.parentNode) {
            alertEl.remove();
          }
        }, 10000);
      });
    }
  }
}

// Initialize when document is loaded
window.addEventListener('load', () => {
  // First register service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
      .then((registration) => {
        console.log('ServiceWorker registered:', registration);
        
        // Request notification permission
        requestNotificationPermission();
      })
      .catch((error) => {
        console.log('ServiceWorker registration failed:', error);
      });
  }
  
  // Then initialize resource monitor
  // Make sure the script is loaded first
  const resourceMonitorScript = document.createElement('script');
  resourceMonitorScript.src = '/js/resource-monitor.js';
  resourceMonitorScript.onload = initResourceMonitor;
  document.head.appendChild(resourceMonitorScript);
});

// Ensure mobile bottom nav works with drawer nav
document.addEventListener('DOMContentLoaded', function() {
  const bottomNavItems = document.querySelectorAll('.mobile-nav .nav-item');
  
  bottomNavItems.forEach(item => {
    item.addEventListener('click', function(e) {
      // If this is a link to a major section that's in the drawer, update both navs
      const link = this.querySelector('a');
      if (link) {
        const href = link.getAttribute('href');
        const drawerItem = document.querySelector(`.drawer-nav-item a[href="${href}"]`);
        
        if (drawerItem) {
          // Remove active class from all nav items
          document.querySelectorAll('.drawer-nav-item').forEach(item => {
            item.classList.remove('active');
          });
          
          // Add active class to the matching drawer item
          drawerItem.parentElement.classList.add('active');
        }
      }
    });
  });
});

// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
  // Register service worker for PWA
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registered:', registration);
        
        // Request notification permission
        requestNotificationPermission();
      })
      .catch(error => {
        console.error('ServiceWorker registration failed:', error);
      });
  }
  
  // Request permission for notifications
  function requestNotificationPermission() {
    if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          console.log('Notification permission granted');
        }
      });
    }
  }
  
  // Simulate resource updates for demo purposes
  function simulateResourceUpdates() {
    // Update filament level randomly
    const filamentLevel = Math.floor(Math.random() * 100);
    const filamentElement = document.getElementById('filament-level');
    const resFilamentElement = document.getElementById('res-filament-level');
    
    if (filamentElement) {
      filamentElement.textContent = `${filamentLevel}%`;
      filamentElement.className = filamentLevel < 15 ? 'status-error' : 
                                 (filamentLevel < 30 ? 'status-warning' : 'status-normal');
    }
    
    if (resFilamentElement) {
      resFilamentElement.textContent = `${filamentLevel}%`;
    }
    
    // Update printer temperature randomly
    const printerTemp = Math.floor(190 + Math.random() * 20);
    const printerTempElement = document.getElementById('printer-temp');
    
    if (printerTempElement) {
      printerTempElement.textContent = `${printerTemp}°C`;
    }
    
    // Update system resources
    const memoryUsage = Math.floor(Math.random() * 100);
    const cpuUsage = Math.floor(Math.random() * 100);
    const diskSpace = Math.floor(Math.random() * 100);
    
    const memoryElement = document.getElementById('memory-usage');
    const cpuElement = document.getElementById('cpu-usage');
    const diskElement = document.getElementById('disk-space');
    
    if (memoryElement) {
      memoryElement.textContent = `${memoryUsage}%`;
    }
    
    if (cpuElement) {
      cpuElement.textContent = `${cpuUsage}%`;
    }
    
    if (diskElement) {
      diskElement.textContent = `${diskSpace}%`;
    }
    
    // Show alerts for low resources
    if (filamentLevel < 15) {
      showAlert('warning', `Filament level low: ${filamentLevel}%`);
    }
    
    if (diskSpace < 15) {
      showAlert('warning', `Disk space low: ${diskSpace}%`);
    }
    
    if (memoryUsage > 90) {
      showAlert('danger', `High memory usage: ${memoryUsage}%`);
    }
  }
  
  // Function to show alerts
  function showAlert(type, message) {
    const alertsContainer = document.getElementById('alerts-container');
    
    if (alertsContainer) {
      const alertEl = document.createElement('div');
      alertEl.className = `alert alert-${type}`;
      alertEl.textContent = message;
      
      // Add dismiss button
      const dismissBtn = document.createElement('button');
      dismissBtn.className = 'close';
      dismissBtn.innerHTML = '&times;';
      dismissBtn.addEventListener('click', () => alertEl.remove());
      
      alertEl.appendChild(dismissBtn);
      alertsContainer.appendChild(alertEl);
      
      // Auto-remove after 5 seconds
      setTimeout(() => {
        if (alertEl.parentNode) {
          alertEl.remove();
        }
      }, 5000);
    }
  }
  
  // Simulate resource updates every 10 seconds
  setInterval(simulateResourceUpdates, 10000);
  
  // Initial resource update
  simulateResourceUpdates();
}); 