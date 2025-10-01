// --- Service Worker registration (scoped to /OmniCall/) ---
if ("serviceWorker" in navigator) {
  navigator.serviceWorker
    .register("./sw.js", { scope: "./" })
    .then(() => console.log("ServiceWorker registered successfully"))
    .catch((err) => console.log("ServiceWorker registration failed:", err));
}

// --- Firebase config (yours) ---
const firebaseConfig = {
  apiKey: "AIzaSyApbUKcukuKUYXvIfJxT6xWMVpjBTqoTdA",
  authDomain: "omnicall-d3630.firebaseapp.com",
  projectId: "omnicall-d3630",
  storageBucket: "omnicall-d3630.firebasestorage.app",
  messagingSenderId: "68373319387",
  appId: "1:68373319387:web:00592a477edba938f3c6fe",
};
firebase.initializeApp(firebaseConfig);

// --- Helpers ---
const VAPID_KEY =
  "BP65XFXUvabvVTV6IRa9m-8JrssxnxFWJxDD3I8tvxpwu2xd7EJLEXV-vdBCpkeaWFV87TCJPMRombBcbBXLZ6s";
const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent);
const isAndroid = /Android/.test(navigator.userAgent);
const isStandalone =
  window.matchMedia("(display-mode: standalone)").matches ||
  window.navigator.standalone === true;

// Capture pairing code from URL and persist it (so A2HS keeps it)
(function persistPairFromURL() {
  try {
    const params = new URLSearchParams(location.search);
    const urlPair = params.get("pair");
    if (urlPair) {
      localStorage.setItem("omnicall_user", urlPair.trim());
      // optional: clean the URL in-place (keeps localStorage value)
      history.replaceState({}, "", "./");
    }
  } catch (e) {
    console.warn("Could not parse pair param:", e);
  }
})();

// Get or prompt for the userId (pairing code)
function resolveUserId() {
  let userId = localStorage.getItem("omnicall_user");
  if (!userId) {
    userId = prompt(
      "Enter your OmniCall pairing code (from your PC/CLI or QR):"
    );
    if (!userId) return null;
    userId = userId.trim();
    localStorage.setItem("omnicall_user", userId);
  }
  return userId;
}

// Core: get FCM token and (if changed/new) write it under /users/{userId}/tokens/{token}
async function registerTokenForUser(userId) {
  const registration = await navigator.serviceWorker.ready;
  const messaging = firebase.messaging();

  const token = await messaging.getToken({
    vapidKey: VAPID_KEY,
    serviceWorkerRegistration: registration,
  });
  if (!token) throw new Error("FCM getToken() returned empty token");

  const last = localStorage.getItem("omnicall_last_token");
  if (last !== token) {
    await firebase.auth().signInAnonymously();
    const db = firebase.firestore();
    await db
      .collection("users")
      .doc(userId)
      .collection("tokens")
      .doc(token)
      .set(
        {
          token,
          userId,
          platform: isIOS ? "ios-pwa" : isAndroid ? "android-pwa" : "web",
          ua: navigator.userAgent,
          createdAt: firebase.firestore.FieldValue.serverTimestamp(),
        },
        { merge: true }
      );
    localStorage.setItem("omnicall_last_token", token);
  }

  return token;
}

// --- UI wiring ---
document.addEventListener("DOMContentLoaded", () => {
  const enableBtn = document.getElementById("enableNotifications");
  const tokenEl = document.getElementById("token");
  const copyBtn = document.getElementById("copyToken");

  // If permission already granted and paired, refresh token on load
  (async () => {
    try {
      const userId = localStorage.getItem("omnicall_user");
      if (Notification.permission === "granted" && userId) {
        const t = await registerTokenForUser(userId);
        if (tokenEl) tokenEl.textContent = `FCM Token:\n${t}`;
      }
    } catch (e) {
      console.warn("Auto refresh token on load failed:", e);
    }
  })();

  // Also refresh when app returns to foreground
  document.addEventListener("visibilitychange", async () => {
    if (document.hidden) return;
    try {
      const userId = localStorage.getItem("omnicall_user");
      if (Notification.permission === "granted" && userId) {
        await registerTokenForUser(userId);
      }
    } catch (e) {
      console.warn("Token refresh on foreground failed:", e);
    }
  });

  enableBtn.addEventListener("click", async () => {
    try {
      if (!("Notification" in window)) {
        alert("This browser does not support notifications.");
        return;
      }

      // iOS must be installed as a PWA (A2HS) for web push
      if (isIOS && !isStandalone) {
        alert(
          "On iPhone, please Add to Home Screen first, then open the app from your home screen and try again."
        );
        return;
      }

      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        alert("Notification permission denied.");
        return;
      }

      const userId = resolveUserId();
      if (!userId) {
        alert("Pairing code required.");
        return;
      }

      const token = await registerTokenForUser(userId);
      if (tokenEl) tokenEl.textContent = `FCM Token:\n${token}`;
      alert("Notifications enabled & paired!");
    } catch (err) {
      console.error("Error enabling notifications:", err);
      alert("Error enabling notifications. See console.");
    }
  });

  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const txt = (tokenEl && tokenEl.textContent) || "";
      const tokenOnly = txt.replace(/^FCM Token:\s*/i, "").trim();
      if (!tokenOnly) {
        alert("No token to copy yet.");
        return;
      }
      try {
        await navigator.clipboard.writeText(tokenOnly);
        alert("Token copied!");
      } catch (e) {
        alert("Copy failed. Select & copy manually.");
      }
    });
  }
});
