"""YOLOv8 object detection for target acquisition."""

import numpy as np
from typing import List, Dict, Tuple, Optional
from loguru import logger

try:
    from ultralytics import YOLO
except ImportError:
    raise ImportError("ultralytics not installed. Install with: pip install ultralytics")


class Detection:
    """Represents a single detection."""
    
    def __init__(self, bbox: Tuple[float, float, float, float], confidence: float, class_id: int, class_name: str):
        """
        Args:
            bbox: (x1, y1, x2, y2) in pixel coordinates
            confidence: Confidence score (0-1)
            class_id: Class ID from model
            class_name: Human-readable class name
        """
        self.x1, self.y1, self.x2, self.y2 = bbox
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
    
    @property
    def width(self) -> float:
        """Bounding box width."""
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        """Bounding box height."""
        return self.y2 - self.y1
    
    @property
    def center(self) -> Tuple[float, float]:
        """Bounding box center coordinates."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
    
    @property
    def area(self) -> float:
        """Bounding box area."""
        return self.width * self.height
    
    def __repr__(self) -> str:
        return (
            f"Detection({self.class_name}, conf={self.confidence:.2f}, "
            f"bbox=({self.x1:.0f},{self.y1:.0f})-({self.x2:.0f},{self.y2:.0f}))"
        )


class YOLOv8Detector:
    """YOLOv8 object detector for gameplay."""
    
    def __init__(
        self,
        model: str = "yolov8n.pt",
        confidence: float = 0.5,
        iou: float = 0.45,
        device: str = "cuda",
        half: bool = True,
        max_det: int = 10,
    ):
        """
        Initialize YOLOv8 detector.
        
        Args:
            model: Model path or name ("yolov8n.pt", "yolov8s.pt", etc.)
            confidence: Detection confidence threshold
            iou: IoU threshold for NMS
            device: "cuda" or "cpu"
            half: Use FP16 precision if available
            max_det: Maximum detections per frame
        """
        logger.info(f"Loading YOLOv8 model: {model}")
        
        self.model = YOLO(model)
        self.confidence = confidence
        self.iou = iou
        self.device = device
        self.half = half
        self.max_det = max_det
        
        # Move model to device
        self.model.to(device)
        if half and device == "cuda":
            self.model.half()
        
        logger.info(
            f"YOLOv8 loaded (device={device}, half={half}, "
            f"conf={confidence}, iou={iou})"
        )
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Run inference on frame.
        
        Args:
            frame: Input frame (BGR, uint8)
        
        Returns:
            List of Detection objects
        """
        if frame is None:
            return []
        
        # Run inference
        results = self.model(
            frame,
            conf=self.confidence,
            iou=self.iou,
            max_det=self.max_det,
            verbose=False,
        )
        
        detections = []
        if results and len(results) > 0:
            result = results[0]
            
            if hasattr(result, 'boxes') and result.boxes is not None:
                for box in result.boxes:
                    # Extract coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    
                    # Get class name
                    class_name = self.model.names.get(class_id, f"class_{class_id}")
                    
                    detection = Detection(
                        bbox=(x1, y1, x2, y2),
                        confidence=confidence,
                        class_id=class_id,
                        class_name=class_name,
                    )
                    detections.append(detection)
        
        return detections
    
    def detect_persons(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect only "person" class.
        
        Args:
            frame: Input frame (BGR, uint8)
        
        Returns:
            List of Detection objects with class_name="person"
        """
        all_detections = self.detect(frame)
        # COCO class 0 is 'person'
        return [d for d in all_detections if d.class_id == 0 or d.class_name == "person"]
    
    def set_confidence(self, confidence: float):
        """Update confidence threshold."""
        self.confidence = max(0.0, min(1.0, confidence))
        logger.info(f"Confidence threshold set to {self.confidence}")
    
    def set_iou(self, iou: float):
        """Update IoU threshold."""
        self.iou = max(0.0, min(1.0, iou))
        logger.info(f"IoU threshold set to {self.iou}")
