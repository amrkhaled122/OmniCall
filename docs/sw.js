const CACHE_NAME = 'omnicall-v1';
const STATIC_CACHE = [
    '/OmniCall/',
    '/OmniCall/index.html',
    '/OmniCall/styles.css',
    '/OmniCall/app.js',
    '/OmniCall/manifest.json',
    '/OmniCall/icon-192.png',
    '/OmniCall/icon-512.png'
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
            icon: '/icon-192.png',
            badge: '/icon-192.png',
            vibrate: [100, 50, 100]
        });
    }
});

// Push event - handle incoming push notifications
self.addEventListener('push', (event) => {
    console.log('Push received:', event);
    
    const data = event.data.json();
    const options = {
        body: data.message,
        icon: '/OmniCall/icon-192.png',
        badge: '/OmniCall/icon-192.png',
        vibrate: [100, 50, 100],
        data: {
            url: data.url || '/'
        },
        requireInteraction: true, // Keep notification visible until user interacts
        actions: [
            {
                action: 'open',
                title: 'Open App'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// In notificationclick event, open base URL with repo path:
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('/OmniCall/')
        );
    }
});