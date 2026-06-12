"""Target calculation and aiming logic."""

import math
from typing import List, Tuple, Optional, Dict
from loguru import logger

from src.detection import Detection


class TargetCalculator:
    """Calculate targeting vectors and aim points."""
    
    def __init__(
        self,
        screen_center: Tuple[int, int] = (400, 300),
        head_offset: float = 0.2,
        min_distance_px: float = 20,
        max_distance_px: float = 500,
        priority: str = "distance",
    ):
        """
        Initialize target calculator.
        
        Args:
            screen_center: Center of game screen (x, y)
            head_offset: Offset to aim higher on target (0.0-1.0, where 1.0 is top)
            min_distance_px: Minimum distance to target (pixels)
            max_distance_px: Maximum distance to target (pixels)
            priority: Targeting priority ("distance", "center", "size")
        """
        self.screen_center = screen_center
        self.head_offset = max(0.0, min(1.0, head_offset))
        self.min_distance_px = min_distance_px
        self.max_distance_px = max_distance_px
        self.priority = priority
        
        logger.info(
            f"TargetCalculator initialized (center={screen_center}, "
            f"head_offset={head_offset}, priority={priority})"
        )
    
    def get_best_target(
        self,
        detections: List[Detection],
    ) -> Optional[Detection]:
        """
        Select best target from detections.
        
        Args:
            detections: List of Detection objects
        
        Returns:
            Best Detection or None
        """
        if not detections:
            return None
        
        # Filter by distance
        valid_targets = []
        for det in detections:
            center = det.center
            distance = self._distance(center, self.screen_center)
            
            if self.min_distance_px <= distance <= self.max_distance_px:
                valid_targets.append((det, distance))
        
        if not valid_targets:
            return None
        
        # Sort by priority
        if self.priority == "distance":
            # Nearest target
            best = min(valid_targets, key=lambda x: x[1])[0]
        elif self.priority == "center":
            # Closest to screen center
            best = min(valid_targets, key=lambda x: x[1])[0]
        elif self.priority == "size":
            # Largest target
            best = max(valid_targets, key=lambda x: x[0].area)[0]
        else:
            best = valid_targets[0][0]
        
        return best
    
    def get_aim_point(
        self,
        detection: Detection,
    ) -> Tuple[float, float]:
        """
        Calculate aim point on target (head/torso area).
        
        Args:
            detection: Target detection
        
        Returns:
            (x, y) aim coordinates
        """
        # Start at center
        center_x, center_y = detection.center
        
        # Apply head offset (move up on the target)
        offset_y = detection.height * self.head_offset
        aim_x = center_x
        aim_y = center_y - offset_y
        
        return (aim_x, aim_y)
    
    def calculate_movement(
        self,
        detection: Detection,
        current_pos: Tuple[float, float] = None,
    ) -> Dict[str, float]:
        """
        Calculate movement vector to target.
        
        Args:
            detection: Target detection
            current_pos: Current mouse position (defaults to screen center)
        
        Returns:
            Dict with movement data
        """
        if current_pos is None:
            current_pos = self.screen_center
        
        aim_point = self.get_aim_point(detection)
        
        # Calculate vector
        delta_x = aim_point[0] - current_pos[0]
        delta_y = aim_point[1] - current_pos[1]
        
        # Calculate distance
        distance = math.sqrt(delta_x**2 + delta_y**2)
        
        # Normalize direction
        if distance > 0:
            direction_x = delta_x / distance
            direction_y = delta_y / distance
        else:
            direction_x = 0
            direction_y = 0
        
        return {
            "delta_x": delta_x,
            "delta_y": delta_y,
            "distance": distance,
            "direction_x": direction_x,
            "direction_y": direction_y,
            "target_x": aim_point[0],
            "target_y": aim_point[1],
        }
    
    def get_all_targets_sorted(
        self,
        detections: List[Detection],
        sort_by: str = "distance",
    ) -> List[Tuple[Detection, float]]:
        """
        Get all valid targets sorted by criterion.
        
        Args:
            detections: List of Detection objects
            sort_by: Sort criterion ("distance", "size", "confidence")
        
        Returns:
            List of (Detection, sort_value) tuples
        """
        valid_targets = []
        
        for det in detections:
            center = det.center
            distance = self._distance(center, self.screen_center)
            
            if self.min_distance_px <= distance <= self.max_distance_px:
                if sort_by == "distance":
                    sort_value = distance
                elif sort_by == "size":
                    sort_value = -det.area  # Negative for descending
                elif sort_by == "confidence":
                    sort_value = -det.confidence  # Negative for descending
                else:
                    sort_value = distance
                
                valid_targets.append((det, sort_value))
        
        # Sort by value
        valid_targets.sort(key=lambda x: x[1])
        return valid_targets
    
    @staticmethod
    def _distance(
        p1: Tuple[float, float],
        p2: Tuple[float, float],
    ) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def set_screen_center(self, center: Tuple[int, int]):
        """Update screen center."""
        self.screen_center = center
        logger.debug(f"Screen center updated to {center}")
