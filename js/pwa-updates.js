// PWA Update Handler
class PWAUpdater {
  constructor() {
    this.registration = null;
    this.updateFound = false;
    this.refreshing = false;
    
    // Listen for the controlling service worker changing
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (this.refreshing) return;
      this.refreshing = true;
      window.location.reload();
    });
  }
  
  init() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
          this.registration = registration;
          
          // Check if a new service worker is waiting
          if (registration.waiting) {
            this.updateReady(registration.waiting);
          }
          
          // Listen for new service workers
          registration.addEventListener('updatefound', () => {
            this.updateFound = true;
            const newWorker = registration.installing;
            
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                this.updateReady(newWorker);
              }
            });
          });
          
          // Check for updates every hour
          setInterval(() => {
            registration.update();
          }, 3600000);
        })
        .catch(error => {
          console.error('Service Worker registration failed:', error);
        });
    }
  }
  
  updateReady(worker) {
    // Show update notification
    this.showUpdateNotification()
      .then(shouldUpdate => {
        if (shouldUpdate) {
          worker.postMessage({ type: 'SKIP_WAITING' });
        }
      });
  }
  
  showUpdateNotification() {
    return new Promise(resolve => {
      // Create update UI
      const updateBar = document.createElement('div');
      updateBar.className = 'pwa-update-bar';
      updateBar.innerHTML = `
        <span>A new version is available!</span>
        <button id="pwa-update-button">Update Now</button>
        <button id="pwa-update-later">Later</button>
      `;
      
      // Style the update bar
      updateBar.style.position = 'fixed';
      updateBar.style.bottom = '0';
      updateBar.style.left = '0';
      updateBar.style.right = '0';
      updateBar.style.backgroundColor = '#4285f4';
      updateBar.style.color = 'white';
      updateBar.style.padding = '12px 16px';
      updateBar.style.display = 'flex';
      updateBar.style.justifyContent = 'space-between';
      updateBar.style.alignItems = 'center';
      updateBar.style.zIndex = '9999';
      
      document.body.appendChild(updateBar);
      
      // Add event listeners
      document.getElementById('pwa-update-button').addEventListener('click', () => {
        resolve(true);
        updateBar.remove();
      });
      
      document.getElementById('pwa-update-later').addEventListener('click', () => {
        resolve(false);
        updateBar.remove();
      });
    });
  }
}

// Initialize the PWA updater
const pwaUpdater = new PWAUpdater();
pwaUpdater.init(); 