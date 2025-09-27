// Register service worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => {
            console.log('ServiceWorker registered successfully');
        })
        .catch(err => {
            console.log('ServiceWorker registration failed:', err);
        });
}

// Notification permission request on button click
document.addEventListener('DOMContentLoaded', () => {
    const enableBtn = document.getElementById('enableNotifications');
    
    enableBtn.addEventListener('click', async () => {
        if (!("Notification" in window)) {
            alert("This browser does not support notifications.");
            return;
        }
        const permission = await Notification.requestPermission();
        if (permission === "granted") {
            alert("Notifications enabled! You will now receive push notifications.");
            // TODO: Register push subscription with backend here
        } else {
            alert("Notification permission denied.");
        }
    });
});
