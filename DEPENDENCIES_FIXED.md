# 🔧 Dependency Installation & Troubleshooting Guide

## ✅ What Was Fixed

**Error:** `ModuleNotFoundError: No module named 'flask_cors'`

**Solution:** Installed all required dependencies:
- ✅ flask-cors
- ✅ transformers (Hugging Face)
- ✅ torch (PyTorch 2.2.2)
- ✅ accelerate
- ✅ appdirs

---

## 📦 Quick Install

If you ever need to reinstall dependencies:

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install flask flask-cors transformers torch accelerate appdirs
```

---

## 🚀 Starting the Server

### Method 1: Use the Startup Script (Recommended)
```bash
./start_server.sh
```

This script:
- Sets required environment variables (fixes OpenMP conflict)
- Checks all dependencies
- Starts the server automatically

### Method 2: Manual Start
```bash
export KMP_DUPLICATE_LIB_OK=TRUE
python3 web_story_server_enhanced.py
```

---

## ⚠️ Known Issues & Fixes

### Issue 1: OpenMP Library Conflict

**Error:**
```
OMP: Error #15: Initializing libiomp5.dylib, but found libomp.dylib already initialized.
```

**Solution:**
The `start_server.sh` script automatically sets `KMP_DUPLICATE_LIB_OK=TRUE`

If running manually:
```bash
export KMP_DUPLICATE_LIB_OK=TRUE
python3 web_story_server_enhanced.py
```

---

### Issue 2: PyTorch Version Too Old

**Error:**
```
Disabling PyTorch because PyTorch >= 2.1 is required but found 2.0.1
```

**Solution:**
```bash
pip install --upgrade torch torchvision torchaudio
```

Current version installed: **PyTorch 2.2.2** ✅

---

### Issue 3: Transformers Not Found

**Error:**
```
ModuleNotFoundError: No module named 'transformers'
```

**Solution:**
```bash
pip install transformers
```

---

### Issue 4: Using Anaconda Python

If you're using Anaconda (like you are), make sure to use Anaconda's pip:

```bash
/opt/anaconda3/bin/pip install [package-name]
```

Or activate your environment first:
```bash
conda activate base  # or your environment name
pip install [package-name]
```

---

## 📋 Verify Installation

Check all dependencies are working:

```bash
python3 -c "
import flask
import flask_cors  
import transformers
import torch
print('✅ Flask:', flask.__version__)
print('✅ Transformers:', transformers.__version__)
print('✅ PyTorch:', torch.__version__)
print('\n🎉 All dependencies OK!')
"
```

Expected output:
```
✅ Flask: 1.1.2 (or higher)
✅ Transformers: 4.57.1 (or higher)
✅ PyTorch: 2.2.2 (or higher)

🎉 All dependencies OK!
```

---

## 🐍 Python Environment Info

**Your setup:**
- Python: 3.9.13
- Location: `/opt/anaconda3/bin/python3`
- Environment: Anaconda base

**Installed packages:**
- transformers: 4.57.1
- torch: 2.2.2
- flask: 1.1.2
- flask-cors: 6.0.1
- accelerate: 1.10.1
- appdirs: 1.4.4

---

## 📁 Files Created

1. **`requirements.txt`** - List of all dependencies
2. **`start_server.sh`** - Startup script with environment fixes

---

## 🎯 Next Steps

1. **Start the server:**
   ```bash
   ./start_server.sh
   ```

2. **Open your browser:**
   ```
   http://localhost:5001
   ```

3. **First run will download the AI model (~2GB)**
   - Takes 5-10 minutes depending on internet
   - Only happens once
   - Model cached to `~/.cache/huggingface/`

---

## 🆘 Still Having Issues?

### Clear and Reinstall
```bash
pip uninstall transformers torch -y
pip install transformers torch accelerate
```

### Check Python Path
```bash
which python3
# Should show: /opt/anaconda3/bin/python3
```

### Check Installed Packages
```bash
pip list | grep -E "(flask|torch|transformers)"
```

---

## 💡 Performance Tips

After dependencies are working:

1. **First Model Download:** Be patient, ~2GB download
2. **Loading Time:** Model takes 10-30 seconds to load into RAM
3. **Generation Speed:** 2-5 seconds per story response on your Mac
4. **RAM Usage:** Expect 3-4GB while running

---

## ✅ Summary

**All errors fixed!** Your system now has:
- ✅ All required Python packages installed
- ✅ PyTorch upgraded to 2.2.2
- ✅ OpenMP conflict resolved via startup script
- ✅ Ready to run Llama-3.2-1B-Instruct model

**Just run:** `./start_server.sh`
