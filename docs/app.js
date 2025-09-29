// Register service worker (scoped to /OmniCall/)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js', { scope: './' })
    .then(() => console.log('ServiceWorker registered successfully'))
    .catch(err => console.log('ServiceWorker registration failed:', err));
}

// ---- Firebase Messaging (FCM) ----
// Your Firebase Web config (from Firebase console)
const firebaseConfig = {
  apiKey: "AIzaSyApbUKcukuKUYXvIfJxT6xWMVpjBTqoTdA",
  authDomain: "omnicall-d3630.firebaseapp.com",
  projectId: "omnicall-d3630",
  // storageBucket is not required for messaging, okay to keep or omit:
  storageBucket: "omnicall-d3630.firebasestorage.app",
  messagingSenderId: "68373319387",
  appId: "1:68373319387:web:00592a477edba938f3c6fe",
  // measurementId optional; not needed for messaging
};

// Initialize Firebase (compat SDK is loaded via index.html)
firebase.initializeApp(firebaseConfig);

document.addEventListener('DOMContentLoaded', () => {
  const enableBtn = document.getElementById('enableNotifications');
  const tokenEl = document.getElementById('token');
  const copyBtn = document.getElementById('copyToken');

  enableBtn.addEventListener('click', async () => {
    try {
      if (!('Notification' in window)) {
        alert('This browser does not support notifications.');
        return;
      }
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        alert('Notification permission denied.');
        return;
      }

      const registration = await navigator.serviceWorker.ready;
      const messaging = firebase.messaging();

      // Your Public VAPID Key from Cloud Messaging → Web Push certificates
      const vapidKey = 'BP65XFXUvabvVTV6IRa9m-8JrssxnxFWJxDD3I8tvxpwu2xd7EJLEXV-vdBCpkeaWFV87TCJPMRombBcbBXLZ6s';

      const token = await messaging.getToken({
        vapidKey,
        serviceWorkerRegistration: registration
      });

      if (!token) {
        alert('Failed to get FCM token.');
        return;
      }

      tokenEl.textContent = `FCM Token:\n${token}`;
      alert('Notifications enabled! Token displayed below.');
    } catch (err) {
      console.error('Error enabling notifications:', err);
      alert('Error enabling notifications. See console.');
    }
  });

  copyBtn.addEventListener('click', async () => {
    const txt = tokenEl.textContent.replace(/^FCM Token:\s*/,'').trim();
    if (!txt) { alert('No token to copy yet.'); return; }
    try {
      await navigator.clipboard.writeText(txt);
      alert('Token copied to clipboard!');
    } catch {
      alert('Copy failed. Manually select & copy the token text.');
    }
  });
});
