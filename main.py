"""Main entry point for autonomous gameplay agent."""

import argparse
import time
import sys
import yaml
from pathlib import Path
from typing import Dict, Optional

from src.logger import setup_logger
from src.screen_capture import ScreenCapture
from src.detection import YOLOv8Detector
from src.targeting import TargetCalculator
from src.humanization import MotionHumanizer
from src.input_sim import InputSimulator

logger = setup_logger(level="INFO", verbose=False)


class GameAgent:
    """Main autonomous gameplay agent."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize agent from configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_logger()
        self._initialize_components()
        
        self.running = False
        self.frame_count = 0
        self.detection_count = 0
        self.start_time = time.time()
        
        logger.info("GameAgent initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        path = Path(config_path)
        if not path.exists():
            logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
    
    def _setup_logger(self):
        """Configure logging based on config."""
        debug_config = self.config.get("debug", {})
        logging_config = self.config.get("logging", {})
        
        level = logging_config.get("level", "INFO")
        log_file = logging_config.get("file", None)
        verbose = debug_config.get("enabled", False)
        
        global logger
        logger = setup_logger(level=level, log_file=log_file, verbose=verbose)
    
    def _initialize_components(self):
        """Initialize all agent components."""
        # Screen capture
        cap_config = self.config.get("capture", {})
        self.screen_capture = ScreenCapture(
            left=cap_config.get("left", 400),
            top=cap_config.get("top", 300),
            width=cap_config.get("width", 800),
            height=cap_config.get("height", 600),
            fps=cap_config.get("fps", 60),
            use_bettercam=cap_config.get("use_bettercam", True),
        )
        
        # YOLOv8 detector
        model_config = self.config.get("model", {})
        self.detector = YOLOv8Detector(
            model=model_config.get("path", "yolov8n.pt"),
            confidence=model_config.get("confidence", 0.5),
            iou=model_config.get("iou", 0.45),
            device=model_config.get("device", "cuda"),
            half=model_config.get("half", True),
        )
        
        # Target calculator
        screen_center = (
            cap_config.get("left", 400) + cap_config.get("width", 800) // 2,
            cap_config.get("top", 300) + cap_config.get("height", 600) // 2,
        )
        target_config = self.config.get("targeting", {})
        self.target_calc = TargetCalculator(
            screen_center=screen_center,
            head_offset=target_config.get("head_offset", 0.2),
            min_distance_px=target_config.get("min_distance_px", 20),
            max_distance_px=target_config.get("max_distance_px", 500),
            priority=target_config.get("priority", "distance"),
        )
        
        # Motion humanizer
        human_config = self.config.get("humanization", {})
        self.humanizer = MotionHumanizer(
            smoothing_factor=human_config.get("smoothing_factor", 0.25),
            random_noise_px=human_config.get("random_noise_px", 3),
            jitter_frequency=human_config.get("jitter_frequency", 0.3),
            min_move_delay_ms=human_config.get("min_move_delay_ms", 10),
            curve_type=human_config.get("curve_type", "ease_out"),
        )
        
        # Input simulator
        input_config = self.config.get("input_simulation", {})
        self.input_sim = InputSimulator(
            method=input_config.get("method", "win32"),
            max_speed_px=input_config.get("max_speed_px", 50),
            enable_movement=input_config.get("enable_movement", True),
            enable_clicks=input_config.get("enable_clicks", False),
        )
        
        logger.info("All components initialized")
    
    def run(self):
        """Main agent loop."""
        logger.info("Starting agent...")
        self.running = True
        
        # Start screen capture
        self.screen_capture.start()
        time.sleep(0.5)  # Wait for capture to start
        
        try:
            while self.running:
                self._process_frame()
                
                # Check for exit key (in real implementation, would use keyboard listener)
                # For now, this is just a placeholder
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def _process_frame(self):
        """Process single frame."""
        # Capture frame
        frame = self.screen_capture.capture()
        if frame is None:
            time.sleep(0.001)
            return
        
        self.frame_count += 1
        
        # Detect targets
        detections = self.detector.detect_persons(frame)
        
        if detections:
            self.detection_count += 1
            
            # Get best target
            best_target = self.target_calc.get_best_target(detections)
            
            if best_target:
                # Calculate movement
                movement = self.target_calc.calculate_movement(best_target)
                
                # Check if should move
                if self.humanizer.should_move():
                    # Get humanized position
                    current_pos = self.input_sim.get_mouse_position()
                    humanized_pos = self.humanizer.update(
                        target_x=movement["target_x"],
                        target_y=movement["target_y"],
                        current_x=current_pos[0],
                        current_y=current_pos[1],
                    )
                    
                    # Move mouse
                    self.input_sim.move_mouse(humanized_pos[0], humanized_pos[1])
        
        # Maintain target FPS
        time.sleep(0.001)  # Small sleep to prevent busy loop
    
    def stop(self):
        """Stop the agent."""
        logger.info("Stopping agent...")
        self.running = False
        self.screen_capture.stop()
        
        # Print statistics
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        detection_rate = self.detection_count / self.frame_count if self.frame_count > 0 else 0
        
        logger.info(
            f"Agent stopped. Stats: {self.frame_count} frames, "
            f"{avg_fps:.1f} FPS avg, {detection_rate*100:.1f}% detection rate"
        )
    
    def set_debug_mode(self, enabled: bool):
        """Enable/disable debug mode."""
        debug_config = self.config.get("debug", {})
        debug_config["enabled"] = enabled
        logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Gameplay Agent - Computer Vision Based",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --config custom_config.yaml
  python main.py --debug
        """,
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with visualization",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Override model path from config",
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu"],
        help="Override device (cuda/cpu) from config",
    )
    
    args = parser.parse_args()
    
    # Check config file exists
    if not Path(args.config).exists():
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)
    
    # Initialize and run agent
    try:
        agent = GameAgent(config_path=args.config)
        
        if args.debug:
            agent.set_debug_mode(True)
        
        # Override config if arguments provided
        if args.model:
            agent.config["model"]["path"] = args.model
        if args.device:
            agent.config["model"]["device"] = args.device
        
        logger.info("="*60)
        logger.info("AUTONOMOUS GAMEPLAY AGENT STARTING")
        logger.info("="*60)
        logger.info(f"Config: {args.config}")
        logger.info(f"Debug: {args.debug}")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*60)
        
        # Run agent
        agent.run()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
