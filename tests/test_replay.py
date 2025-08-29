"""
Tests for PoolMind Replay Recording functionality
"""
import os
import tempfile
from unittest.mock import Mock, patch

import numpy as np
import pytest

from poolmind.services.replay import ReplayRecorder


class TestReplayRecorder:
    """Test cases for ReplayRecorder class"""

    def setup_method(self):
        """Set up test fixtures"""
        # Use temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

        self.replay_config = {
            "enabled": True,
            "diff_threshold": 20.0,
            "cooldown_frames": 30,
            "clip_seconds": 10,
            "output_dir": self.temp_dir,
        }

        self.cam_config = {"width": 1280, "height": 720, "fps": 30}

    def test_replay_recorder_initialization(self):
        """Test ReplayRecorder initializes correctly"""
        recorder = ReplayRecorder(self.replay_config, self.cam_config)

        assert recorder.enabled is True
        assert abs(recorder.threshold - 20.0) < 1e-6
        assert recorder.cooldown_frames == 30
        assert recorder.clip_seconds == 10
        assert recorder.outdir == self.temp_dir
        assert recorder.width == 1280
        assert recorder.height == 720
        assert recorder.fps == 30
        assert recorder.prev_gray is None
        assert recorder.cooldown == 0

    def test_replay_recorder_default_config(self):
        """Test ReplayRecorder with default configuration"""
        recorder = ReplayRecorder({}, self.cam_config)

        assert recorder.enabled is True  # default
        assert abs(recorder.threshold - 18.0) < 1e-6  # default
        assert recorder.cooldown_frames == 60  # default
        assert recorder.clip_seconds == 12  # default
        assert recorder.outdir == "replays"  # default

    def test_replay_recorder_disabled(self):
        """Test ReplayRecorder when disabled"""
        config = {"enabled": False}
        recorder = ReplayRecorder(config, self.cam_config)

        assert recorder.enabled is False

    @patch("cv2.cvtColor")
    def test_process_frame_first_frame(self, mock_cvtcolor):
        """Test processing the first frame"""
        recorder = ReplayRecorder(self.replay_config, self.cam_config)

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_gray = np.zeros((720, 1280), dtype=np.uint8)
        mock_cvtcolor.return_value = mock_gray

        recorder.process_frame(test_frame)

        # First frame should just store the gray version
        mock_cvtcolor.assert_called_once()
        assert recorder.prev_gray is not None
        np.testing.assert_array_equal(recorder.prev_gray, mock_gray)

    @patch("cv2.cvtColor")
    @patch("cv2.absdiff")
    def test_process_frame_no_motion(self, mock_absdiff, mock_cvtcolor):
        """Test processing frame with no significant motion"""
        recorder = ReplayRecorder(self.replay_config, self.cam_config)

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        gray_frame = np.zeros((720, 1280), dtype=np.uint8)

        mock_cvtcolor.return_value = gray_frame

        # Mock minimal difference
        diff_frame = np.ones((720, 1280), dtype=np.uint8) * 5  # Low difference
        mock_absdiff.return_value = diff_frame

        # Process first frame to set prev_gray
        recorder.process_frame(test_frame)

        # Process second frame - should not trigger recording
        with patch("subprocess.Popen") as mock_popen:
            recorder.process_frame(test_frame)
            mock_popen.assert_not_called()

    @patch("cv2.cvtColor")
    @patch("cv2.absdiff")
    @patch("subprocess.Popen")
    @patch("time.strftime")
    def test_process_frame_with_motion(
        self, mock_strftime, mock_popen, mock_absdiff, mock_cvtcolor
    ):
        """Test processing frame with significant motion"""
        recorder = ReplayRecorder(self.replay_config, self.cam_config)

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        gray_frame = np.zeros((720, 1280), dtype=np.uint8)

        mock_cvtcolor.return_value = gray_frame
        mock_strftime.return_value = "20231101-120000"

        # Mock high difference (motion detected)
        diff_frame = np.ones((720, 1280), dtype=np.uint8) * 50  # High difference
        mock_absdiff.return_value = diff_frame

        # Process first frame to set prev_gray
        recorder.process_frame(test_frame)

        # Process second frame - should trigger recording
        recorder.process_frame(test_frame)

        # Should have called ffmpeg
        mock_popen.assert_called_once()

        # Check cooldown was set
        assert recorder.cooldown == 30

    @patch("cv2.cvtColor")
    @patch("cv2.absdiff")
    @patch("subprocess.Popen")
    def test_cooldown_prevents_recording(self, mock_popen, mock_absdiff, mock_cvtcolor):
        """Test that cooldown prevents multiple recordings"""
        recorder = ReplayRecorder(self.replay_config, self.cam_config)

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        gray_frame = np.zeros((720, 1280), dtype=np.uint8)

        mock_cvtcolor.return_value = gray_frame

        # Mock high difference
        diff_frame = np.ones((720, 1280), dtype=np.uint8) * 50
        mock_absdiff.return_value = diff_frame

        # Set cooldown manually
        recorder.cooldown = 10
        recorder.prev_gray = gray_frame

        # Process frame - should not trigger recording due to cooldown
        recorder.process_frame(test_frame)

        mock_popen.assert_not_called()
        assert recorder.cooldown == 9  # Decremented

    @patch("cv2.cvtColor")
    def test_process_frame_disabled(self, mock_cvtcolor):
        """Test processing frame when recorder is disabled"""
        config = {"enabled": False}
        recorder = ReplayRecorder(config, self.cam_config)

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        recorder.process_frame(test_frame)

        # Should not process anything when disabled
        mock_cvtcolor.assert_not_called()

    @patch("cv2.cvtColor")
    @patch("cv2.absdiff")
    @patch("subprocess.Popen")
    def test_ffmpeg_command_construction(self, mock_popen, mock_absdiff, mock_cvtcolor):
        """Test that ffmpeg command is constructed correctly"""
        recorder = ReplayRecorder(self.replay_config, self.cam_config)

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        gray_frame = np.zeros((720, 1280), dtype=np.uint8)

        mock_cvtcolor.return_value = gray_frame

        # Mock high difference
        diff_frame = np.ones((720, 1280), dtype=np.uint8) * 50
        mock_absdiff.return_value = diff_frame

        # Process frames to trigger recording
        recorder.process_frame(test_frame)
        recorder.process_frame(test_frame)

        # Check ffmpeg was called with correct parameters
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][
            0
        ]  # First positional argument (command list)

        assert "ffmpeg" in call_args
        assert "-f" in call_args
        assert "v4l2" in call_args
        assert "-framerate" in call_args
        assert "30" in call_args
        assert "-video_size" in call_args
        assert "1280x720" in call_args
        assert "-t" in call_args
        assert "10" in call_args

    @patch("cv2.cvtColor")
    @patch("cv2.absdiff")
    @patch("subprocess.Popen")
    def test_recording_exception_handling(
        self, mock_popen, mock_absdiff, mock_cvtcolor
    ):
        """Test exception handling during recording"""
        recorder = ReplayRecorder(self.replay_config, self.cam_config)

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        gray_frame = np.zeros((720, 1280), dtype=np.uint8)

        mock_cvtcolor.return_value = gray_frame
        mock_popen.side_effect = Exception("FFmpeg failed")

        # Mock high difference
        diff_frame = np.ones((720, 1280), dtype=np.uint8) * 50
        mock_absdiff.return_value = diff_frame

        # Should not crash even if ffmpeg fails
        recorder.process_frame(test_frame)
        recorder.process_frame(test_frame)  # This should trigger recording attempt

        # Exception should be caught gracefully

    def test_output_directory_creation(self):
        """Test that output directory is created"""
        new_temp_dir = os.path.join(self.temp_dir, "new_replay_dir")
        config = self.replay_config.copy()
        config["output_dir"] = new_temp_dir

        # Directory should be created during initialization
        ReplayRecorder(config, self.cam_config)

        assert os.path.exists(new_temp_dir)

    @patch("cv2.cvtColor")
    @patch("cv2.absdiff")
    def test_difference_threshold_calculation(self, mock_absdiff, mock_cvtcolor):
        """Test motion detection threshold calculation"""
        recorder = ReplayRecorder(self.replay_config, self.cam_config)

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        gray_frame = np.zeros((720, 1280), dtype=np.uint8)

        mock_cvtcolor.return_value = gray_frame

        # Test different difference levels
        diff_frame_low = np.ones((720, 1280), dtype=np.uint8) * 10  # Below threshold
        diff_frame_high = np.ones((720, 1280), dtype=np.uint8) * 30  # Above threshold

        # First frame
        recorder.process_frame(test_frame)

        # Low difference - should not trigger
        mock_absdiff.return_value = diff_frame_low
        with patch("subprocess.Popen") as mock_popen:
            recorder.process_frame(test_frame)
            mock_popen.assert_not_called()

        # High difference - should trigger
        mock_absdiff.return_value = diff_frame_high
        with patch("subprocess.Popen") as mock_popen:
            recorder.process_frame(test_frame)
            mock_popen.assert_called_once()

    def teardown_method(self):
        """Clean up test files"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
