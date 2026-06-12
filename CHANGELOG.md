# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-12

### Added
- Initial release with complete modular architecture
- High-performance screen capture (60+ FPS) using bettercam/mss
- YOLOv8 real-time object detection with CUDA support
- Advanced targeting system with head/torso prioritization
- Motion humanization with Lerp smoothing and noise generation
- Input simulation via Win32 API and PyDirectInput
- Comprehensive configuration system (YAML-based)
- Unit tests for all core modules
- Detailed documentation and quick-start guide
- Thread-safe multi-threaded architecture
- Extensive logging and debugging capabilities

### Features
- **Screen Capture Pipeline**: Bounding box capture with configurable resolution and FPS
- **Object Detection**: YOLOv8-based person detection with custom model support
- **Targeting Logic**: Multiple prioritization strategies (distance, center, size)
- **Humanization**: Ease-out curves, random noise, jitter for realistic motion
- **Input Control**: Win32 native mouse movement for DX11/DX12 game compatibility
- **Performance Optimization**: Skip frame detection, resolution downscaling, GPU acceleration
- **Debug Mode**: Bounding box visualization, FPS overlay, movement logging

### Technical Specs
- **Language**: Python 3.9+
- **OS**: Windows 10/11 (Win32 API)
- **GPU**: NVIDIA CUDA (optional, CPU fallback available)
- **Dependencies**: ultralytics, bettercam, pydirectinput, loguru, PyYAML

## Future Roadmap

### Planned Features
- [ ] Multi-target tracking
- [ ] Predictive leading (bullet lead calculation)
- [ ] Adaptive difficulty (learn from misses)
- [ ] Web-based configuration dashboard
- [ ] Performance telemetry and analytics
- [ ] Plugin system for extensibility
- [ ] macOS/Linux support (requires abstraction of Win32 API)
- [ ] Real-time video streaming debug view

### Known Limitations
- Windows-only (Win32 API dependency)
- Requires admin privileges for mouse input
- Works only with DX11/DX12 games (not older D3D9)
- No built-in anti-ban protection (educational use only)

### Performance Notes
- YOLOv8n: ~16ms inference (CUDA)
- Screen capture: <2ms per frame (bettercam)
- Total pipeline latency: ~20-30ms typical
- Memory: ~2GB VRAM (GPU), ~500MB RAM (CPU)

---

**Note**: This project is for educational purposes only. Unauthorized use in online multiplayer games violates Terms of Service and may result in account bans or legal action.
