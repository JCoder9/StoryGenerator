# 🚀 Building for Mac, Windows & Linux

## Quick Start - Build Everything at Once

```bash
# One command to rule them all:
./build_desktop_app.sh

# Choose option 6: Build + Zip for distribution
# Wait 5-10 minutes
# Get ready-to-upload files!
```

**Result:** Three files ready to upload to your website:
- `AIStoryGenerator-mac-v1.0.0.zip` (~80MB)
- `AIStoryGenerator-windows-v1.0.0.zip` (~85MB)  
- `AIStoryGenerator-linux-v1.0.0.tar.gz` (~80MB)

---

## Step-by-Step Guide

### Prerequisites (One-Time Setup)

**1. Install Node.js:**
```bash
# Mac (using Homebrew):
brew install node

# Or download from:
# https://nodejs.org/ (use LTS version)
```

**2. Install Dependencies:**
```bash
cd /Users/jordanhiggins/Desktop/Story_Generator
npm install
```

This downloads Electron and packaging tools (~200MB, takes 2-3 minutes).

---

## Building Apps

### Option 1: Interactive Build Script (Easiest)

```bash
./build_desktop_app.sh
```

**Menu Options:**
1. **Test app** - Quick test in Electron window (2 seconds)
2. **Build Mac only** - Creates Mac .app (~2 minutes)
3. **Build Windows only** - Creates Windows .exe (~2 minutes)
4. **Build Linux only** - Creates Linux executable (~2 minutes)
5. **Build all platforms** - Mac + Windows + Linux (~5 minutes)
6. **Build + Zip all** - Production-ready files (~6 minutes) ✨ **RECOMMENDED**
7. Exit

### Option 2: Manual Commands

**Build for specific platform:**
```bash
npm run package-mac      # macOS
npm run package-win      # Windows
npm run package-linux    # Linux
```

**Build all at once:**
```bash
npm run package-all
```

**Create distribution zips:**
```bash
npm run zip-all
```

**Build + Zip in one command:**
```bash
npm run build-all
```

---

## What Gets Created

### Mac Build
```
AIStoryGenerator-darwin-x64/
└── AIStoryGenerator.app/
    ├── Contents/
    │   ├── MacOS/
    │   │   └── AIStoryGenerator (executable)
    │   ├── Resources/
    │   │   ├── app/
    │   │   │   ├── web_story_server_enhanced.py
    │   │   │   ├── adaptive_story_engine_enhanced.py
    │   │   │   ├── model_selector.py
    │   │   │   ├── bin/python
    │   │   │   └── lib/python3.9/...
    │   │   └── electron.asar
    │   └── Info.plist
    └── (Double-click to run!)
```

**Distribution file:** `AIStoryGenerator-mac-v1.0.0.zip` (~80MB)

### Windows Build
```
AIStoryGenerator-win32-x64/
├── AIStoryGenerator.exe          (Launch this!)
├── resources/
│   └── app.asar
├── web_story_server_enhanced.py
├── adaptive_story_engine_enhanced.py
├── model_selector.py
├── bin/python.exe
├── lib/...
└── (All files bundled together)
```

**Distribution file:** `AIStoryGenerator-windows-v1.0.0.zip` (~85MB)

### Linux Build
```
AIStoryGenerator-linux-x64/
├── AIStoryGenerator              (Launch this!)
├── resources/
│   └── app.asar
├── web_story_server_enhanced.py
├── adaptive_story_engine_enhanced.py
├── model_selector.py
├── bin/python
└── lib/...
```

**Distribution file:** `AIStoryGenerator-linux-v1.0.0.tar.gz` (~80MB)

---

## Testing Your Builds

### Test Mac App:
```bash
open ./AIStoryGenerator-darwin-x64/AIStoryGenerator.app
```

### Test Windows App (if on Mac, need Windows VM/computer):
```bash
# Transfer to Windows machine, then:
AIStoryGenerator.exe
```

### Test Linux App (if on Mac, need Linux VM/computer):
```bash
./AIStoryGenerator-linux-x64/AIStoryGenerator
```

---

## Distribution on Your Website

### File Sizes (Approximate)

| Platform | Compressed | Uncompressed | Download Time (10 Mbps) |
|----------|-----------|--------------|------------------------|
| Mac | 80 MB | 250 MB | 64 seconds |
| Windows | 85 MB | 260 MB | 68 seconds |
| Linux | 80 MB | 250 MB | 64 seconds |

**Plus:** AI model auto-downloads on first run (~1.5GB, 10-15 minutes)

### Upload to Your Website

**1. Upload distribution files:**
```
yourwebsite.com/downloads/
├── AIStoryGenerator-mac-v1.0.0.zip
├── AIStoryGenerator-windows-v1.0.0.zip
└── AIStoryGenerator-linux-v1.0.0.tar.gz
```

**2. Create download page:**
```html
<h1>Download AI Story Generator</h1>

<a href="/downloads/AIStoryGenerator-mac-v1.0.0.zip">
  🍎 Download for Mac (80 MB)
</a>

<a href="/downloads/AIStoryGenerator-windows-v1.0.0.zip">
  🪟 Download for Windows (85 MB)
</a>

<a href="/downloads/AIStoryGenerator-linux-v1.0.0.tar.gz">
  🐧 Download for Linux (80 MB)
</a>

<p>First run downloads AI model (~1.5 GB)</p>
```

### Alternative: GitHub Releases (Free Hosting)

**1. Create release on GitHub:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**2. Upload files to release:**
- Go to GitHub → Releases → Create new release
- Upload the 3 distribution files
- Publish release

**3. Link from your website:**
```html
<a href="https://github.com/YourUsername/StoryGenerator/releases/latest">
  Download AI Story Generator
</a>
```

**Benefits:** 
- ✅ Free bandwidth
- ✅ No file size limits
- ✅ Automatic version management
- ✅ Download stats

---

## Platform-Specific Notes

### macOS
- **Format:** .app bundle inside .zip
- **Installation:** Unzip, drag to Applications
- **Security:** Users may need to right-click → Open first time (unsigned app)
- **Minimum OS:** macOS 10.13 (High Sierra) or later

**User Instructions:**
```
1. Download and unzip
2. Right-click AIStoryGenerator.app → Open
3. Click "Open" when security warning appears
4. Wait for AI model to download (first run only)
```

### Windows
- **Format:** Folder with .exe inside .zip
- **Installation:** Unzip, run .exe
- **Security:** May show "Windows protected your PC" - click "More info" → "Run anyway"
- **Minimum OS:** Windows 10 or later

**User Instructions:**
```
1. Download and unzip
2. Double-click AIStoryGenerator.exe
3. Click "Run anyway" if Windows SmartScreen appears
4. Wait for AI model to download (first run only)
```

### Linux
- **Format:** .tar.gz with executable
- **Installation:** Extract, chmod +x, run
- **Minimum:** Any modern Linux distro with GUI

**User Instructions:**
```bash
tar -xzf AIStoryGenerator-linux-v1.0.0.tar.gz
cd AIStoryGenerator-linux-x64
chmod +x AIStoryGenerator
./AIStoryGenerator
```

---

## Troubleshooting Builds

### "npm not found"
```bash
# Install Node.js first
brew install node
```

### "electron-packager command not found"
```bash
# Install dependencies
npm install
```

### Build fails on Mac for Windows
**This is normal!** Cross-platform builds work from Mac to Windows/Linux. The packager handles it automatically.

### "Permission denied" when running build script
```bash
chmod +x build_desktop_app.sh
./build_desktop_app.sh
```

### Builds are huge (>500MB)
Check that `.gitignore` excludes:
- `node_modules/`
- `AIStoryGenerator-*/`
- `__pycache__/`
- `*.pyc`

### App won't start after building
Make sure Python virtual environment is included:
- `bin/python` should exist
- `lib/python3.9/` should have all packages

---

## Updating Your App (Version 2.0)

**1. Update version in package.json:**
```json
{
  "version": "2.0.0"
}
```

**2. Rebuild:**
```bash
./build_desktop_app.sh
# Choose option 6
```

**3. New files created:**
```
AIStoryGenerator-mac-v2.0.0.zip
AIStoryGenerator-windows-v2.0.0.zip
AIStoryGenerator-linux-v2.0.0.tar.gz
```

**4. Upload and announce:**
- Upload to website/GitHub
- Update download links
- Notify users

---

## Advanced: Code Signing (Optional)

For production apps, consider code signing to remove security warnings:

### Mac
```bash
# Requires Apple Developer account ($99/year)
codesign --deep --force --sign "Developer ID Application: Your Name" AIStoryGenerator.app
```

### Windows
```bash
# Requires code signing certificate (~$100-300/year)
signtool sign /f certificate.pfx /p password AIStoryGenerator.exe
```

**Without signing:**
- Mac: Users see "App from unidentified developer"
- Windows: "Windows protected your PC"

Both can be bypassed (right-click → Open on Mac, "More info" → "Run anyway" on Windows), but signing makes it smoother.

---

## Quick Reference

**Test locally:**
```bash
./build_desktop_app.sh  # Option 1
```

**Build all platforms:**
```bash
./build_desktop_app.sh  # Option 6
```

**Manual build + zip:**
```bash
npm run build-all
```

**Upload to website:**
```bash
# Upload these 3 files:
ls -lh AIStoryGenerator-*.{zip,tar.gz}
```

**Done!** 🎉
