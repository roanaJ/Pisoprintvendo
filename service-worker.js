const CACHE_NAME = 'pisoprint-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/css/styles.css',
  '/js/main.js',
  // Add vendor files to cache
  '/vendor/css/bootstrap.min.css',
  '/vendor/css/bootstrap-icons.css',
  '/vendor/css/all.min.css',
  '/vendor/js/chart.umd.min.js',
  '/vendor/js/moment.min.js',
  // Add font files to cache
  '/vendor/fonts/bootstrap-icons.woff',
  '/vendor/fonts/bootstrap-icons.woff2',
  '/vendor/webfonts/fa-solid-900.woff2',
  '/vendor/webfonts/fa-solid-900.woff',
  '/vendor/webfonts/fa-regular-400.woff2',
  '/vendor/webfonts/fa-regular-400.woff',
  '/vendor/webfonts/fa-brands-400.woff2',
  '/vendor/webfonts/fa-brands-400.woff',
  // Add other important assets
];

// Install event - caches assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached response if found
        if (response) {
          return response;
        }
        
        // Try to fetch from network
        return fetch(event.request)
          .then((networkResponse) => {
            // If it's a valid response, clone it and store in cache
            if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              const responseToCache = networkResponse.clone();
              caches.open(CACHE_NAME)
                .then((cache) => {
                  cache.put(event.request, responseToCache);
                });
            }
            return networkResponse;
          })
          .catch(() => {
            // Network request failed, try to return offline page for HTML requests
            if (event.request.headers.get('Accept').includes('text/html')) {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// Push event - handle notifications
self.addEventListener('push', (event) => {
  const data = event.data.json();
  
  const options = {
    body: data.body,
    icon: 'images/icon-192x192.png',
    badge: 'images/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});

// Listen for messages from the client
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
}); 