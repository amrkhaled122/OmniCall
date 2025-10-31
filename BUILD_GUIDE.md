# OmniCall Build & Distribution Guide

## Quick Build

### 1. Build the Executable

```powershell
# Activate your conda environment
conda activate OmniCall

# Build with PyInstaller
python -m PyInstaller OmniCall.spec --clean

# Output will be in: dist\OmniCall\
```

### 2. Test the Build

```powershell
# Run the executable to test
.\dist\OmniCall\OmniCall.exe
```

---

## Distribution Options

You have **two options** for distributing OmniCall:

### Option A: Portable ZIP (Quick & Simple)

**Use this if:** You want users to just unzip and run, no installer needed.

```powershell
# Create a clean distribution folder
New-Item -ItemType Directory -Path "OmniCall-v1.0.0-Portable" -Force

# Copy only essential files
Copy-Item "dist\OmniCall\OmniCall.exe" "OmniCall-v1.0.0-Portable\"
Copy-Item "dist\OmniCall\_internal" "OmniCall-v1.0.0-Portable\_internal" -Recurse
Copy-Item "dist\OmniCall\Accept.png" "OmniCall-v1.0.0-Portable\"
Copy-Item "README.md" "OmniCall-v1.0.0-Portable\"
Copy-Item "LICENSE" "OmniCall-v1.0.0-Portable\"

# Create ZIP
Compress-Archive -Path "OmniCall-v1.0.0-Portable\*" -DestinationPath "OmniCall-v1.0.0-Portable.zip" -Force

# Cleanup
Remove-Item "OmniCall-v1.0.0-Portable" -Recurse -Force
```

**Users will see:**
- `OmniCall.exe` (double-click to run)
- `_internal/` (folder with dependencies - can be hidden)
- `Accept.png` (template image)
- `README.md` and `LICENSE`

---

### Option B: Professional Installer (Recommended)

**Use this if:** You want proper installation with Start Menu shortcuts, desktop icon, and taskbar pinning.

#### Prerequisites

1. **Download Inno Setup** (free, open-source):
   - Visit: https://jrsoftware.org/isdl.php
   - Download and install Inno Setup 6.x
   - Default install location: `C:\Program Files (x86)\Inno Setup 6\`

#### Build Steps

```powershell
# Step 1: Build the executable (if not done yet)
python -m PyInstaller OmniCall.spec --clean

# Step 2: Compile the installer with Inno Setup
# Option 1: Using GUI
# - Right-click on installer.iss
# - Select "Compile"

# Option 2: Using command line
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss

# Output will be: installer_output\OmniCall-Setup-v1.0.0.exe
```

**Installer Features:**
- ✅ Installs to `C:\Program Files\OmniCall\` by default
- ✅ Hides `_internal` folder from user view
- ✅ Creates Start Menu shortcuts
- ✅ Optional desktop shortcut (user choice)
- ✅ Optional taskbar pin (user choice)
- ✅ Proper uninstaller
- ✅ Shows LICENSE during installation
- ✅ Checks for existing installation and offers to upgrade

**Users will only see:**
- Installation wizard
- After install: Start Menu entry, optional desktop icon, optional taskbar pin
- Clean install directory with just the .exe visible

---

## Windows Trust / Code Signing

### The "Untrusted Publisher" Warning

When users download and run your .exe, Windows SmartScreen shows a warning:
```
Windows protected your PC
Microsoft Defender SmartScreen prevented an unrecognized app from starting.
```

### Solutions

#### Option 1: Code Signing Certificate (Paid)

**Cost:** $100-$400/year  
**Time to setup:** 1-3 days  
**Benefit:** Windows immediately trusts your app

**Providers:**
- DigiCert (~$299/year): https://www.digicert.com/signing/code-signing-certificates
- Sectigo (~$199/year): https://sectigostore.com/code-signing
- SSL.com (~$249/year): https://www.ssl.com/certificates/code-signing/

**Process:**
1. Purchase certificate from provider
2. Verify your identity (ID, business docs)
3. Receive certificate (.pfx file)
4. Sign your .exe:
   ```powershell
   # Using signtool (included with Windows SDK)
   signtool sign /f "your-cert.pfx" /p "password" /t http://timestamp.digicert.com "dist\OmniCall\OmniCall.exe"
   ```
5. Rebuild installer with signed .exe

#### Option 2: Build Reputation (Free)

**Cost:** Free  
**Time to setup:** Instant  
**Benefit:** Windows learns to trust your app after ~100+ users download it

**How it works:**
- Keep distributing unsigned
- As more users click "More info" → "Run anyway"
- Windows SmartScreen builds reputation
- After 2-4 weeks, warning goes away for most users

**Tips:**
- Add note to README explaining the warning
- Create a quick video showing users how to bypass it
- Get friends/testers to download and run it (builds rep faster)

#### Option 3: User Instructions (Immediate)

Add this to your README.md and GitHub release notes:

```markdown
### First-Time Setup: Windows SmartScreen Warning

When you first run OmniCall, Windows may show a security warning because the app is unsigned.

**This is normal and safe.** Here's how to proceed:

1. Click **"More info"**
2. Click **"Run anyway"**
3. The app will start normally

Why this happens: OmniCall is a new, open-source app. Code signing certificates cost $200+/year. 
As more users download OmniCall, Windows SmartScreen will learn to trust it automatically.

Your antivirus may also scan the file—this is expected and the app is safe.
```

---

## Recommended Workflow

### For GitHub Releases

1. **Build the app:**
   ```powershell
   python -m PyInstaller OmniCall.spec --clean
   ```

2. **Create both distribution formats:**
   
   **Portable ZIP:**
   ```powershell
   .\create-portable.ps1  # Script provided below
   ```
   
   **Installer:**
   ```powershell
   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

3. **Upload to GitHub Release:**
   - `OmniCall-v1.0.0-Portable.zip` (for advanced users)
   - `OmniCall-Setup-v1.0.0.exe` (recommended for most users)

4. **Release notes template:**
   ```markdown
   ## 🚀 OmniCall v1.0.0
   
   ### Downloads
   
   - **[OmniCall-Setup-v1.0.0.exe](link)** - Recommended installer (14 MB)
     - Includes desktop shortcut and Start Menu entry
     - Easy uninstall via Windows Settings
   
   - **[OmniCall-v1.0.0-Portable.zip](link)** - Portable version (14 MB)
     - No installation required
     - Just extract and run OmniCall.exe
   
   ### ⚠️ First-Time Security Warning
   
   Windows may show a SmartScreen warning when first running OmniCall.
   Click "More info" → "Run anyway" to proceed. This is normal for new apps.
   
   ### What's New
   - Initial public release
   - Desktop app for Dota 2 match notifications
   - PWA for mobile notifications (iOS & Android)
   - Live stats and community features
   ```

---

## Helper Scripts

### create-portable.ps1

Save this as `create-portable.ps1`:

```powershell
# OmniCall Portable Distribution Builder

$version = "1.0.0"
$folderName = "OmniCall-v$version-Portable"
$zipName = "$folderName.zip"

Write-Host "Building portable distribution..." -ForegroundColor Cyan

# Clean up old builds
if (Test-Path $folderName) {
    Remove-Item $folderName -Recurse -Force
}
if (Test-Path $zipName) {
    Remove-Item $zipName -Force
}

# Create distribution folder
New-Item -ItemType Directory -Path $folderName | Out-Null

# Copy essential files
Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item "dist\OmniCall\OmniCall.exe" "$folderName\" -Force
Copy-Item "dist\OmniCall\_internal" "$folderName\_internal" -Recurse -Force
Copy-Item "dist\OmniCall\Accept.png" "$folderName\" -Force
Copy-Item "README.md" "$folderName\" -Force
Copy-Item "LICENSE" "$folderName\" -Force

# Create a quick start file
$quickStart = @"
# OmniCall - Quick Start

## How to Run

1. Double-click **OmniCall.exe** to launch the app
2. Follow the on-screen setup wizard to pair your phone
3. Keep the app running while playing Dota 2

## First-Time Windows Warning

If Windows shows a security warning:
1. Click "More info"
2. Click "Run anyway"

This is normal for new apps without expensive code signing certificates.

## Need Help?

- Documentation: README.md
- Issues: https://github.com/amrkhaled122/OmniCall/issues
- PWA: https://amrkhaled122.github.io/OmniCall/
"@

Set-Content -Path "$folderName\QUICK_START.txt" -Value $quickStart -Force

# Create ZIP
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
Compress-Archive -Path "$folderName\*" -DestinationPath $zipName -Force

# Cleanup
Remove-Item $folderName -Recurse -Force

Write-Host "✅ Build complete: $zipName" -ForegroundColor Green
Write-Host "Size: $([math]::Round((Get-Item $zipName).Length / 1MB, 2)) MB" -ForegroundColor Gray
```

Run it with:
```powershell
.\create-portable.ps1
```

---

## File Size Optimization

Current build is ~40-60 MB due to OpenCV. To reduce:

### Option 1: UPX Compression (Already enabled in .spec)

Already configured in `OmniCall.spec`:
```python
upx=True,
```

### Option 2: Exclude unused modules

Add to `OmniCall.spec` under `excludes`:
```python
excludes=['unittest', 'email', 'html', 'http', 'xml', 'pydoc'],
```

### Option 3: Strip unused OpenCV modules

OpenCV includes many modules you might not need. Consider using `opencv-python-headless` if you don't need GUI features (you do, so keep current).

---

## Testing Checklist

Before releasing:

- [ ] Build runs on clean Windows 10/11 machine
- [ ] All tabs load correctly
- [ ] QR pairing works
- [ ] Test notifications work
- [ ] Game detection works
- [ ] Stats refresh works
- [ ] Feedback submission works
- [ ] Support tab displays correctly with logos
- [ ] Installer creates shortcuts properly
- [ ] Uninstaller removes all files
- [ ] App survives restart
- [ ] Config persists across launches

---

## Troubleshooting Build Issues

### "UPX not found" Error

Download UPX:
```powershell
# Download UPX from GitHub
# https://github.com/upx/upx/releases
# Extract upx.exe to your PATH or same folder as spec file
```

### "Module not found" during build

Activate conda environment:
```powershell
conda activate OmniCall
```

### Large file size

Check if all dependencies are needed:
```powershell
pipdeptree  # Shows dependency tree
```

---

## Support

For build issues:
- Check PyInstaller docs: https://pyinstaller.org/
- Check Inno Setup docs: https://jrsoftware.org/ishelp/
- Open issue: https://github.com/amrkhaled122/OmniCall/issues
