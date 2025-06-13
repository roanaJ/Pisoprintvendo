// Resource monitoring for PisoPrint system
class PrinterResourceMonitor {
  constructor(serverUrl, checkInterval = 60000) {
    this.serverUrl = serverUrl;
    this.checkInterval = checkInterval;
    this.thresholds = {
      filament: 15,     // Alert when filament below 15%
      paper: 10,        // Alert when paper below 10%
      ink: 15,          // Alert when ink below 15%
      memory: 90,       // Alert when memory usage above 90%
      cpu: 90,          // Alert when CPU usage above 90%
      diskSpace: 10,    // Alert when free disk space below 10%
      temperature: 60   // Alert when temperature above 60°C
    };
    this.monitoringActive = false;
  }

  start() {
    if (this.monitoringActive) return;
    
    this.monitoringActive = true;
    this.monitorInterval = setInterval(() => this.checkResources(), this.checkInterval);
    
    // Initial check
    this.checkResources();
    
    console.log('Resource monitoring started');
  }

  stop() {
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
      this.monitoringActive = false;
      console.log('Resource monitoring stopped');
    }
  }

  async checkResources() {
    try {
      const response = await fetch(`${this.serverUrl}/api/system/status`);
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }
      
      const data = await response.json();
      this.analyzeResourceData(data);
    } catch (error) {
      console.error('Failed to check resources:', error);
      this.notifyError('Connection error', 'Failed to retrieve printer status');
    }
  }

  analyzeResourceData(data) {
    const alerts = [];

    // Check consumables
    if (data.filament && data.filament.level < this.thresholds.filament) {
      alerts.push({
        type: 'resource',
        resource: 'filament',
        level: data.filament.level,
        message: `Filament level low: ${data.filament.level}%`
      });
    }
    
    if (data.paper && data.paper.level < this.thresholds.paper) {
      alerts.push({
        type: 'resource',
        resource: 'paper',
        level: data.paper.level,
        message: `Paper level low: ${data.paper.level}%`
      });
    }
    
    if (data.ink && data.ink.level < this.thresholds.ink) {
      alerts.push({
        type: 'resource',
        resource: 'ink',
        level: data.ink.level,
        message: `Ink level low: ${data.ink.level}%`
      });
    }
    
    // Check system resources
    if (data.system) {
      if (data.system.memoryUsage > this.thresholds.memory) {
        alerts.push({
          type: 'system',
          resource: 'memory',
          level: data.system.memoryUsage,
          message: `High memory usage: ${data.system.memoryUsage}%`
        });
      }
      
      if (data.system.cpuUsage > this.thresholds.cpu) {
        alerts.push({
          type: 'system',
          resource: 'cpu',
          level: data.system.cpuUsage,
          message: `High CPU usage: ${data.system.cpuUsage}%`
        });
      }
      
      if (data.system.diskSpace < this.thresholds.diskSpace) {
        alerts.push({
          type: 'system',
          resource: 'diskSpace',
          level: data.system.diskSpace,
          message: `Low disk space: ${data.system.diskSpace}%`
        });
      }
    }
    
    // Check hardware status
    if (data.hardware) {
      if (data.hardware.temperature > this.thresholds.temperature) {
        alerts.push({
          type: 'hardware',
          resource: 'temperature',
          level: data.hardware.temperature,
          message: `High temperature: ${data.hardware.temperature}°C`
        });
      }
      
      if (data.hardware.errors && data.hardware.errors.length > 0) {
        data.hardware.errors.forEach(error => {
          alerts.push({
            type: 'error',
            resource: 'hardware',
            message: `Hardware error: ${error.code} - ${error.message}`
          });
        });
      }
    }
    
    // Send notifications for all alerts
    alerts.forEach(alert => {
      if (alert.type === 'error') {
        this.notifyError(alert.resource, alert.message);
      } else {
        this.notifyLowResource(alert.resource, alert.level, alert.message);
      }
    });
    
    // Update dashboard if available
    this.updateDashboard(data, alerts);
  }

  notifyError(source, message) {
    // Send to server for push notification
    fetch(`${this.serverUrl}/api/notify/error`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source: source,
        message: message,
        timestamp: new Date().toISOString()
      })
    }).catch(err => console.error('Failed to send error notification:', err));
    
    // Also show local notification if possible
    this.showLocalNotification('PisoPrint Error', message);
  }

  notifyLowResource(resource, level, message) {
    // Send to server for push notification
    fetch(`${this.serverUrl}/api/notify/resource`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resource: resource,
        level: level,
        message: message,
        timestamp: new Date().toISOString()
      })
    }).catch(err => console.error('Failed to send resource notification:', err));
    
    // Also show local notification if possible
    this.showLocalNotification('PisoPrint Resource Warning', message);
  }

  showLocalNotification(title, message) {
    if ('Notification' in window && Notification.permission === 'granted') {
      navigator.serviceWorker.ready.then(registration => {
        registration.showNotification(title, {
          body: message,
          icon: 'images/icon-192x192.png',
          badge: 'images/badge-72x72.png',
          vibrate: [100, 50, 100]
        });
      });
    }
  }

  updateDashboard(data, alerts) {
    // Update UI with latest data if dashboard is loaded
    const dashboardEvent = new CustomEvent('resourceUpdate', {
      detail: { data, alerts }
    });
    window.dispatchEvent(dashboardEvent);
  }

  // Allow threshold configuration
  setThreshold(resource, value) {
    if (this.thresholds.hasOwnProperty(resource)) {
      this.thresholds[resource] = value;
      console.log(`Threshold for ${resource} set to ${value}`);
      return true;
    }
    return false;
  }
}

// Export for use in main.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PrinterResourceMonitor;
} else {
  window.PrinterResourceMonitor = PrinterResourceMonitor;
} 