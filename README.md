# 🎮 OmniCall - Game Match Notifier

> **Never miss a match again!** Get instant push notifications on your phone when a Dota 2 match is found.

OmniCall monitors your PC screen for game matches and sends instant notifications to your phone via a Progressive Web App (PWA). Perfect for gamers who multitask while waiting in queue!

---

## ✨ Features

- 🔔 **Instant Push Notifications** - Get alerted on your phone the moment a match is found.
- 🖥️ **Desktop Monitoring** - Runs quietly in the background on Windows.
- 📱 **Progressive Web App** - No mobile app installation required  just add the app to the home screen using the steps you will see below !
- 🔒 **Secure** - No data is stored from your side , you use an anonymous name to generate a token that is used to send ntofications to your device.
- ⚡ **Fast** - Optimized for low latency notifications.
- 📊 **Statistics** - Track your matches and see community stats.

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

### Step 1: Download and Install

1. **Go to [Releases](../../releases)** and download the latest `OmniCall-Setup-v1.0.0.exe`

2. **Run the installer** - You'll see the following screens:

   ![Installer Step 1](screenshots/Installer_1.png)
   *License agreement - Read and accept to proceed*

   ![Installer Step 2](screenshots/Installer_2.png)
   *Select additional tasks (Desktop shortcut, etc.)*

   ![Installer Step 3](screenshots/Installer_3.png)
   *Press install*

   ![Installer Step 4](screenshots/Installer_4.png)
   *Wait for the installer to finish*

   ![Installer Step 5](screenshots/Installer_5.png)
   *Installation complete - Launch OmniCall*

---

### Step 2: Register Your Device

1. **Launch OmniCall** - You'll see the registration screen:

   ![Launch Screen 1 - Register](screenshots/Launch_1.png)
   *Enter a friendly device name (e.g., "Nevermore's Laptop", "Gaming PC")*

2. **Generate Pairing QR** - After entering your name, click the button:

   ![Launch Screen 2 - Generate](screenshots/Launch_2.png)
   *Click "Generate Pairing QR" to create your unique pairing code*

---

### Step 3: Pair Your Phone

1. **Scan the QR Code** - The setup screen appears with QR and instructions:

   ![Launch Screen 3 - QR Code](screenshots/Launch_3.png)
   *Scan this QR code with your phone camera*

2. **Install PWA on Your Phone** - Watch this quick setup guide:

   <div align="center">
   
   
   https://github.com/user-attachments/assets/1ad8c082-f9be-478e-81c7-4422e4079dc6
   
   *📱 1-minute video showing iPhone and Android PWA installation*
   
   </div>

   **Or follow these steps manually:**

   **For iPhone:**
   - Scan QR → Opens in Safari
   - Tap Share button (⬆️) → "Add to Home Screen"
   - Tap "Add" → Open from home screen
   - Tap "Enable Notifications" in the PWA

   **For Android:**
   - Scan QR → Opens in Chrome
   - Tap menu (⋮) → "Install app"
   - Tap "Install" → Open from home screen
   - Tap "Enable Notifications" in the PWA

3. **Send Test Notification** - Back on your PC, click "Send Test Notification":

   ![Launch Screen 4 - Success](screenshots/Launch_4.png)
   *✅ Confirmation screen - Your phone is now paired!*

---

### Step 4: You're Ready!

Your desktop app and phone are now connected. You'll receive instant notifications when matches are found.

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

## 📊 App Features

### 🎮 Tracking Tab - Initial State

![Tracking Tab - OFF](screenshots/App_Tab_2.png)

When you first launch OmniCall, tracking is **OFF** (red button):
- **Complete registration** - Ensure you've paired your phone first
- **Send Test** - Verify notifications work before starting tracking
- **Show Pairing QR** - Add more phones or re-pair if needed
- **Status indicator** - Shows "Tracking idle" when not monitoring

*Ready to start? Click the toggle button to turn tracking ON!*

---

### 🎮 Tracking Tab - Active Monitoring

![Tracking Tab - ON](screenshots/App_Tab_1.png)

Once you enable tracking, the button turns **ON** (green):
- **Active monitoring** - Screen is scanned every 250ms for matches
- **Real-time status** - Shows "Detector running" or "Match detected!"
- **Instant notifications** - Phone alerts you the moment a match is found
- **Keyboard shortcuts** - Use `Ctrl+T` or `F8` to quickly toggle

*Keep this running in the background while you queue for games!*

---

### 📈 Statistics Tab

![Statistics Tab](screenshots/App_Tab_3.png)

View your gaming activity and community stats:

**Your Activity:**
- **Games Found** - Total matches detected on your PC
- **Last Match** - Timestamp of your most recent match

**Community Stats:**
- **Total Users** - Active OmniCall users worldwide
- **Total Matches** - All matches found by the community
- **Total Notifications Sent** - Cumulative notifications delivered

*Click "Refresh" to update stats in real-time*

---

### 💬 Feedback Tab

![Feedback Tab](screenshots/App_Tab_4.png)

Share your thoughts directly with the developer:
- **Feedback text area** - Report bugs, suggest features, or share your wins
- **Word counter** - Track your message length (max 2000 words)
- **Submit button** - Send feedback instantly to the creator
- **Test notifications** - Verify your phone connection anytime

*Your feedback helps improve OmniCall for everyone!*

---

### 🛠️ Support Tab

![Support Tab](screenshots/App_Tab_5.png)

Support the project and keep development going:
- **Donation options** - PayPal and Binance details
- **Contact information** - Easy-to-copy email and IDs
- **Visual guide** - Clear instructions for sending contributions
- **Thank you message** - Every bit helps maintain and improve OmniCall

*If OmniCall helps you never miss a match, consider supporting! ❤️*

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

-  **No personal data** collected beyond device pairing and statiscts shown in the app itself. 
-  **Open source** - review the code yourself

**What we store:**
- Device ID (random, anonymous)
- Display name (you choose)
- FCM tokens (for notifications)
- Match statistics (count only)

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

- **PayPal**:  amrkhaled122@aucegypt.edu
- **Binance**: amrkhaled272@gmail.com

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

This tool is for **personal use only**. Use responsibly and in accordance with the Terms of Service of any games you play. The developer is not responsible for any consequences of using this software.

---

**Made with ❤️ by Amr Khaled**

*Star ⭐ this repo if you find it useful!*
