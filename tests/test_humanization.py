"""Unit tests for humanization module."""

import pytest
from src.humanization import MotionHumanizer


class TestMotionHumanizer:
    """Test MotionHumanizer class."""
    
    @pytest.fixture
    def humanizer(self):
        """Create humanizer fixture."""
        return MotionHumanizer(
            smoothing_factor=0.25,
            random_noise_px=3.0,
            jitter_frequency=0.3,
            min_move_delay_ms=10.0,
        )
    
    def test_initialization(self, humanizer):
        """Test humanizer initialization."""
        assert 0.01 <= humanizer.smoothing_factor <= 1.0
        assert humanizer.random_noise_px >= 0
    
    def test_update_interpolation(self, humanizer):
        """Test Lerp interpolation."""
        humanizer.reset_position(0, 0)
        
        # Update towards (100, 100)
        pos = humanizer.update(100, 100, 0, 0)
        
        # With smoothing_factor=0.25, should move 25% of the way
        # Position should be between (0,0) and (100,100)
        assert pos[0] > 0
        assert pos[1] > 0
        assert pos[0] <= 100
        assert pos[1] <= 100
    
    def test_should_move(self, humanizer):
        """Test move delay simulation."""
        # First call should succeed (no prior move)
        result1 = humanizer.should_move()
        assert result1 is True
        
        # Immediate second call should fail (within min_move_delay_ms)
        result2 = humanizer.should_move()
        assert result2 is False
    
    def test_distance_to_target(self, humanizer):
        """Test distance calculation."""
        humanizer.reset_position(0, 0)
        humanizer.target_pos = (3, 4)  # 3-4-5 triangle
        
        distance = humanizer.distance_to_target()
        assert abs(distance - 5.0) < 0.01
    
    def test_easing_functions(self):
        """Test easing curve functions."""
        # Ease out cubic should return 1.0 at t=1.0
        result = MotionHumanizer._ease_out_cubic(1.0)
        assert abs(result - 1.0) < 0.01
        
        # Should return 0 at t=0
        result = MotionHumanizer._ease_out_cubic(0.0)
        assert abs(result - 0.0) < 0.01
