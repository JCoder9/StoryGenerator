# AI Story Generator - Installation Guide

## Quick Start (5 minutes)

### Requirements
- **Python 3.9+** ([Download here](https://www.python.org/downloads/))
- **2GB free disk space** (for AI model download)
- **4GB RAM minimum** (8GB recommended)

### Installation Steps

#### 1. Extract the zip file
```bash
unzip StoryGenerator-v1.0.0-portable.zip
cd StoryGenerator
```

#### 2. Create virtual environment
```bash
# macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# Windows:
python -m venv venv
venv\Scripts\activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the app
```bash
# macOS/Linux:
./start_server.sh

# Windows:
python web_story_server_enhanced.py
```

#### 5. Open in browser
The app will automatically open at: **http://localhost:5000**

---

## What Happens on First Run

1. **Model Download** (~2.2GB) - Only happens once
   - Takes 5-10 minutes depending on internet speed
   - Downloads TinyLlama AI model automatically
   - Saved to `~/.cache/huggingface/`

2. **Server Starts**
   - Flask server runs on port 5000
   - Terminal UI loads in browser
   - Ready to generate stories!

---

## Usage

### Select a Genre
Choose from:
- 🔍 **Detective** - Solve mysteries
- 🚀 **Sci-Fi** - Space adventures
- 👻 **Horror** - Spooky tales
- ⚔️ **War** - Military operations
- 🗺️ **Adventure** - Epic quests

### Make Choices
- Read the story segment
- Click one of 3 choice buttons
- Wait ~10-15 seconds for AI to generate continuation
- Story builds based on your choices
- Auto-ends after 8 decisions

---

## Troubleshooting

### "Port 5000 already in use"
```bash
# macOS: Disable AirPlay Receiver
System Settings → General → AirPlay Receiver → Off

# Or use different port:
export PORT=8080
python web_story_server_enhanced.py
```

### "Model download failed"
```bash
# Check internet connection
# Or manually download from:
# https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

### "ImportError" or missing packages
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Story generation slow or stuck
- First generation takes longer (model loading)
- Subsequent generations: 10-15 seconds
- If stuck >30 seconds, refresh browser

---

## System Requirements

### Minimum
- **OS**: macOS 10.15+, Windows 10+, or Linux
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4GB
- **Disk**: 5GB free (2GB model + 3GB dependencies)
- **Internet**: Required for first-time model download

### Recommended
- **CPU**: Quad-core 2.5 GHz+
- **RAM**: 8GB
- **Disk**: SSD for faster loading

---

## Updating

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart server
./start_server.sh
```

---

## Uninstalling

1. Delete the `StoryGenerator` folder
2. Remove model cache (optional):
```bash
rm -rf ~/.cache/huggingface/hub/models--TinyLlama*
```

---

## Support

- **GitHub Issues**: https://github.com/JCoder9/StoryGenerator/issues
- **Documentation**: See `README.md`
- **Guides**: Check `.md` files in project folder

---

## Technical Details

- **AI Model**: TinyLlama 1.1B Chat
- **Framework**: Flask + PyTorch
- **Frontend**: Terminal-style UI (HTML/CSS/JS)
- **Generation**: ~150 tokens per continuation
- **Runs 100% locally** - no API keys needed!
