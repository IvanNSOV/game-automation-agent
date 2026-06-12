# Quick Start Guide - Autonomous Gameplay Agent

## Prerequisites

- **Python**: 3.9+ (tested on 3.11)
- **OS**: Windows 10/11 (Win32 API dependency)
- **GPU** (optional but recommended): NVIDIA with CUDA support
- **Dependencies**: See `requirements.txt`

---

## 5-Minute Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/gamingking243/game-automation-agent.git
cd game-automation-agent
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Installation time**: ~5-10 minutes (depends on CUDA availability)

### Step 4: Download Model (Auto-Download on First Run)
```bash
# Models auto-download from Ultralytics hub on first execution
# Or manually download:
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Step 5: Run Agent
```bash
python main.py
```

✅ **Agent is running!** Press `Ctrl+C` to stop.

---

## Configuration

### Quick Config Changes

Edit `config.yaml` to customize:

```yaml
# Make agent slower (more human-like)
humanization:
  smoothing_factor: 0.15  # Lower = smoother motion
  random_noise_px: 5      # Increase jitter

# Use custom model
model:
  path: "models/best.pt"  # Your trained model

# Adjust capture area
capture:
  width: 640    # Smaller = faster
  height: 480
```

**Restart agent after config changes** (Python re-reads config on startup).

---

## Test Installation

### Run Unit Tests
```bash
pip install pytest pytest-cov
pytest tests/ -v
```

### Quick Functionality Check
```bash
python -c "from src.detection import YOLOv8Detector; print('✓ Detection OK')"
python -c "from src.humanization import MotionHumanizer; print('✓ Humanization OK')"
python -c "from src.input_sim import InputSimulator; print('✓ Input Sim OK')"
```

---

## Running Agent in Different Modes

### Standard Mode
```bash
python main.py
```

### Debug Mode (Verbose Logging)
```bash
python main.py --debug
```

### Custom Configuration
```bash
python main.py --config my_config.yaml
```

### Override Model
```bash
python main.py --model models/best.pt --device cuda
```

---

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'ultralytics'"
**Fix**: `pip install ultralytics`

### ❌ "No module named 'bettercam'"
**Fix**: `pip install bettercam` (or uses `mss` fallback automatically)

### ❌ Mouse not moving
**Issues to check**:
1. Ensure game window is in focus
2. Verify `enable_movement: true` in config
3. Check Windows permissions (may need admin)
4. Try `method: "pydirectinput"` in config if Win32 fails

### ❌ Very slow detection (low FPS)
**Solutions**:
1. Reduce capture resolution:
   ```yaml
   capture:
     width: 640
     height: 480
   ```
2. Use smaller model:
   ```yaml
   model:
     path: "yolov8n.pt"  # nano is fastest
   ```
3. Increase skip frames:
   ```yaml
   performance:
     detection_skip_frames: 1  # Run detection every 2nd frame
   ```
4. Use GPU:
   ```yaml
   model:
     device: "cuda"
   ```

### ❌ CUDA not found (GPU not detected)
**Install CUDA**:
1. Download from NVIDIA
2. `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
3. Verify: `python -c "import torch; print(torch.cuda.is_available())"`

---

## Performance Tips

### Optimize for 60+ FPS

**Profile Current Performance**:
```python
# In main.py, log shows:
# "Stats: 1000 frames, 45.2 FPS avg, 78.3% detection rate"
```

**Improvement Checklist**:
- [ ] Use `yolov8n.pt` (nano model, fastest)
- [ ] Set `device: "cuda"` if GPU available
- [ ] Reduce capture area size
- [ ] Increase `detection_skip_frames`
- [ ] Lower confidence threshold slightly

### Memory Usage
- **VRAM**: ~2GB with nano model on GPU
- **RAM**: ~500MB with CPU only
- **Disk**: ~100MB for model weights

---

## Advanced Usage

### Use Custom Trained Model

1. **Train your own YOLO model**:
   ```bash
   yolo detect train data=your_dataset.yaml model=yolov8n.pt epochs=100 device=0
   ```

2. **Copy weights**:
   ```bash
   cp runs/detect/train/weights/best.pt models/best.pt
   ```

3. **Update config**:
   ```yaml
   model:
     path: "models/best.pt"
   ```

### Adjust Targeting Parameters

```yaml
targeting:
  # Aim higher on targets (for headshots)
  head_offset: 0.3          # 30% from top of bbox
  
  # Distance constraints
  min_distance_px: 30       # Ignore very close targets
  max_distance_px: 400      # Ignore far targets
  
  # Priority
  priority: "distance"      # "distance", "center", or "size"
```

### Fine-Tune Humanization

```yaml
humanization:
  smoothing_factor: 0.20    # Slower = more natural
  random_noise_px: 4        # Hand tremor simulation
  jitter_frequency: 0.4     # 40% chance of micro-jitter
  min_move_delay_ms: 15     # Human reaction time
  curve_type: "ease_out"    # "linear", "ease_out", or "bezier"
```

---

## Performance Benchmarks

On **RTX 3080 + i9-10900K**:

| Setting | FPS | Latency |
|---------|-----|----------|
| yolov8n (cuda) | 60+ | ~16ms |
| yolov8s (cuda) | 45+ | ~22ms |
| yolov8n (cpu) | 15 | ~65ms |
| yolov8s (cpu) | 8 | ~120ms |

---

## File Structure

```
game-automation-agent/
├── main.py                 # Entry point ← START HERE
├── config.yaml             # Configuration file
├── requirements.txt        # Dependencies
├── README.md               # Full documentation
├── QUICKSTART.md           # This file
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── screen_capture.py   # 60+ FPS capture
│   ├── detection.py        # YOLOv8 inference
│   ├── targeting.py        # Aim calculation
│   ├── humanization.py     # Lerp + noise
│   ├── input_sim.py        # Mouse control
│   └── logger.py           # Logging setup
│
├── models/
│   └── best.pt             # Your custom model (optional)
│
├── tests/
│   ├── test_detection.py
│   ├── test_targeting.py
│   └── test_humanization.py
│
└── debug_frames/           # Debug output (auto-created)
```

---

## Next Steps

1. ✅ Install and run with default config
2. 📖 Read full `README.md` for detailed documentation
3. ⚙️ Customize `config.yaml` for your system
4. 🧪 Run unit tests: `pytest tests/ -v`
5. 🎮 Point at your game and enjoy!

---

## Support

- **Issues**: Check GitHub Issues tab
- **Logs**: Check `agent.log` for detailed error messages
- **Questions**: See troubleshooting section above

---

**⚠️ Remember**: This is for educational and single-player testing only. Online multiplayer use violates game ToS and anti-cheat policies.

**Happy coding!** 🚀
