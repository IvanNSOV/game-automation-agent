"""Input simulation - mouse movement and clicking via Win32 API and PyDirectInput."""

import time
import threading
from typing import Tuple, Optional
from loguru import logger

try:
    import pydirectinput
    PYDIRECTINPUT_AVAILABLE = True
except ImportError:
    PYDIRECTINPUT_AVAILABLE = False
    logger.warning("pydirectinput not available")

try:
    import ctypes
    from ctypes import wintypes
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("Windows API not available")


class InputSimulator:
    """Simulate mouse input using Win32 API or PyDirectInput."""
    
    def __init__(
        self,
        method: str = "win32",
        max_speed_px: float = 50.0,
        enable_movement: bool = True,
        enable_clicks: bool = False,
        click_delay_ms: float = 50.0,
    ):
        """
        Initialize input simulator.
        
        Args:
            method: "win32" (recommended) or "pydirectinput"
            max_speed_px: Maximum pixels to move per call
            enable_movement: Enable mouse movement
            enable_clicks: Enable mouse clicks
            click_delay_ms: Delay between click and release
        """
        self.method = method
        self.max_speed_px = max_speed_px
        self.enable_movement = enable_movement
        self.enable_clicks = enable_clicks
        self.click_delay_ms = click_delay_ms
        
        # Validate method availability
        if method == "win32" and not WIN32_AVAILABLE:
            logger.warning("Win32 API not available, falling back to pydirectinput")
            self.method = "pydirectinput"
        
        if self.method == "pydirectinput" and not PYDIRECTINPUT_AVAILABLE:
            logger.warning("PyDirectInput not available, falling back to basic mouse control")
            self.method = "basic"
        
        if self.method == "win32":
            self._setup_win32()
        
        self.current_pos = (0.0, 0.0)
        self._lock = threading.Lock()
        
        logger.info(
            f"InputSimulator initialized (method={self.method}, "
            f"movement={enable_movement}, clicks={enable_clicks})"
        )
    
    def _setup_win32(self):
        """Setup Win32 API for mouse control."""
        self.SetCursorPos = ctypes.windll.user32.SetCursorPos
        self.SetCursorPos.argtypes = [wintypes.int, wintypes.int]
        self.SetCursorPos.restype = wintypes.bool
        
        self.GetCursorPos = ctypes.windll.user32.GetCursorPos
        self.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
        self.GetCursorPos.restype = wintypes.bool
        
        self.mouse_event = ctypes.windll.user32.mouse_event
        logger.debug("Win32 API initialized for mouse control")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            (x, y) position
        """
        if self.method == "win32":
            point = wintypes.POINT()
            if self.GetCursorPos(ctypes.byref(point)):
                return (point.x, point.y)
        
        # Fallback
        return self.current_pos
    
    def move_mouse(self, x: int, y: int, smooth: bool = False):
        """
        Move mouse to absolute position.
        
        Args:
            x: Target X coordinate
            y: Target Y coordinate
            smooth: Apply smoothing (not implemented here, use MotionHumanizer)
        """
        if not self.enable_movement:
            return
        
        with self._lock:
            if self.method == "win32":
                try:
                    self.SetCursorPos(int(x), int(y))
                    self.current_pos = (x, y)
                except Exception as e:
                    logger.error(f"Win32 mouse movement failed: {e}")
            
            elif self.method == "pydirectinput":
                try:
                    pydirectinput.moveTo(int(x), int(y))
                    self.current_pos = (x, y)
                except Exception as e:
                    logger.error(f"PyDirectInput mouse movement failed: {e}")
    
    def move_mouse_by(self, delta_x: int, delta_y: int):
        """
        Move mouse by relative offset.
        
        Args:
            delta_x: Pixels to move in X direction
            delta_y: Pixels to move in Y direction
        """
        current = self.get_mouse_position()
        new_x = current[0] + delta_x
        new_y = current[1] + delta_y
        self.move_mouse(new_x, new_y)
    
    def left_click(self, x: int = None, y: int = None):
        """
        Perform left mouse click.
        
        Args:
            x: Click X coordinate (uses current position if None)
            y: Click Y coordinate (uses current position if None)
        """
        if not self.enable_clicks:
            return
        
        if x is not None and y is not None:
            self.move_mouse(x, y)
        
        if self.method == "win32":
            try:
                # Left mouse button down (0x0002) and up (0x0004)
                ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # Down
                time.sleep(self.click_delay_ms / 1000.0)
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # Up
            except Exception as e:
                logger.error(f"Win32 click failed: {e}")
        
        elif self.method == "pydirectinput":
            try:
                pydirectinput.click()
            except Exception as e:
                logger.error(f"PyDirectInput click failed: {e}")
    
    def right_click(self, x: int = None, y: int = None):
        """
        Perform right mouse click.
        
        Args:
            x: Click X coordinate (uses current position if None)
            y: Click Y coordinate (uses current position if None)
        """
        if not self.enable_clicks:
            return
        
        if x is not None and y is not None:
            self.move_mouse(x, y)
        
        if self.method == "win32":
            try:
                # Right mouse button down (0x0008) and up (0x0010)
                ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)  # Down
                time.sleep(self.click_delay_ms / 1000.0)
                ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)  # Up
            except Exception as e:
                logger.error(f"Win32 right click failed: {e}")
        
        elif self.method == "pydirectinput":
            try:
                pydirectinput.rightClick()
            except Exception as e:
                logger.error(f"PyDirectInput right click failed: {e}")
    
    def set_enabled(self, enabled: bool):
        """Enable/disable mouse movement."""
        self.enable_movement = enabled
        logger.info(f"Mouse movement {'enabled' if enabled else 'disabled'}")
