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
            },
            "detection": {"hough_dp": 1.2, "ball_min_radius": 8},
            "tracking": {"max_disappeared": 30},
            "ui": {"show_fps": True, "fullscreen": False},
            "replay": {"enabled": True, "output_dir": "test_replays"},
            "game": {"pocket_radius": 25},
            "web": {"enabled": False},
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

    @patch("poolmind.app.yaml.safe_load")
    @patch("builtins.open")
    def test_config_loading(self, mock_open, mock_yaml_load):
        """Test configuration file loading"""
        mock_yaml_load.return_value = self.config_data

        with patch("sys.argv", ["app.py", "--config", "test.yaml"]):
            with patch.object(self, "_mock_main_components"):
                main()

        mock_open.assert_called_with("test.yaml", "r")
        mock_yaml_load.assert_called_once()

    @patch("cv2.destroyAllWindows")
    @patch("cv2.waitKey", return_value=27)  # ESC key
    @patch("cv2.imshow")
    @patch("cv2.namedWindow")
    def test_opencv_window_setup(
        self, mock_namedwindow, mock_imshow, mock_waitkey, mock_destroy
    ):
        """Test OpenCV window setup and cleanup"""
        with self._patch_all_components():
            with patch("sys.argv", ["app.py", "--config", self.temp_config.name]):
                main()

        mock_namedwindow.assert_called_once_with("PoolMind", cv2.WINDOW_NORMAL)
        mock_destroy.assert_called_once()

    @patch("cv2.setWindowProperty")
    @patch("cv2.destroyAllWindows")
    @patch("cv2.waitKey", return_value=27)
    @patch("cv2.imshow")
    @patch("cv2.namedWindow")
    def test_fullscreen_mode(
        self,
        mock_namedwindow,
        mock_imshow,
        mock_waitkey,
        mock_destroy,
        mock_setwindowprop,
    ):
        """Test fullscreen mode setup"""
        # Enable fullscreen in config
        self.config_data["ui"]["fullscreen"] = True
        with open(self.temp_config.name, "w") as f:
            yaml.dump(self.config_data, f)

        with self._patch_all_components():
            with patch("sys.argv", ["app.py", "--config", self.temp_config.name]):
                main()

        mock_setwindowprop.assert_called_once_with(
            "PoolMind", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
        )

    @patch("threading.Thread")
    @patch("cv2.destroyAllWindows")
    @patch("cv2.waitKey", return_value=27)
    @patch("cv2.imshow")
    @patch("cv2.namedWindow")
    def test_web_server_startup(
        self, mock_namedwindow, mock_imshow, mock_waitkey, mock_destroy, mock_thread
    ):
        """Test web server thread startup when enabled"""
        # Enable web server
        self.config_data["web"]["enabled"] = True
        with open(self.temp_config.name, "w") as f:
            yaml.dump(self.config_data, f)

        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        with self._patch_all_components():
            with patch("sys.argv", ["app.py", "--config", self.temp_config.name]):
                main()

        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    def _patch_all_components(self):
        """Context manager to patch all component classes"""
        patches = [
            patch("poolmind.app.Camera", return_value=self._mock_camera()),
            patch("poolmind.app.MarkerHomography", return_value=Mock()),
            patch("poolmind.app.TableGeometry", return_value=Mock()),
            patch("poolmind.app.BallDetector", return_value=Mock()),
            patch("poolmind.app.CentroidTracker", return_value=Mock()),
            patch("poolmind.app.Overlay", return_value=self._mock_overlay()),
            patch("poolmind.app.ReplayRecorder", return_value=Mock()),
            patch("poolmind.app.GameEngine", return_value=self._mock_engine()),
            patch("poolmind.app.FrameHub", return_value=Mock()),
        ]

        class PatchContext:
            def __enter__(self):
                self.mocks = [p.__enter__() for p in patches]
                return self.mocks

            def __exit__(self, exc_type, exc_val, exc_tb):
                for p in reversed(patches):
                    p.__exit__(exc_type, exc_val, exc_tb)

        return PatchContext()

    def _mock_camera(self):
        """Create a mock camera that yields one frame then stops"""
        mock = Mock()
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock.frames.return_value = iter([test_frame])
        return mock

    def _mock_overlay(self):
        """Create a mock overlay that returns a frame"""
        mock = Mock()
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock.draw.return_value = test_frame
        return mock

    def _mock_engine(self):
        """Create a mock game engine"""
        mock = Mock()
        mock.get_state.return_value = {}
        mock.consume_events.return_value = []
        return mock

    def test_component_initialization_parameters(self):
        """Test that components are initialized with correct config parameters"""
        with patch("poolmind.app.Camera") as mock_camera:
            with self._patch_all_components():
                with patch("sys.argv", ["app.py", "--config", self.temp_config.name]):
                    try:
                        main()
                    except (AttributeError, ValueError, ImportError):
                        pass  # Expected due to incomplete mocking

            # Verify camera was initialized with correct parameters
            mock_camera.assert_called_once_with(index=0, width=1280, height=720, fps=30)

    def teardown_method(self):
        """Clean up test files"""
        import os

        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
