"""Unit tests for targeting module."""

import pytest
import math
from src.targeting import TargetCalculator
from src.detection import Detection


class TestTargetCalculator:
    """Test TargetCalculator class."""
    
    @pytest.fixture
    def calculator(self):
        """Create calculator fixture."""
        return TargetCalculator(
            screen_center=(400, 300),
            head_offset=0.2,
            min_distance_px=20,
            max_distance_px=500,
        )
    
    def test_initialization(self, calculator):
        """Test calculator initialization."""
        assert calculator.screen_center == (400, 300)
        assert calculator.head_offset == 0.2
    
    def test_get_best_target_empty(self, calculator):
        """Test with no detections."""
        result = calculator.get_best_target([])
        assert result is None
    
    def test_get_aim_point(self, calculator):
        """Test aim point calculation."""
        # Create detection with known bbox
        det = Detection(bbox=(100, 100, 200, 300), confidence=0.9, class_id=0, class_name="person")
        
        aim = calculator.get_aim_point(det)
        # Center is (150, 200), with head_offset=0.2, height=200, aim_y should be 200 - 40 = 160
        assert aim[0] == 150  # x stays at center
        assert aim[1] == 160  # y moved up by 20% of height
    
    def test_calculate_movement(self, calculator):
        """Test movement calculation."""
        det = Detection(bbox=(400, 250, 500, 350), confidence=0.9, class_id=0, class_name="person")
        
        movement = calculator.calculate_movement(det)
        
        assert "delta_x" in movement
        assert "delta_y" in movement
        assert "distance" in movement
        assert "direction_x" in movement
        assert "direction_y" in movement
    
    def test_distance_calculation(self):
        """Test distance utility."""
        p1 = (0, 0)
        p2 = (3, 4)  # 3-4-5 triangle
        distance = TargetCalculator._distance(p1, p2)
        assert abs(distance - 5.0) < 0.01
