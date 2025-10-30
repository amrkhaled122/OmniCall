# 🎯 Quick Reference

## For End Users

**Want to use OmniCall?** → See [README.md](README.md)

## For Contributors

**Want to contribute?** → See [CONTRIBUTING.md](CONTRIBUTING.md)

## For Deployers

**Setting up for production?** → See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## For Cloud Functions

**Deploying backend?** → See [CLOUD_FUNCTIONS_SETUP.md](CLOUD_FUNCTIONS_SETUP.md)

---

## 🔥 Common Commands

### Running the App
```bash
python pc_app/omnicall_app.py
```

### Building Executable
```bash
pyinstaller OmniCall.spec
```

### Deploying Cloud Functions
```bash
firebase deploy --only functions
```

### Checking Logs
```bash
firebase functions:log
```

### Installing Dependencies
```bash
pip install -r pc_app/requirements.txt
cd functions && npm install
```

---

## 📁 Project Structure

```
OmniCall/
├── pc_app/                    # 🖥️ Desktop app (Python/PyQt6)
├── functions/                 # ☁️ Cloud Functions (Node.js)
├── docs/                      # 📱 PWA (HTML/JS)
├── README.md                  # 📖 User documentation
├── CONTRIBUTING.md            # 🤝 Contribution guide
├── DEPLOYMENT_CHECKLIST.md    # ✅ Deployment steps
├── CLOUD_FUNCTIONS_SETUP.md   # ☁️ Backend setup
└── Accept.png                 # 🎯 Detection template
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Check Python 3.11+ installed |
| No notifications | Re-pair phone (scan QR) |
| Stats not loading | Check internet, click Refresh |
| Build fails | Update PyInstaller, check deps |
| Functions error | Check `firebase functions:log` |

---

## 🔗 Important Links

- **Repository**: https://github.com/amrkhaled122/OmniCall
- **PWA**: https://amrkhaled122.github.io/OmniCall/
- **Issues**: https://github.com/amrkhaled122/OmniCall/issues
- **Releases**: https://github.com/amrkhaled122/OmniCall/releases

---

**Questions?** Open an issue or email amrkhaled122@aucegypt.edu
