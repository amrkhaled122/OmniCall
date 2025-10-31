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
const isDesktop = !isIOS && !isAndroid;
const isStandalone =
  window.matchMedia("(display-mode: standalone)").matches ||
  window.navigator.standalone === true;

const statusEl = () => document.getElementById("status");

// Cookie utils (bridge Safari tab → installed PWA)
function setCookie(name, value, maxAgeSeconds) {
  document.cookie = `${name}=${encodeURIComponent(
    value
  )}; Max-Age=${maxAgeSeconds}; Path=/OmniCall/; Secure; SameSite=Lax`;
}
function getCookie(name) {
  const m = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
  return m ? decodeURIComponent(m[2]) : null;
}

// Persist pairing from URL (?pair=...)
(function persistPairFromURL() {
  try {
    const params = new URLSearchParams(location.search);
    const urlPair = params.get("pair");
    if (urlPair) {
      const clean = urlPair.trim();
      localStorage.setItem("omnicall_user", clean);
      setCookie("omnicall_user", clean, 60 * 60 * 24 * 365);
      history.replaceState({}, "", "./");
      console.log("[pair] stored from URL:", clean);
    }
  } catch (e) {
    console.warn("Could not parse pair param:", e);
  }
})();

function getPairedUserId() {
  return (
    localStorage.getItem("omnicall_user") ||
    getCookie("omnicall_user") ||
    null
  );
}

// Token registration
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

// --- QR Scanner logic (jsQR) ---
let _videoStream = null;
let _scanRAF = null;

function extractUserIdFromQR(data) {
  // Accept full URL with ?pair=... or a raw userId
  try {
    const u = new URL(data);
    const p = u.searchParams.get("pair");
    if (p) return p.trim();
  } catch (_) {}
  // fallback: allow typical id pattern
  const m = String(data).trim().match(/^[a-z0-9-]{8,}$/i);
  return m ? m[0] : null;
}

async function startQRScanner() {
  const overlay = document.getElementById("scanner");
  const video = document.getElementById("qrVideo");
  overlay.classList.remove("hidden");
  overlay.setAttribute("aria-hidden", "false");

  try {
    _videoStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } },
      audio: false,
    });
  } catch (err) {
    console.error("Camera access denied:", err);
    alert("Camera permission is required to scan the QR. Please allow camera.");
    overlay.classList.add("hidden");
    overlay.setAttribute("aria-hidden", "true");
    return;
  }

  video.srcObject = _videoStream;
  await video.play();

  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d", { willReadFrequently: true });

  const tick = async () => {
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(img.data, canvas.width, canvas.height, {
        inversionAttempts: "dontInvert",
      });
      if (code && code.data) {
        const userId = extractUserIdFromQR(code.data);
        if (userId) {
          await stopQRScanner();
          // Persist pairing and auto-enable notifications
          localStorage.setItem("omnicall_user", userId);
          setCookie("omnicall_user", userId, 60 * 60 * 24 * 365);
          await enableNotificationsFlow(/* auto = */ true);
          return;
        }
      }
    }
    _scanRAF = requestAnimationFrame(tick);
  };
  _scanRAF = requestAnimationFrame(tick);
}

async function stopQRScanner() {
  const overlay = document.getElementById("scanner");
  overlay.classList.add("hidden");
  overlay.setAttribute("aria-hidden", "true");
  if (_scanRAF) cancelAnimationFrame(_scanRAF);
  _scanRAF = null;
  if (_videoStream) {
    _videoStream.getTracks().forEach((t) => t.stop());
    _videoStream = null;
  }
}

// --- Enable flow (manual button or after successful scan) ---
async function enableNotificationsFlow(auto = false) {
  try {
    if (!("Notification" in window)) {
      alert("This browser does not support notifications.");
      return;
    }
    if (isIOS && !isStandalone) {
      alert(
        "On iPhone, Add to Home Screen first, then open the app and try again."
      );
      return;
    }

    const userId = getPairedUserId();
    if (!userId) {
      // no pairing; if this was manual click, open the scanner
      if (!auto) await startQRScanner();
      return;
    }

    let permission = Notification.permission;
    if (permission !== "granted") {
      permission = await Notification.requestPermission();
    }
    if (permission !== "granted") {
      alert("Notification permission denied.");
      return;
    }

    await registerTokenForUser(userId);
    const st = statusEl();
    if (st) st.textContent = "Status: Paired & Notifications Enabled";
    alert("Paired and notifications enabled!");
  } catch (err) {
    console.error("Enable flow error:", err);
    alert("Error enabling notifications. See console.");
  }
}

// --- Stats (read-only) ---
function todayKey() {
  // Use local date (Cairo for you) in YYYY-MM-DD
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

async function loadStats() {
  try {
    const db = firebase.firestore();
    // live global stats
    db.collection("stats")
      .doc("global")
      .onSnapshot((snap) => {
        const data = snap.data() || {};
        document.getElementById("statUsers").textContent =
          data.totalUsers ?? 0;
        document.getElementById("statSends").textContent =
          data.totalSends ?? 0;
      });

    // today stats
    db.collection("stats_daily")
      .doc(todayKey())
      .onSnapshot((snap) => {
        const data = snap.data() || {};
        document.getElementById("statUsersToday").textContent =
          data.usersToday ?? 0;
      });
  } catch (e) {
    console.warn("Failed to load stats:", e);
  }
}

// --- Device-specific UI logic ---
function showDeviceSpecificUI() {
  const mobileControls = document.getElementById("mobile-controls");
  const desktopView = document.getElementById("desktop-view");
  const iosInstall = document.getElementById("ios-install");
  const androidInstall = document.getElementById("android-install");
  const headerSubtitle = document.getElementById("header-subtitle");

  // Desktop: Only show stats and support (no pairing/notifications)
  if (isDesktop) {
    if (headerSubtitle) {
      headerSubtitle.textContent = "View live stats and support the creator.";
    }
    if (mobileControls) mobileControls.style.display = "none";
    if (desktopView) desktopView.style.display = "block";
    if (iosInstall) iosInstall.style.display = "none";
    if (androidInstall) androidInstall.style.display = "none";
    loadStats();
    return;
  }

  // Mobile: Check if installed
  if (isStandalone) {
    // Installed PWA - show full mobile interface
    if (headerSubtitle) {
      headerSubtitle.textContent = "Get instant notifications when a match is found.";
    }
    if (mobileControls) mobileControls.style.display = "block";
    if (desktopView) desktopView.style.display = "block";
    if (iosInstall) iosInstall.style.display = "none";
    if (androidInstall) androidInstall.style.display = "none";
    loadStats();
  } else {
    // Not installed - show install instructions
    if (headerSubtitle) {
      headerSubtitle.textContent = "Install the app to receive notifications on your phone.";
    }
    if (mobileControls) mobileControls.style.display = "none";
    if (desktopView) desktopView.style.display = "none";
    
    if (isIOS) {
      if (iosInstall) iosInstall.style.display = "block";
      if (androidInstall) androidInstall.style.display = "none";
    } else if (isAndroid) {
      if (androidInstall) androidInstall.style.display = "block";
      if (iosInstall) iosInstall.style.display = "none";
    }
  }
}

// --- UI wiring ---
document.addEventListener("DOMContentLoaded", () => {
  const scanBtn = document.getElementById("scanQR");
  const enableBtn = document.getElementById("enableNotifications");
  const closeScan = document.getElementById("closeScan");

  // Show device-specific UI
  showDeviceSpecificUI();

  // auto: mark status if already paired & granted
  (async () => {
    try {
      const userId = getPairedUserId();
      if (userId && Notification.permission === "granted") {
        const st = statusEl();
        if (st) st.textContent = "Status: Paired & Notifications Enabled";
      } else if (getPairedUserId()) {
        const st = statusEl();
        if (st) st.textContent = "Status: Paired (permission not granted yet)";
      }
    } catch (e) {
      console.warn("Init status failed:", e);
    }
  })();

  // keep token fresh in background (no UI)
  document.addEventListener("visibilitychange", async () => {
    if (document.hidden) return;
    try {
      const userId = getPairedUserId();
      if (userId && Notification.permission === "granted") {
        await registerTokenForUser(userId);
      }
    } catch (e) {
      console.warn("Token refresh on foreground failed:", e);
    }
  });

  // buttons
  enableBtn?.addEventListener("click", () => enableNotificationsFlow(false));
  scanBtn?.addEventListener("click", () => startQRScanner());
  closeScan?.addEventListener("click", () => stopQRScanner());
});
