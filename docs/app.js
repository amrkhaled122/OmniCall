// SW registration (scoped to /OmniCall/)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js', { scope: './' })
    .then(() => console.log('ServiceWorker registered successfully'))
    .catch(err => console.log('ServiceWorker registration failed:', err));
}

// ---- Firebase config (yours) ----
const firebaseConfig = {
  apiKey: "AIzaSyApbUKcukuKUYXvIfJxT6xWMVpjBTqoTdA",
  authDomain: "omnicall-d3630.firebaseapp.com",
  projectId: "omnicall-d3630",
  storageBucket: "omnicall-d3630.firebasestorage.app",
  messagingSenderId: "68373319387",
  appId: "1:68373319387:web:00592a477edba938f3c6fe"
};
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

      // 1) Ensure we have a pairing code (userId) persisted
      let userId = localStorage.getItem('omnicall_user');
      if (!userId) {
        userId = prompt('Enter your OmniCall pairing code (provided by your PC/CLI):');
        if (!userId) { alert('Pairing code required.'); return; }
        userId = userId.trim();
        localStorage.setItem('omnicall_user', userId);
      }

      // 2) Get token
      const registration = await navigator.serviceWorker.ready;
      const messaging = firebase.messaging();
      const vapidKey = 'BP65XFXUvabvVTV6IRa9m-8JrssxnxFWJxDD3I8tvxpwu2xd7EJLEXV-vdBCpkeaWFV87TCJPMRombBcbBXLZ6s';

      const token = await messaging.getToken({
        vapidKey,
        serviceWorkerRegistration: registration
      });
      if (!token) { alert('Failed to get FCM token.'); return; }

      // 3) Sign in anonymously and store token under the user
      await firebase.auth().signInAnonymously();
      const db = firebase.firestore();
      await db.collection('users').doc(userId).collection('tokens').doc(token).set({
        token,
        userId,
        platform: 'ios-pwa',
        ua: navigator.userAgent,
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
      }, { merge: true });

      if (tokenEl) tokenEl.textContent = `FCM Token:\n${token}`;
      alert('Notifications enabled & paired!');
    } catch (err) {
      console.error('Error enabling notifications:', err);
      alert('Error enabling notifications. See console.');
    }
  });

  copyBtn?.addEventListener('click', async () => {
    const txt = (tokenEl?.textContent || '').replace(/^FCM Token:\s*/,'').trim();
    if (!txt) { alert('No token to copy yet.'); return; }
    try { await navigator.clipboard.writeText(txt); alert('Token copied!'); }
    catch { alert('Copy failed. Select & copy manually.'); }
  });
});
