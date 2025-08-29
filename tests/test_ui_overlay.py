"""
Tests for UI overlay module
"""
from unittest.mock import Mock, patch

import numpy as np

from poolmind.ui.overlay import Overlay


class TestOverlay:
    """Test cases for Overlay class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = {"show_fps": True, "draw_ids": True, "draw_trails": True}

        # Mock table geometry
        self.mock_table = Mock()
        self.mock_table.back_project_points.return_value = [(100, 100), (200, 200)]
        self.mock_table.default_pockets.return_value = [(50, 50, 20), (150, 150, 20)]

        self.overlay = Overlay(self.config, self.mock_table)

    def test_overlay_initialization(self):
        """Test overlay initializes correctly"""
        assert self.overlay.show_fps is True
        assert self.overlay.draw_ids is True
        assert self.overlay.draw_trails is True
        assert self.overlay.table == self.mock_table
        assert self.overlay.trails == {}

    def test_overlay_default_config(self):
        """Test overlay with default configuration"""
        overlay = Overlay({}, self.mock_table)

        assert overlay.show_fps is True  # default
        assert overlay.draw_ids is True  # default
        assert overlay.draw_trails is True  # default

    def test_get_ball_color(self):
        """Test ball color mapping"""
        assert self.overlay._get_ball_color("cue") == (255, 255, 255)  # White
        assert self.overlay._get_ball_color("solid") == (0, 255, 0)  # Green
        assert self.overlay._get_ball_color("stripe") == (255, 0, 0)  # Blue
        assert self.overlay._get_ball_color("unknown") == (0, 255, 255)  # Yellow
        assert self.overlay._get_ball_color("invalid") == (
            0,
            255,
            255,
        )  # Default to yellow

    @patch("cv2.aruco.drawDetectedMarkers")
    @patch("cv2.circle")
    @patch("cv2.putText")
    def test_draw_with_tracks_and_markers(
        self, mock_puttext, mock_circle, mock_draw_markers
    ):
        """Test drawing with tracks and ArUco markers"""
        # Create test frame
        frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)

        # Test tracks - new format with color
        tracks = {1: (100, 200, 15, "cue"), 2: (300, 400, 15, "solid")}

        # Mock ArUco debug data
        debug_markers = (["corners"], ["ids"])

        fps = 30.0

        self.overlay.draw(frame_bgr, warped_bgr, h_inv, tracks, fps, debug_markers)

        # Verify ArUco markers were drawn
        mock_draw_markers.assert_called_once()

        # Verify circles were drawn (2 tracks)
        assert mock_circle.call_count == 2

        # Verify text was drawn (FPS + track labels)
        assert mock_puttext.call_count >= 3  # FPS + 2 track labels

    @patch("cv2.putText")
    def test_draw_with_old_track_format(self, mock_puttext):
        """Test drawing with old track format (x, y, radius only)"""
        frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)

        # Old format tracks - just (x, y, radius)
        tracks = {1: (100, 200, 15), 2: (300, 400, 15)}

        fps = 25.0
        debug_markers = None

        # Should not raise exception with old format
        result = self.overlay.draw(
            frame_bgr, warped_bgr, h_inv, tracks, fps, debug_markers
        )

        assert result is not None
        assert result.shape == frame_bgr.shape

    @patch("cv2.putText")
    def test_draw_trails_functionality(self, mock_puttext):
        """Test trail drawing functionality"""
        frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)

        tracks = {1: (100, 200, 15, "cue")}

        # Draw multiple times to build trail
        for i in range(5):
            tracks[1] = (100 + i * 10, 200 + i * 5, 15, "cue")
            self.overlay.draw(frame_bgr, warped_bgr, h_inv, tracks, 30.0, None)

        # Check trail was stored
        assert 1 in self.overlay.trails
        assert len(self.overlay.trails[1]) == 5

    def test_draw_trails_limit(self):
        """Test trail length is limited"""
        frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)

        tracks = {1: (100, 200, 15, "cue")}

        # Draw more than trail limit (60)
        for i in range(70):
            tracks[1] = (100 + i, 200 + i, 15, "cue")
            self.overlay.draw(frame_bgr, warped_bgr, h_inv, tracks, 30.0, None)

        # Trail should be limited to last 60 points
        assert len(self.overlay.trails[1]) == 60

    @patch("cv2.putText")
    def test_draw_without_fps(self, mock_puttext):
        """Test drawing with FPS display disabled"""
        config = {"show_fps": False, "draw_ids": True, "draw_trails": True}
        overlay = Overlay(config, self.mock_table)

        frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)
        tracks = {1: (100, 200, 15, "cue")}

        overlay.draw(frame_bgr, warped_bgr, h_inv, tracks, 30.0, None)

        # Should not draw FPS text
        fps_calls = [call for call in mock_puttext.call_args_list if "FPS" in str(call)]
        assert len(fps_calls) == 0

    @patch("cv2.putText")
    def test_draw_without_ids(self, mock_puttext):
        """Test drawing with ID labels disabled"""
        config = {"show_fps": True, "draw_ids": False, "draw_trails": True}
        overlay = Overlay(config, self.mock_table)

        frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)
        tracks = {1: (100, 200, 15, "cue")}

        overlay.draw(frame_bgr, warped_bgr, h_inv, tracks, 30.0, None)

        # Should only draw FPS, not track IDs
        id_calls = [call for call in mock_puttext.call_args_list if "ID" in str(call)]
        assert len(id_calls) == 0

    def test_draw_without_trails(self):
        """Test drawing with trails disabled"""
        config = {"show_fps": True, "draw_ids": True, "draw_trails": False}
        overlay = Overlay(config, self.mock_table)

        frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)
        tracks = {1: (100, 200, 15, "cue")}

        # Draw multiple times
        for _ in range(5):
            overlay.draw(frame_bgr, warped_bgr, h_inv, tracks, 30.0, None)

        # No trails should be stored
        assert overlay.trails == {}

    def test_draw_empty_tracks(self):
        """Test drawing with no tracks"""
        frame_bgr = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)
        tracks = {}

        result = self.overlay.draw(frame_bgr, warped_bgr, h_inv, tracks, 30.0, None)

        assert result is not None
        assert result.shape == frame_bgr.shape

    @patch("cv2.circle")
    def test_draw_pockets_with_homography(self, mock_circle):
        """Test drawing pocket hints with homography"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        h_matrix = np.eye(3, dtype=np.float32)

        self.overlay.draw_pockets(frame, h_matrix)

        # Should call default_pockets and draw circles
        self.mock_table.default_pockets.assert_called_once_with(20)
        assert mock_circle.call_count >= 1

    def test_draw_pockets_without_homography(self):
        """Test drawing pocket hints without homography"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Should not crash when h_matrix is None
        self.overlay.draw_pockets(frame, None)

        # Should not call table methods
        self.mock_table.default_pockets.assert_not_called()
        self.mock_table.back_project_points.assert_not_called()

    @patch("cv2.circle")
    def test_draw_pockets_empty_pockets(self, mock_circle):
        """Test drawing pocket hints with empty pocket list"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        h_matrix = np.eye(3, dtype=np.float32)

        # Mock empty pocket list
        self.mock_table.default_pockets.return_value = []
        self.mock_table.back_project_points.return_value = []

        self.overlay.draw_pockets(frame, h_matrix)

        # Should not draw any circles
        mock_circle.assert_not_called()

    def test_frame_copy_independence(self):
        """Test that drawn frame is independent copy"""
        original_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        warped_bgr = np.zeros((400, 800, 3), dtype=np.uint8)
        h_inv = np.eye(3, dtype=np.float32)
        tracks = {}

        result = self.overlay.draw(
            original_frame, warped_bgr, h_inv, tracks, 30.0, None
        )

        # Result should be a copy, not the same object
        assert result is not original_frame
        assert result.shape == original_frame.shape
