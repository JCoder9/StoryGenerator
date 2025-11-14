# 🚀 QUICK START: Build for Mac, Windows & Linux

## One-Line Command

```bash
./build_all.sh
```

**That's it!** Wait 5-10 minutes and you'll have three files ready to upload:
- ✅ `AIStoryGenerator-mac-v1.0.0.zip` (Mac)
- ✅ `AIStoryGenerator-windows-v1.0.0.zip` (Windows)
- ✅ `AIStoryGenerator-linux-v1.0.0.tar.gz` (Linux)

---

## First-Time Setup (One Time Only)

### 1. Install Node.js
```bash
brew install node
```

### 2. Install Dependencies
```bash
cd /Users/jordanhiggins/Desktop/Story_Generator
npm install
```

---

## Build Process

### Simple: One command for everything
```bash
./build_all.sh
```

### Interactive: Step-by-step menu
```bash
./build_desktop_app.sh
# Choose option 6: Build + Zip for distribution
```

### Manual: Individual platforms
```bash
npm run package-mac      # Mac only
npm run package-win      # Windows only
npm run package-linux    # Linux only
npm run package-all      # All three
npm run zip-all          # Compress all
npm run build-all        # Build + Compress
```

---

## What You Get

After building, you'll have these files in your project folder:

```
Story_Generator/
├── AIStoryGenerator-mac-v1.0.0.zip          ← Upload to website
├── AIStoryGenerator-windows-v1.0.0.zip      ← Upload to website
├── AIStoryGenerator-linux-v1.0.0.tar.gz     ← Upload to website
│
├── AIStoryGenerator-darwin-x64/             (source folder, don't upload)
├── AIStoryGenerator-win32-x64/              (source folder, don't upload)
└── AIStoryGenerator-linux-x64/              (source folder, don't upload)
```

---

## Upload to Your Website

### Option 1: Direct Upload

1. Upload the 3 distribution files to your web host
2. Create download links on your website
3. Done!

**Example file structure on your website:**
```
yourwebsite.com/
├── downloads/
│   ├── AIStoryGenerator-mac-v1.0.0.zip
│   ├── AIStoryGenerator-windows-v1.0.0.zip
│   └── AIStoryGenerator-linux-v1.0.0.tar.gz
└── story-generator.html
```

### Option 2: GitHub Releases (Free, Recommended)

1. Create release on GitHub
2. Upload the 3 files as release assets
3. Link from your website

**Benefits:**
- ✅ Free unlimited bandwidth
- ✅ Automatic download stats
- ✅ Version management
- ✅ CDN acceleration

---

## Test Your Builds

### Mac (on your current Mac):
```bash
open ./AIStoryGenerator-darwin-x64/AIStoryGenerator.app
```

### Windows (need Windows computer):
1. Transfer .zip to Windows PC
2. Unzip
3. Double-click `AIStoryGenerator.exe`

### Linux (need Linux computer):
1. Transfer .tar.gz to Linux PC
2. Extract: `tar -xzf AIStoryGenerator-linux-v1.0.0.tar.gz`
3. Run: `./AIStoryGenerator-linux-x64/AIStoryGenerator`

---

## User Installation Instructions

### Mac Users:
```
1. Download AIStoryGenerator-mac-v1.0.0.zip
2. Unzip the file
3. Drag AIStoryGenerator.app to Applications folder
4. Right-click → Open (first time only)
5. Click "Open" on security warning
6. Wait for AI model to download (~1.5GB, 10-15 min)
7. Start creating stories!
```

### Windows Users:
```
1. Download AIStoryGenerator-windows-v1.0.0.zip
2. Unzip to a folder (e.g., C:\AIStoryGenerator)
3. Double-click AIStoryGenerator.exe
4. Click "More info" → "Run anyway" if Windows SmartScreen appears
5. Wait for AI model to download (~1.5GB, 10-15 min)
6. Start creating stories!
```

### Linux Users:
```bash
# Download and extract
tar -xzf AIStoryGenerator-linux-v1.0.0.tar.gz
cd AIStoryGenerator-linux-x64

# Make executable
chmod +x AIStoryGenerator

# Run
./AIStoryGenerator

# First run downloads AI model (~1.5GB)
```

---

## Troubleshooting

### Build fails: "npm not found"
```bash
brew install node
```

### Build fails: "electron-packager not found"
```bash
npm install
```

### "Permission denied" on build scripts
```bash
chmod +x build_all.sh build_desktop_app.sh
```

### Mac app won't open: "Unidentified developer"
```
Right-click → Open → Click "Open" button
(Only needed first time)
```

### Windows: "Windows protected your PC"
```
Click "More info" → "Run anyway"
(Only needed first time)
```

---

## File Sizes

| Platform | Compressed | After Install | With AI Model |
|----------|-----------|---------------|---------------|
| Mac | 80 MB | 250 MB | 1.75 GB |
| Windows | 85 MB | 260 MB | 1.76 GB |
| Linux | 80 MB | 250 MB | 1.75 GB |

**First run:** Downloads 1.5GB AI model (one time)  
**After that:** App opens instantly

---

## Version Updates

To release version 2.0:

1. Update `package.json`:
   ```json
   "version": "2.0.0"
   ```

2. Rebuild:
   ```bash
   ./build_all.sh
   ```

3. New files created:
   ```
   AIStoryGenerator-mac-v2.0.0.zip
   AIStoryGenerator-windows-v2.0.0.zip
   AIStoryGenerator-linux-v2.0.0.tar.gz
   ```

4. Upload and update download links

---

## Complete Build Command Reference

```bash
# Quick test (no build)
npm start

# Build one platform
npm run package-mac
npm run package-win
npm run package-linux

# Build all platforms
npm run package-all

# Create distribution zips
npm run zip-mac
npm run zip-win
npm run zip-linux
npm run zip-all

# Build + Zip everything
npm run build-all

# OR use the automated script:
./build_all.sh

# OR use the interactive menu:
./build_desktop_app.sh
```

---

## Summary

**To build everything:**
```bash
./build_all.sh
```

**To upload to website:**
```bash
# Upload these 3 files:
AIStoryGenerator-mac-v1.0.0.zip
AIStoryGenerator-windows-v1.0.0.zip
AIStoryGenerator-linux-v1.0.0.tar.gz
```

**Users download, install, and run locally - no hosting costs for you!** 🎉
