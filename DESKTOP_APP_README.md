# 🎮 AI Story Generator - Desktop App

## What This Is

A **100% local** interactive AI story generator that runs entirely on your computer. No internet needed after initial setup, no hosting costs, complete privacy.

## How It Works

1. **Download** the app (one time)
2. **Double-click** to launch
3. **First run**: Downloads AI model automatically (~1.5GB, 5-10 minutes)
4. **Every run after**: Instant start, opens in your browser at `localhost:5000`

## Technical Details

- **Backend**: Flask server runs on `localhost:5000`
- **AI Model**: GPT-2 Medium (1.5GB) - automatically selected based on your hardware
- **Storage**: Stories saved to your Documents folder
- **Privacy**: Everything stays on your computer, zero data sent anywhere

## Installation

### For Users (Simple)

**Mac:**
```bash
# Download AIStoryGenerator-darwin-x64.zip
# Unzip
# Drag AIStoryGenerator.app to Applications
# Double-click to run
```

**Windows:**
```bash
# Download AIStoryGenerator-win32-x64.zip
# Unzip
# Run AIStoryGenerator.exe
```

### For Developers (Build from source)

1. **Install Node.js** (for Electron packaging)
```bash
# Download from https://nodejs.org/
# Or use Homebrew:
brew install node
```

2. **Install Electron dependencies**
```bash
cd /Users/jordanhiggins/Desktop/Story_Generator
npm install
```

3. **Test in development mode**
```bash
npm start
# This will:
# - Start Flask server
# - Open Electron window
# - Load localhost:5000
```

4. **Package as desktop app**

For Mac:
```bash
npm run package-mac
# Creates: AIStoryGenerator-darwin-x64/AIStoryGenerator.app
```

For Windows (cross-compile on Mac):
```bash
npm run package-win
# Creates: AIStoryGenerator-win32-x64/AIStoryGenerator.exe
```

For Linux:
```bash
npm run package-linux
# Creates: AIStoryGenerator-linux-x64/AIStoryGenerator
```

## Distribution

### Option 1: GitHub Releases (Free)
```bash
# 1. Create release on GitHub
# 2. Upload packaged apps as attachments
# 3. Users download from yourwebsite.com → links to GitHub release
```

### Option 2: Your Website (Direct Download)
```bash
# Host the .zip files on your website
# Users click download button
# No hosting costs for the app itself (static files)
```

### Example Download Page for Your Website:
```html
<div class="download-section">
    <h1>AI Story Generator</h1>
    <p>Interactive storytelling powered by AI. Runs 100% on your computer.</p>
    
    <div class="download-buttons">
        <a href="/downloads/AIStoryGenerator-mac.zip" class="btn-download">
            <i class="fab fa-apple"></i> Download for Mac
            <span class="size">~80MB</span>
        </a>
        
        <a href="/downloads/AIStoryGenerator-windows.zip" class="btn-download">
            <i class="fab fa-windows"></i> Download for Windows
            <span class="size">~85MB</span>
        </a>
    </div>
    
    <div class="info">
        <p><strong>First run:</strong> Downloads AI model (~1.5GB)</p>
        <p><strong>After that:</strong> Works offline, instant start</p>
        <p><strong>Privacy:</strong> All data stays on your computer</p>
    </div>
</div>
```

## System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB free space (for AI model)
- **OS**: macOS 10.13+, Windows 10+, or Linux
- **Internet**: Only needed for initial model download

## App Size

- **Download size**: 80-90MB (Electron + Python + Flask)
- **Installed size**: ~100MB
- **AI Model**: 1.5GB (downloads on first run)
- **Total**: ~1.6GB after setup

## How to Distribute on Your Website

### 1. Build the apps
```bash
npm run package-mac
npm run package-win
```

### 2. Zip them
```bash
cd AIStoryGenerator-darwin-x64
zip -r ../AIStoryGenerator-mac.zip AIStoryGenerator.app
cd ..

cd AIStoryGenerator-win32-x64  
zip -r ../AIStoryGenerator-windows.zip .
cd ..
```

### 3. Upload to your website
```bash
# Upload to yourwebsite.com/downloads/
# - AIStoryGenerator-mac.zip
# - AIStoryGenerator-windows.zip
```

### 4. Add download page
```html
<!-- yourwebsite.com/story-generator -->
<a href="/downloads/AIStoryGenerator-mac.zip">Download</a>
```

## Benefits of This Approach

✅ **Zero hosting costs** - No monthly server fees
✅ **Unlimited users** - Each user provides their own compute
✅ **Complete privacy** - Data never leaves user's computer
✅ **Offline capable** - Works without internet after setup
✅ **Better performance** - Uses full power of user's hardware
✅ **No rate limits** - Users can generate unlimited stories
✅ **Free AI** - No API costs ever

## User Experience

**First Launch:**
```
1. User downloads app from your website (80MB)
2. Installs like any app
3. Launches app
4. Window opens showing: "Downloading AI model... 1.5GB"
5. Progress bar (takes 5-10 minutes)
6. Model cached, app opens to story terminal
```

**Every Launch After:**
```
1. User double-clicks app icon
2. App opens in 2-3 seconds
3. Ready to generate stories
```

## Troubleshooting

### App won't start
- Check if port 5000 is available
- Look at Console.app (Mac) for error logs

### Model download fails
- Check internet connection
- Model downloads to: `~/.cache/huggingface/`
- Can manually download and place there

### Performance issues
- App uses 2-4GB RAM during generation
- Close other apps if memory is tight
- Smaller model can be configured in settings

## Development Notes

### File Structure
```
AIStoryGenerator.app/
├── electron-main.js          ← Electron entry point
├── package.json              ← Node dependencies
├── web_story_server_enhanced.py  ← Flask server
├── adaptive_story_engine_enhanced.py  ← AI engine
├── model_selector.py         ← Auto model selection
├── bin/python                ← Bundled Python
├── lib/python3.9/            ← Python dependencies
├── static/                   ← CSS/JS for UI
└── templates/                ← HTML templates
```

### How It Works Internally
1. Electron starts → `electron-main.js`
2. Spawns Python process → Runs Flask server
3. Waits for `localhost:5000` to respond
4. Opens BrowserWindow → Loads Flask UI
5. User interacts with web UI
6. Flask calls AI model locally
7. On quit → Kills Flask process

## Next Steps

1. **Install Node.js** → `brew install node`
2. **Install dependencies** → `npm install`
3. **Test it** → `npm start`
4. **Package it** → `npm run package-mac`
5. **Upload to website** → Zip and host the packaged app

Then users just download and run - **no Python, no terminal commands, just works!**
