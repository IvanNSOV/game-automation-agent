"""Autonomous Gameplay Agent - Core Package."""

__version__ = "1.0.0"
__author__ = "Ivan Smirnov"
__license__ = "MIT"

from src.screen_capture import ScreenCapture
from src.detection import YOLOv8Detector
from src.targeting import TargetCalculator
from src.humanization import MotionHumanizer
from src.input_sim import InputSimulator
from src.logger import setup_logger

__all__ = [
    "ScreenCapture",
    "YOLOv8Detector",
    "TargetCalculator",
    "MotionHumanizer",
    "InputSimulator",
    "setup_logger",
]
