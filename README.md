# 🎮 OmniCall - Game Match Notifier

> **Never miss a match again!** Get instant push notifications on your phone when a Dota 2 match is found.

OmniCall monitors your PC screen for game matches and sends instant notifications to your phone via a Progressive Web App (PWA). Perfect for gamers who multitask while waiting in queue!

---

## ✨ Features

- 🔔 **Instant Push Notifications** - Get alerted on your phone the moment a match is found
- 🖥️ **Desktop Monitoring** - Runs quietly in the background on Windows
- 📱 **Progressive Web App** - No mobile app installation required
- 🔒 **Secure** - Your data stays private with Cloud Functions
- ⚡ **Fast** - Optimized for low latency notifications
- 📊 **Statistics** - Track your matches and see community stats

---

## 🚀 Quick Start

### Prerequisites

- **Windows 10/11** (64-bit)
- **Python 3.11+** (if running from source)
- **Modern smartphone** with web browser
- **Internet connection**

### Option 1: Download Pre-built App (Easiest)

1. **Download** the latest release from [Releases](../../releases)
2. **Extract** the ZIP file
3. **Run** `OmniCall.exe`
4. **Register** and pair your phone (see Setup Guide below)

### Option 2: Run from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/amrkhaled122/OmniCall.git
   cd OmniCall
   ```

2. **Install dependencies**
   ```bash
   pip install -r pc_app/requirements.txt
   ```

3. **Run the app**
   ```bash
   python pc_app/omnicall_app.py
   ```

---

## 📱 Setup Guide

### Step 1: Register Your Device

1. Launch OmniCall on your PC
2. Click **"Not registered? Click here"**
3. Enter a **display name** (e.g., "My Gaming PC")
4. Click **"Generate Pairing Link"**

### Step 2: Pair Your Phone

1. A **QR code** will appear on your PC
2. Open your **phone camera** and scan the QR code
   - *Or manually visit the displayed URL*
3. On your phone, click **"Allow Notifications"**
4. Click **"Pair Device"**

✅ **You're all set!** Your phone is now paired.

### Step 3: Test Notifications

1. Go to the **Feedback** tab
2. Click **"Send Test Notification"**
3. Check your phone for the notification

---

## 🎯 How to Use

### Starting Game Tracking

1. Launch **OmniCall** on your PC
2. Go to the **"Tracking"** tab
3. Click the **toggle button** to turn tracking **ON** (green)
4. Minimize the app and play your game

### What Happens Next

- OmniCall monitors your screen every 250ms
- When a match is detected, it sends a notification to your phone
- You'll get a push notification instantly
- Click the notification to see details

### Stopping Tracking

- Click the toggle button again to turn it **OFF** (red)
- Or simply close the app

---

## 📊 Features Overview

### 🎮 Tracking Tab
- **Toggle tracking ON/OFF**
- **Send test notifications**
- **Show pairing QR code**
- **View connection status**

### 📈 Statistics Tab
- **Your Activity**: Matches found, last match time
- **Community Stats**: Total users, notifications sent today
- **Refresh button** to update stats

### 💬 Feedback Tab
- **Send feedback** to the developer
- **Test notifications** anytime
- **Word counter** (max 2000 characters)

### 🛠️ Support Tab
- **Donation options** (PayPal, Binance)
- **Contact information**
- **Support the project**

---

## ⚙️ Configuration

The app stores configuration in:
```
%APPDATA%/OmniCall/config.json
```

**Config fields:**
- `user_id` - Your unique device ID
- `display_name` - Your device name
- `total_matches` - Total matches detected
- `last_match` - Timestamp of last match

*Note: Do not manually edit this file unless you know what you're doing!*

---

## 🔧 Troubleshooting

### ❌ "No notifications received"

**Check:**
1. Phone is paired (go to Tracking tab → click "Show Pairing QR")
2. Test notification works (Feedback tab → "Send Test Notification")
3. Phone browser allows notifications
4. Internet connection is active

**Fix:**
- Re-pair your phone by scanning the QR code again

---

### ❌ "App won't start"

**Check:**
1. Windows 10/11 (64-bit)
2. No antivirus blocking the app
3. Run as Administrator (right-click → "Run as administrator")

**Fix:**
- Download the latest release
- Check Windows Event Viewer for errors

---

### ❌ "Tracking button doesn't work"

**Check:**
1. You're registered (not in "Not registered" mode)
2. Template image `Accept.png` exists in app folder

**Fix:**
- Restart the app
- Re-register if needed

---

### ❌ "Statistics not loading"

**Check:**
1. Internet connection
2. Not blocked by firewall

**Fix:**
- Click "Refresh" button in Statistics tab
- Restart the app

---

## 🏗️ For Developers

### Project Structure

```
OmniCall/
├── pc_app/                 # Desktop application
│   ├── omnicall_app.py     # Main GUI (PyQt6)
│   ├── firebase_client.py  # Cloud Functions client
│   ├── detector.py         # Screen monitoring
│   ├── config.py           # Config management
│   └── requirements.txt    # Python dependencies
├── functions/              # Firebase Cloud Functions
│   ├── index.js            # Backend API
│   └── package.json        # Node dependencies
├── docs/                   # PWA (Progressive Web App)
│   ├── index.html          # PWA UI
│   ├── app.js              # PWA logic
│   ├── sw.js               # Service worker
│   └── manifest.json       # PWA manifest
└── Accept.png              # Template image for detection
```

### Tech Stack

**Desktop App:**
- Python 3.11+
- PyQt6 (GUI)
- OpenCV (screen detection)
- Requests (HTTP client)

**Backend:**
- Firebase Cloud Functions (Node.js)
- Firestore (database)
- Firebase Cloud Messaging (notifications)

**Mobile:**
- Progressive Web App (PWA)
- Service Workers (background notifications)

### Building from Source

1. **Install dependencies**
   ```bash
   pip install -r pc_app/requirements.txt
   ```

2. **Build with PyInstaller**
   ```bash
   pyinstaller OmniCall.spec
   ```

3. **Output** will be in `dist/OmniCall/`

### Running Tests

```bash
# Test notification sending
python pc_app/omnicall_app.py

# Check logs
firebase functions:log
```

---

## 🔒 Privacy & Security

- ✅ **No service account** bundled in the app
- ✅ **Secure Cloud Functions** handle all Firebase operations
- ✅ **No personal data** collected beyond device pairing
- ✅ **Open source** - review the code yourself

**What we store:**
- Device ID (random, anonymous)
- Display name (you choose)
- FCM tokens (for notifications)
- Match statistics (count only)

**What we DON'T store:**
- Screenshots
- Game usernames
- Personal information
- Credit card details

---

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 💖 Support the Project

If you find OmniCall useful, consider supporting development:

**PayPal**: [Your PayPal Link]  
**Binance**: [Your Binance Address]

---

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](../../issues)
- **Email**: amrkhaled122@aucegypt.edu
- **Website**: [https://amrkhaled122.github.io/OmniCall/](https://amrkhaled122.github.io/OmniCall/)

---

## 🙏 Acknowledgments

- Firebase for Cloud Functions and FCM
- PyQt6 for the GUI framework
- OpenCV for screen detection
- The gaming community for inspiration

---

## ⚠️ Disclaimer

This tool is for **personal use only**. Use responsibly and in accordance with the Terms of Service of any games you play. The developers are not responsible for any consequences of using this software.

---

**Made with ❤️ by Amr Khaled**

*Star ⭐ this repo if you find it useful!*
