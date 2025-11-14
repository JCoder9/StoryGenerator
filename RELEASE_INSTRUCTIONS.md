# GitHub Release Instructions

## Upload the Package to GitHub Releases

### Step 1: Go to Releases Page
Open in your browser:
```
https://github.com/JCoder9/StoryGenerator/releases
```

### Step 2: Create New Release
1. Click the green **"Draft a new release"** button (top right)

### Step 3: Configure Release
Fill in the form:

**Choose a tag:** Select `v1.0.0` from dropdown (already created)

**Release title:**
```
AI Story Generator v1.0.0
```

**Description:** (Copy and paste this)
```
## 🎮 AI Story Generator - First Stable Release

Interactive story generator powered by TinyLlama AI. Create branching narratives in multiple genres with AI-generated continuations.

### ✨ Features
- **5 Genres**: Detective 🔍, Sci-Fi 🚀, Horror 👻, War ⚔️, Adventure 🗺️
- **AI-Powered**: TinyLlama 1.1B Chat model for story generation
- **Context-Aware**: Choices adapt to story events
- **Terminal UI**: Retro terminal-style web interface
- **100% Local**: No API keys, no cloud services, runs entirely on your machine

### 📋 Requirements
- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- 5GB disk space (2GB for AI model, 3GB for dependencies)
- Internet connection for first-time model download

### 🚀 Quick Start
1. Download `StoryGenerator-v1.0.0-portable.zip` below
2. Extract the zip file
3. Follow instructions in `INSTALL.md`
4. Run `./start_server.sh` (or `python web_story_server_enhanced.py` on Windows)
5. Browser opens automatically at http://localhost:5000

### 📖 Documentation
- `INSTALL.md` - Complete installation guide
- `README.md` - Project overview
- `QUICK_START.md` - Getting started guide
- 25+ additional guides included in the package

### 🐛 Known Issues
- First story generation takes 20-30 seconds (model loading)
- Subsequent generations: 10-15 seconds
- macOS: Disable AirPlay Receiver if port 5000 is in use

### 💡 What's Next
See our [documentation](https://github.com/JCoder9/StoryGenerator) for advanced features and customization options.

---

**Supported Platforms**: macOS 10.15+, Windows 10+, Linux (Ubuntu 18.04+)
```

### Step 4: Attach Files
1. Scroll down to **"Attach binaries"** section
2. Drag and drop the file from your Desktop folder:
   ```
   StoryGenerator-v1.0.0-portable.zip
   ```
   OR click "Attach files by selecting them" and browse to:
   ```
   /Users/jordanhiggins/Desktop/Story_Generator/StoryGenerator-v1.0.0-portable.zip
   ```

### Step 5: Publish
1. **Uncheck** "Set as a pre-release" (leave unchecked)
2. **Check** "Set as the latest release"
3. Click green **"Publish release"** button

---

## ✅ After Publishing

Your download link will be:
```
https://github.com/JCoder9/StoryGenerator/releases/download/v1.0.0/StoryGenerator-v1.0.0-portable.zip
```

Users can also visit:
```
https://github.com/JCoder9/StoryGenerator/releases
```

And click the download link directly from the release page.

---

## 📊 Release Stats

GitHub will automatically track:
- Number of downloads
- Download per file
- Release views
- Traffic sources

Check stats at: `Insights → Traffic` on your repo

---

## 🔄 Future Updates

To create v1.1.0 later:
```bash
# Make your changes, commit them
git add .
git commit -m "Your changes"
git push origin main

# Create new tag
git tag -a v1.1.0 -m "Description of changes"
git push origin v1.1.0

# Create new zip
zip -r StoryGenerator-v1.1.0-portable.zip . -x [exclusions]

# Upload via GitHub Releases page (same process)
```

---

## Alternative: Command Line (if GitHub CLI is installed)

```bash
# Authenticate (one time)
gh auth login

# Create release
gh release create v1.0.0 \
  StoryGenerator-v1.0.0-portable.zip \
  --title "AI Story Generator v1.0.0" \
  --notes-file RELEASE_NOTES.md

# Check release
gh release view v1.0.0
```
