"""
Tests for PoolMind Main Application
"""
import tempfile
from unittest.mock import Mock, patch

import cv2
import numpy as np
import pytest
import yaml

from poolmind.app import main, parse_args


class TestPoolMindApp:
    """Test cases for main PoolMind application"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_config = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        self.config_data = {
            "camera": {"index": 0, "width": 1280, "height": 720, "fps": 30},
            "calibration": {
                "corner_ids": [0, 1, 2, 3],
                "table_w": 2000,
                "table_h": 1000,
                "ema_alpha": 0.2,
            },
            "detection": {
                "hough_dp": 1.2,
                "hough_min_dist": 16,
                "ball_min_radius": 8,
                "ball_max_radius": 18,
            },
            "tracking": {"max_disappeared": 30, "max_distance": 50},
            "ui": {"show_fps": True, "draw_ids": True, "fullscreen": False},
            "replay": {
                "enabled": True,
                "diff_threshold": 18.0,
                "output_dir": "test_replays",
            },
            "game": {"pocket_radius": 25, "disappear_for_pot": 5},
            "web": {
                "enabled": False,  # Disable for testing
                "host": "127.0.0.1",
                "port": 8000,
            },
        }

        yaml.dump(self.config_data, self.temp_config)
        self.temp_config.close()

    def test_parse_args_default(self):
        """Test argument parsing with default config path"""
        with patch("sys.argv", ["app.py"]):
            args = parse_args()
            assert args.config == "config/config.yaml"

    def test_parse_args_custom_config(self):
        """Test argument parsing with custom config path"""
        test_config = "/path/to/custom/config.yaml"
        with patch("sys.argv", ["app.py", "--config", test_config]):
            args = parse_args()
            assert args.config == test_config

    @patch("cv2.destroyAllWindows")
    @patch("cv2.waitKey")
    @patch("cv2.imshow")
    @patch("cv2.setWindowProperty")
    @patch("cv2.namedWindow")
    @patch("poolmind.app.ReplayRecorder")
    @patch("poolmind.app.FrameHub")
    @patch("poolmind.app.GameEngine")
    @patch("poolmind.app.Overlay")
    @patch("poolmind.app.CentroidTracker")
    @patch("poolmind.app.BallDetector")
    @patch("poolmind.app.TableGeometry")
    @patch("poolmind.app.MarkerHomography")
    @patch("poolmind.app.Camera")
    def test_main_initialization(
        self,
        mock_camera,
        mock_homography,
        mock_table,
        mock_detector,
        mock_tracker,
        mock_overlay,
        mock_engine,
        mock_hub,
        mock_replay,
        mock_namedwindow,
        mock_setwindowprop,
        mock_imshow,
        mock_waitkey,
        mock_destroywindows,
    ):
        """Test main function initializes all components correctly"""

        # Mock camera to provide frames and then stop
        mock_camera_instance = Mock()
        mock_camera_instance.frames.return_value = iter(
            [np.zeros((720, 1280, 3), dtype=np.uint8)]  # One test frame
        )
        mock_camera.return_value = mock_camera_instance

        # Mock other components
        mock_homography_instance = Mock()
        mock_homography_instance.homography_from_frame.return_value = (None, None, None)
        mock_homography.return_value = mock_homography_instance

        mock_table_instance = Mock()
        mock_table_instance.warp.return_value = None
        mock_table.return_value = mock_table_instance

        mock_detector_instance = Mock()
        mock_detector_instance.detect.return_value = []
        mock_detector.return_value = mock_detector_instance

        mock_tracker_instance = Mock()
        mock_tracker_instance.update.return_value = {}
        mock_tracker.return_value = mock_tracker_instance

        mock_engine_instance = Mock()
        mock_engine_instance.get_state.return_value = {}
        mock_engine_instance.consume_events.return_value = []
        mock_engine.return_value = mock_engine_instance

        mock_overlay_instance = Mock()
        mock_overlay_instance.draw.return_value = np.zeros(
            (720, 1280, 3), dtype=np.uint8
        )
        mock_overlay.return_value = mock_overlay_instance

        mock_replay_instance = Mock()
        mock_replay.return_value = mock_replay_instance

        mock_hub_instance = Mock()
        mock_hub.return_value = mock_hub_instance

        # Mock escape key press to exit
        mock_waitkey.return_value = 27  # ESC key

        # Mock arguments
        with patch("sys.argv", ["app.py", "--config", self.temp_config.name]):
            main()

        # Verify components were initialized with correct config sections
        mock_camera.assert_called_once_with(index=0, width=1280, height=720, fps=30)
        mock_homography.assert_called_once()
        mock_table.assert_called_once()
        mock_detector.assert_called_once()
        mock_tracker.assert_called_once()
        mock_overlay.assert_called_once()
        mock_engine.assert_called_once()
        mock_replay.assert_called_once()
        mock_hub.assert_called_once()

        # Verify CV2 window setup
        mock_namedwindow.assert_called_once_with("PoolMind", cv2.WINDOW_NORMAL)

        # Verify cleanup
        mock_camera_instance.release.assert_called_once()
        mock_destroywindows.assert_called_once()

    @patch("cv2.destroyAllWindows")
    @patch("cv2.waitKey")
    @patch("cv2.imshow")
    @patch("cv2.setWindowProperty")
    @patch("cv2.namedWindow")
    @patch("poolmind.app.ReplayRecorder")
    @patch("poolmind.app.FrameHub")
    @patch("poolmind.app.GameEngine")
    @patch("poolmind.app.Overlay")
    @patch("poolmind.app.CentroidTracker")
    @patch("poolmind.app.BallDetector")
    @patch("poolmind.app.TableGeometry")
    @patch("poolmind.app.MarkerHomography")
    @patch("poolmind.app.Camera")
    def test_main_fullscreen_mode(
        self,
        mock_camera,
        mock_homography,
        mock_table,
        mock_detector,
        mock_tracker,
        mock_overlay,
        mock_engine,
        mock_hub,
        mock_replay,
        mock_namedwindow,
        mock_setwindowprop,
        mock_imshow,
        mock_waitkey,
        mock_destroywindows,
    ):
        """Test main function with fullscreen enabled"""

        # Update config to enable fullscreen
        self.config_data["ui"]["fullscreen"] = True
        with open(self.temp_config.name, "w") as f:
            yaml.dump(self.config_data, f)

        # Mock components (simplified)
        self._mock_components(
            mock_camera,
            mock_homography,
            mock_table,
            mock_detector,
            mock_tracker,
            mock_overlay,
            mock_engine,
            mock_hub,
            mock_replay,
        )

        mock_waitkey.return_value = 27  # ESC key

        with patch("sys.argv", ["app.py", "--config", self.temp_config.name]):
            main()

        # Verify fullscreen was set
        mock_setwindowprop.assert_called_once_with(
            "PoolMind", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
        )

    @patch("threading.Thread")
    @patch("cv2.destroyAllWindows")
    @patch("cv2.waitKey")
    @patch("cv2.imshow")
    @patch("cv2.namedWindow")
    @patch("poolmind.app.ReplayRecorder")
    @patch("poolmind.app.FrameHub")
    @patch("poolmind.app.GameEngine")
    @patch("poolmind.app.Overlay")
    @patch("poolmind.app.CentroidTracker")
    @patch("poolmind.app.BallDetector")
    @patch("poolmind.app.TableGeometry")
    @patch("poolmind.app.MarkerHomography")
    @patch("poolmind.app.Camera")
    def test_main_web_server_enabled(
        self,
        mock_camera,
        mock_homography,
        mock_table,
        mock_detector,
        mock_tracker,
        mock_overlay,
        mock_engine,
        mock_hub,
        mock_replay,
        mock_namedwindow,
        mock_imshow,
        mock_waitkey,
        mock_destroywindows,
        mock_thread,
    ):
        """Test main function with web server enabled"""

        # Enable web server in config
        self.config_data["web"]["enabled"] = True
        with open(self.temp_config.name, "w") as f:
            yaml.dump(self.config_data, f)

        # Mock components
        self._mock_components(
            mock_camera,
            mock_homography,
            mock_table,
            mock_detector,
            mock_tracker,
            mock_overlay,
            mock_engine,
            mock_hub,
            mock_replay,
        )

        mock_waitkey.return_value = 27  # ESC key
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        with patch("sys.argv", ["app.py", "--config", self.temp_config.name]):
            main()

        # Verify web server thread was started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @patch("cv2.destroyAllWindows")
    @patch("cv2.waitKey")
    @patch("cv2.imshow")
    @patch("cv2.namedWindow")
    @patch("poolmind.app.ReplayRecorder")
    @patch("poolmind.app.FrameHub")
    @patch("poolmind.app.GameEngine")
    @patch("poolmind.app.Overlay")
    @patch("poolmind.app.CentroidTracker")
    @patch("poolmind.app.BallDetector")
    @patch("poolmind.app.TableGeometry")
    @patch("poolmind.app.MarkerHomography")
    @patch("poolmind.app.Camera")
    def test_main_processing_pipeline(
        self,
        mock_camera,
        mock_homography,
        mock_table,
        mock_detector,
        mock_tracker,
        mock_overlay,
        mock_engine,
        mock_hub,
        mock_replay,
        mock_namedwindow,
        mock_imshow,
        mock_waitkey,
        mock_destroywindows,
    ):
        """Test the main processing pipeline with valid data"""

        # Setup mock components with realistic behavior
        mock_camera_instance = Mock()
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_camera_instance.frames.return_value = iter([test_frame])
        mock_camera.return_value = mock_camera_instance

        # Mock homography detection
        mock_homography_instance = Mock()
        test_h = np.eye(3, dtype=np.float32)
        test_h_inv = np.eye(3, dtype=np.float32)
        mock_homography_instance.homography_from_frame.return_value = (
            test_h,
            test_h_inv,
            None,
        )
        mock_homography.return_value = mock_homography_instance

        # Mock table warping
        mock_table_instance = Mock()
        warped_frame = np.zeros((400, 800, 3), dtype=np.uint8)
        mock_table_instance.warp.return_value = warped_frame
        mock_table.return_value = mock_table_instance

        # Mock ball detection
        mock_detector_instance = Mock()
        mock_detector_instance.detect.return_value = [(100, 200, 15), (300, 400, 15)]
        mock_detector.return_value = mock_detector_instance

        # Mock tracking
        mock_tracker_instance = Mock()
        mock_tracker_instance.update.return_value = {
            1: (100, 200, 15),
            2: (300, 400, 15),
        }
        mock_tracker.return_value = mock_tracker_instance

        # Mock game engine
        mock_engine_instance = Mock()
        mock_engine_instance.get_state.return_value = {"active_balls": 2}
        mock_engine_instance.consume_events.return_value = [{"type": "ball_detected"}]
        mock_engine.return_value = mock_engine_instance

        # Mock overlay
        mock_overlay_instance = Mock()
        output_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_overlay_instance.draw.return_value = output_frame
        mock_overlay.return_value = mock_overlay_instance

        # Mock other components
        mock_hub_instance = Mock()
        mock_hub.return_value = mock_hub_instance
        mock_replay_instance = Mock()
        mock_replay.return_value = mock_replay_instance

        mock_waitkey.return_value = 27  # ESC key

        with patch("sys.argv", ["app.py", "--config", self.temp_config.name]):
            main()

        # Verify the processing pipeline was executed
        mock_homography_instance.homography_from_frame.assert_called_once()
        mock_table_instance.warp.assert_called_once_with(test_frame, test_h)
        mock_detector_instance.detect.assert_called_once_with(warped_frame)
        mock_tracker_instance.update.assert_called_once()
        mock_engine_instance.update.assert_called_once()
        mock_overlay_instance.draw.assert_called_once()
        mock_hub_instance.update_frame.assert_called_once()
        mock_replay_instance.process_frame.assert_called_once()

    def _mock_components(
        self,
        mock_camera,
        mock_homography,
        mock_table,
        mock_detector,
        mock_tracker,
        mock_overlay,
        mock_engine,
        mock_hub,
        mock_replay,
    ):
        """Helper method to setup basic component mocks"""
        # Camera
        mock_camera_instance = Mock()
        mock_camera_instance.frames.return_value = iter(
            [np.zeros((720, 1280, 3), dtype=np.uint8)]
        )
        mock_camera.return_value = mock_camera_instance

        # Other components with minimal setup
        mock_homography.return_value = Mock()
        mock_homography.return_value.homography_from_frame.return_value = (
            None,
            None,
            None,
        )

        mock_table.return_value = Mock()
        mock_table.return_value.warp.return_value = None

        mock_detector.return_value = Mock()
        mock_detector.return_value.detect.return_value = []

        mock_tracker.return_value = Mock()
        mock_tracker.return_value.update.return_value = {}

        mock_engine.return_value = Mock()
        mock_engine.return_value.get_state.return_value = {}
        mock_engine.return_value.consume_events.return_value = []

        mock_overlay.return_value = Mock()
        mock_overlay.return_value.draw.return_value = np.zeros(
            (720, 1280, 3), dtype=np.uint8
        )

        mock_hub.return_value = Mock()
        mock_replay.return_value = Mock()

    def teardown_method(self):
        """Clean up test files"""
        import os

        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
