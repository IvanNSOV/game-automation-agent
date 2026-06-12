"""High-performance screen capture pipeline for gameplay."""

import numpy as np
import threading
import time
from typing import Tuple, Optional
from loguru import logger

try:
    import bettercam
    BETTERCAM_AVAILABLE = True
except ImportError:
    BETTERCAM_AVAILABLE = False
    logger.warning("bettercam not available, falling back to mss")

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    raise ImportError("Neither bettercam nor mss available. Install one with: pip install bettercam")


class ScreenCapture:
    """High-FPS screen capture with threaded buffering."""
    
    def __init__(
        self,
        left: int = 0,
        top: int = 0,
        width: int = 800,
        height: int = 600,
        fps: int = 60,
        use_bettercam: bool = True,
        monitor_index: int = 0,
    ):
        """
        Initialize screen capture.
        
        Args:
            left: Left edge of capture area (pixels)
            top: Top edge of capture area (pixels)
            width: Width of capture area (pixels)
            height: Height of capture area (pixels)
            fps: Target capture FPS
            use_bettercam: Use bettercam (True) or mss (False)
            monitor_index: Which monitor to capture from
        """
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.fps = fps
        self.monitor_index = monitor_index
        
        # Threading
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self._frame_count = 0
        self._fps_clock = time.time()
        self._actual_fps = 0
        
        # Backend selection
        if use_bettercam and BETTERCAM_AVAILABLE:
            self._init_bettercam()
        elif MSS_AVAILABLE:
            self._init_mss()
        else:
            raise RuntimeError("No screen capture backend available")
        
        logger.info(
            f"ScreenCapture initialized: {width}x{height} @ {left},{top} "
            f"(Backend: {self.backend})"
        )
    
    def _init_bettercam(self):
        """Initialize bettercam backend."""
        self.camera = bettercam.create(region=(self.left, self.top, self.width, self.height))
        self.backend = "bettercam"
    
    def _init_mss(self):
        """Initialize mss backend."""
        self.mss = mss.mss()
        self.monitor = self.mss.monitors[self.monitor_index + 1]  # +1 because index 0 is 'all'
        self.backend = "mss"
    
    def start(self):
        """Start capture thread."""
        if self._running:
            logger.warning("Capture already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info("Capture thread started")
    
    def stop(self):
        """Stop capture thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("Capture thread stopped")
    
    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        frame_delay = 1.0 / self.fps
        
        while self._running:
            start_time = time.time()
            
            # Capture frame
            if self.backend == "bettercam":
                frame = self.camera.grab()
                if frame is not None:
                    # bettercam returns RGBA, convert to BGR
                    frame = frame[:, :, :3][:, :, ::-1]
            else:
                # mss backend
                monitor_region = {
                    "left": self.left,
                    "top": self.top,
                    "width": self.width,
                    "height": self.height,
                }
                img = self.mss.grab(monitor_region)
                frame = np.array(img)
                # Convert RGBA to BGR
                frame = frame[:, :, :3][:, :, ::-1]
            
            # Update frame with thread safety
            if frame is not None:
                with self._lock:
                    self._frame = frame.copy()
                    self._frame_count += 1
                    
                    # Calculate actual FPS
                    elapsed = time.time() - self._fps_clock
                    if elapsed >= 1.0:
                        self._actual_fps = self._frame_count / elapsed
                        self._frame_count = 0
                        self._fps_clock = time.time()
            
            # Maintain target FPS
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_delay - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def capture(self) -> Optional[np.ndarray]:
        """
        Get the latest captured frame.
        
        Returns:
            Captured frame as numpy array (BGR format) or None if not available
        """
        with self._lock:
            if self._frame is not None:
                return self._frame.copy()
        return None
    
    def get_fps(self) -> float:
        """Get actual capture FPS."""
        with self._lock:
            return self._actual_fps
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get capture resolution (width, height)."""
        return self.width, self.height
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, *args):
        """Context manager exit."""
        self.stop()
        if hasattr(self, 'camera'):
            self.camera.release()
        if hasattr(self, 'mss'):
            self.mss.close()
