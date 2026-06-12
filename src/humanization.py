"""Input humanization - motion smoothing and noise generation."""

import math
import random
import time
from typing import Tuple, Callable, Optional
from loguru import logger


class MotionHumanizer:
    """Apply human-like motion characteristics to targeting movements."""
    
    def __init__(
        self,
        smoothing_factor: float = 0.25,
        random_noise_px: float = 3.0,
        jitter_frequency: float = 0.3,
        min_move_delay_ms: float = 10.0,
        curve_type: str = "ease_out",
    ):
        """
        Initialize motion humanizer.
        
        Args:
            smoothing_factor: Lerp interpolation speed (0.0-1.0)
                - Lower = smoother, more natural motion
                - Higher = snappier, robotic motion
                - Recommended: 0.15-0.25 for anti-cheat evasion
            random_noise_px: Random pixel offset range (±value)
            jitter_frequency: Probability of jitter per frame (0.0-1.0)
            min_move_delay_ms: Minimum delay between moves (simulates reaction time)
            curve_type: Motion curve ("linear", "ease_out", "bezier")
        """
        self.smoothing_factor = max(0.01, min(1.0, smoothing_factor))
        self.random_noise_px = max(0.0, random_noise_px)
        self.jitter_frequency = max(0.0, min(1.0, jitter_frequency))
        self.min_move_delay_ms = max(0.0, min_move_delay_ms)
        self.curve_type = curve_type
        
        self.last_move_time = 0.0
        self.current_pos = (0.0, 0.0)
        self.target_pos = (0.0, 0.0)
        
        logger.info(
            f"MotionHumanizer initialized (smoothing={smoothing_factor}, "
            f"noise={random_noise_px}px, jitter={jitter_frequency}, "
            f"curve={curve_type})"
        )
    
    def update(
        self,
        target_x: float,
        target_y: float,
        current_x: float = None,
        current_y: float = None,
    ) -> Tuple[float, float]:
        """
        Calculate next movement position with humanization.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            current_x: Current X position (uses last position if None)
            current_y: Current Y position (uses last position if None)
        
        Returns:
            (x, y) next position to move to
        """
        if current_x is None:
            current_x = self.current_pos[0]
        if current_y is None:
            current_y = self.current_pos[1]
        
        self.target_pos = (target_x, target_y)
        
        # Apply smoothing curve
        if self.curve_type == "ease_out":
            t = self._ease_out_cubic(self.smoothing_factor)
        elif self.curve_type == "bezier":
            t = self._bezier_easing(self.smoothing_factor)
        else:  # linear
            t = self.smoothing_factor
        
        # Lerp interpolation
        next_x = current_x + (target_x - current_x) * t
        next_y = current_y + (target_y - current_y) * t
        
        # Apply jitter
        if random.random() < self.jitter_frequency:
            next_x += random.uniform(-self.random_noise_px, self.random_noise_px)
            next_y += random.uniform(-self.random_noise_px, self.random_noise_px)
        else:
            # Small random noise every frame
            if self.random_noise_px > 0:
                next_x += random.uniform(-self.random_noise_px * 0.5, self.random_noise_px * 0.5)
                next_y += random.uniform(-self.random_noise_px * 0.5, self.random_noise_px * 0.5)
        
        self.current_pos = (next_x, next_y)
        return (next_x, next_y)
    
    def should_move(self) -> bool:
        """
        Check if enough time has passed for next move (reaction time simulation).
        
        Returns:
            True if move is allowed, False to skip
        """
        current_time = time.time() * 1000  # Convert to milliseconds
        elapsed = current_time - self.last_move_time
        
        if elapsed >= self.min_move_delay_ms:
            self.last_move_time = current_time
            return True
        return False
    
    def reset_position(self, x: float, y: float):
        """Reset current position (e.g., when mouse teleports)."""
        self.current_pos = (x, y)
        self.target_pos = (x, y)
    
    def set_smoothing_factor(self, factor: float):
        """Update smoothing factor dynamically."""
        self.smoothing_factor = max(0.01, min(1.0, factor))
        logger.info(f"Smoothing factor updated to {factor}")
    
    def set_random_noise(self, noise_px: float):
        """Update random noise range."""
        self.random_noise_px = max(0.0, noise_px)
        logger.info(f"Random noise updated to ±{noise_px}px")
    
    @staticmethod
    def _ease_out_cubic(t: float) -> float:
        """
        Cubic ease-out curve: starts fast, ends slow (natural deceleration).
        This mimics human hand motion deceleration.
        """
        t = 1 - t
        return 1 - (t * t * t)
    
    @staticmethod
    def _bezier_easing(t: float) -> float:
        """
        Smooth cubic bezier curve for natural motion.
        Control points create an S-curve: slow start, fast middle, slow end.
        """
        # Smooth step (3t^2 - 2t^3)
        return t * t * (3 - 2 * t)
    
    @staticmethod
    def _quadratic_ease_out(t: float) -> float:
        """Quadratic ease-out: gentle deceleration."""
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def get_current_position(self) -> Tuple[float, float]:
        """Get current interpolated position."""
        return self.current_pos
    
    def get_target_position(self) -> Tuple[float, float]:
        """Get target position."""
        return self.target_pos
    
    def distance_to_target(self) -> float:
        """Get distance from current position to target."""
        return self.distance(self.current_pos, self.target_pos)
