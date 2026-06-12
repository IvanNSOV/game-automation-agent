"""Unit tests for detection module."""

import pytest
import numpy as np
from src.detection import Detection, YOLOv8Detector


class TestDetection:
    """Test Detection class."""
    
    def test_detection_properties(self):
        """Test detection properties."""
        bbox = (10, 20, 100, 200)
        det = Detection(bbox=bbox, confidence=0.95, class_id=0, class_name="person")
        
        assert det.width == 90
        assert det.height == 180
        assert det.center == (55, 110)
        assert det.area == 90 * 180
    
    def test_detection_repr(self):
        """Test detection string representation."""
        det = Detection((10, 20, 100, 200), confidence=0.95, class_id=0, class_name="person")
        repr_str = repr(det)
        assert "person" in repr_str
        assert "0.95" in repr_str


class TestYOLOv8Detector:
    """Test YOLOv8Detector class."""
    
    @pytest.fixture
    def detector(self):
        """Create detector fixture."""
        return YOLOv8Detector(model="yolov8n.pt", device="cpu")
    
    def test_detector_initialization(self, detector):
        """Test detector initialization."""
        assert detector.confidence == 0.5
        assert detector.device == "cpu"
        assert detector.model is not None
    
    def test_detect_with_dummy_frame(self, detector):
        """Test detection with dummy frame."""
        # Create dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Run detection
        detections = detector.detect(frame)
        
        # Should return list (may be empty for blank frame)
        assert isinstance(detections, list)
    
    def test_detect_persons(self, detector):
        """Test person-specific detection."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_persons(frame)
        
        assert isinstance(detections, list)
