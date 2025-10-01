const CACHE_NAME = 'omnicall-v1';
const STATIC_CACHE = [
   './',
   './index.html',
   './styles.css',
   './app.js',
   './manifest.json',
   './icon-192.png',
   './icon-512.png'
 ];
// Install event - cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(STATIC_CACHE))
    );
});
// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
// Handle WebSocket connection in background
let wsConnection = null;
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'notification') {
        self.registration.showNotification(event.data.title, {
            body: event.data.message,
            icon: './icon-192.png',
            badge: './icon-192.png',
            vibrate: [100, 50, 100]
        });
    }
});



self.addEventListener('push', (event) => {
  let payload = {};
  try {
    // event.data may be null if no data payload arrived
    if (event.data) payload = event.data.json();
  } catch (e) {
    // ignore parse error and use defaults below
  }

  const title = payload.title || 'OmniCall';
  const body  = payload.message || 'Match found !! Hurry up and accept on your PC !!';
  const url   = payload.url || '/OmniCall/';

  const options = {
    body,
    icon: './icon-192.png',
    badge: './icon-192.png',
    vibrate: [100, 50, 100],
    data: { url },
    requireInteraction: true,
    actions: [{ action: 'open', title: 'Open App' }]
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

// In notificationclick event, open base URL with repo path:
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('./')
        );
    }
});