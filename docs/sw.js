// --- OmniCall Service Worker (relative-path build) ---
const CACHE_NAME = 'omnicall-v3'; // bump to force update
const STATIC_CACHE = [
  './',
  './index.html',
  './styles.css',
  './app.js',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './support.png', // include if present
];

// Install: pre-cache shell + take control quickly
self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_CACHE)));
  self.skipWaiting();
});

// Activate: clean old caches + claim clients
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.map((n) => (n !== CACHE_NAME ? caches.delete(n) : null)))
    )
  );
  self.clients.claim();
});

// Fetch: cache-first for precached files, fallback to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((r) => r || fetch(event.request))
  );
});

// Optional: allow foreground page to ask SW to show a local notification
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'notification') {
    const title = event.data.title || 'OmniCall';
    const body  = event.data.message || 'Match found !! Hurry up and accept on your PC !!';
    self.registration.showNotification(title, {
      body,
      icon: './icon-192.png',
      badge: './icon-192.png',
      vibrate: [100, 50, 100],
      requireInteraction: true,
      actions: [{ action: 'open', title: 'Open App' }],
      data: { url: './' }
    });
  }
});

// Push: robustly parse payload (works with data-only and/or notification payloads)
self.addEventListener('push', (event) => {
  let payload = {};
  try { if (event.data) payload = event.data.json(); } catch (_) {}

  // Prefer explicit data fields, fall back to notification block if present
  const title = payload.title
    || (payload.notification && payload.notification.title)
    || 'OmniCall';

  const body = payload.message
    || (payload.notification && payload.notification.body)
    || 'Match found !! Hurry up and accept on your PC !!';

  const url = payload.url
    || (payload.fcmOptions && payload.fcmOptions.link)
    || './';

  const options = {
    body,
    icon: './icon-192.png',
    badge: './icon-192.png',
    vibrate: [100, 50, 100],
    requireInteraction: true,
    actions: [{ action: 'open', title: 'Open App' }],
    data: { url }
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

// Click: focus existing tab if any; otherwise open the app root (relative path)
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = (event.notification && event.notification.data && event.notification.data.url) || './';

  event.waitUntil(
    (async () => {
      const allClients = await clients.matchAll({ type: 'window', includeUncontrolled: true });
      for (const client of allClients) {
        // If already on our app, focus it
        if (client.url.endsWith('/') || client.url.endsWith('/index.html')) {
          try { await client.focus(); return; } catch {}
        }
      }
      // Otherwise open a new one
      await clients.openWindow(targetUrl);
    })()
  );
});
