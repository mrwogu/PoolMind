"""
Tests for Camera capture module
"""
import threading
import time
from unittest.mock import Mock, patch

import cv2
import numpy as np

from poolmind.capture.camera import Camera


class TestCamera:
    """Test cases for Camera class"""

    @patch("cv2.VideoCapture")
    def test_camera_initialization(self, mock_videocapture):
        """Test camera initializes with correct parameters"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        camera = Camera(index=1, width=1920, height=1080, fps=60)

        mock_videocapture.assert_called_once_with(1)
        mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        mock_cap.set.assert_any_call(cv2.CAP_PROP_FPS, 60)

        assert not camera.stopped
        assert camera.frame is None
        assert camera.thread.daemon

        # Cleanup
        camera.release()

    @patch("cv2.VideoCapture")
    def test_camera_default_parameters(self, mock_videocapture):
        """Test camera with default parameters"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        camera = Camera()

        mock_videocapture.assert_called_once_with(0)
        mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        mock_cap.set.assert_any_call(cv2.CAP_PROP_FPS, 30)

        camera.release()

    @patch("cv2.VideoCapture")
    def test_camera_frame_capture_success(self, mock_videocapture):
        """Test successful frame capture"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, test_frame)

        camera = Camera()

        # Wait a bit for thread to capture frame
        time.sleep(0.1)

        assert camera.frame is not None
        assert np.array_equal(camera.frame, test_frame)

        camera.release()

    @patch("cv2.VideoCapture")
    def test_camera_frame_capture_failure(self, mock_videocapture):
        """Test frame capture failure handling"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        # Simulate capture failure
        mock_cap.read.return_value = (False, None)

        camera = Camera()

        # Wait a bit and verify frame remains None
        time.sleep(0.1)

        assert camera.frame is None

        camera.release()

    @patch("cv2.VideoCapture")
    @patch("time.sleep")
    def test_camera_loop_with_failures(self, mock_sleep, mock_videocapture):
        """Test camera loop handles read failures gracefully"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        # First call fails, second succeeds
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_cap.read.side_effect = [(False, None), (True, test_frame)]

        camera = Camera()

        # Wait for processing
        time.sleep(0.1)

        # Should have called sleep on failure
        mock_sleep.assert_any_call(0.005)

        camera.release()

    @patch("cv2.VideoCapture")
    def test_frames_generator(self, mock_videocapture):
        """Test frames generator yields frames correctly"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, test_frame)

        camera = Camera()

        # Wait for frame to be captured
        time.sleep(0.1)

        # Get frames from generator
        frame_generator = camera.frames()
        frames_collected = []

        for i, frame in enumerate(frame_generator):
            frames_collected.append(frame)
            if i >= 2:  # Collect a few frames
                break

        assert len(frames_collected) >= 3
        for frame in frames_collected:
            assert frame is not None
            assert frame.shape == (720, 1280, 3)
            # Should be copies, not the same object
            assert frame is not camera.frame

        camera.release()

    @patch("cv2.VideoCapture")
    @patch("time.sleep")
    def test_frames_generator_no_frame(self, mock_sleep, mock_videocapture):
        """Test frames generator when no frame is available"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap
        mock_cap.read.return_value = (False, None)

        camera = Camera()

        # Create generator and try to get frame
        frame_generator = camera.frames()

        # Start generator and try to get first frame
        # This should sleep since no frame is available
        next_frame_thread = threading.Thread(target=lambda: next(frame_generator, None))
        next_frame_thread.daemon = True
        next_frame_thread.start()

        time.sleep(0.1)  # Let it try to get frame

        # Should have called sleep
        mock_sleep.assert_any_call(0.005)

        camera.release()

    @patch("cv2.VideoCapture")
    def test_camera_release(self, mock_videocapture):
        """Test camera release functionality"""
        mock_cap = Mock()
        mock_cap.read.return_value = (False, None)  # Make it return proper tuple
        mock_videocapture.return_value = mock_cap

        camera = Camera()
        original_thread = camera.thread

        # Give thread time to start
        time.sleep(0.05)

        # Verify thread is running
        assert original_thread.is_alive()

        camera.release()

        # Verify stopped flag is set
        assert camera.stopped

        # After release, thread should be joined and not alive
        assert not original_thread.is_alive()

        # Verify VideoCapture.release() was called
        mock_cap.release.assert_called_once()

    @patch("cv2.VideoCapture")
    def test_camera_thread_safety(self, mock_videocapture):
        """Test thread safety of camera operations"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        test_frames = [np.full((720, 1280, 3), i, dtype=np.uint8) for i in range(10)]
        mock_cap.read.side_effect = [(True, frame) for frame in test_frames]

        camera = Camera()

        # Multiple threads reading frames
        collected_frames = []

        def frame_reader():
            for _ in range(5):
                with camera.lock:
                    if camera.frame is not None:
                        collected_frames.append(camera.frame.copy())
                time.sleep(0.01)

        threads = [threading.Thread(target=frame_reader) for _ in range(3)]
        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Verify no exceptions and frames were collected
        assert len(collected_frames) > 0

        camera.release()

    @patch("cv2.VideoCapture")
    def test_camera_continuous_operation(self, mock_videocapture):
        """Test camera continuous operation over time"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        frame_counter = 0

        def mock_read():
            nonlocal frame_counter
            frame_counter += 1
            frame = np.full((720, 1280, 3), frame_counter % 256, dtype=np.uint8)
            return (True, frame)

        mock_cap.read.side_effect = mock_read

        camera = Camera()

        # Collect frames over time
        start_time = time.time()
        frames_collected = []

        while time.time() - start_time < 0.5:  # Run for 0.5 seconds
            with camera.lock:
                if camera.frame is not None:
                    frames_collected.append(camera.frame[0, 0, 0])  # Get pixel value
            time.sleep(0.01)

        camera.release()

        # Should have collected multiple different frames
        assert len(frames_collected) > 10
        assert len(set(frames_collected)) > 1  # Different frame values

    @patch("cv2.VideoCapture")
    def test_frames_generator_stops_when_camera_released(self, mock_videocapture):
        """Test frames generator stops when camera is released"""
        mock_cap = Mock()
        mock_videocapture.return_value = mock_cap

        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, test_frame)

        camera = Camera()
        time.sleep(0.1)  # Let it capture a frame

        frame_generator = camera.frames()
        frames_collected = []

        # Collect a few frames
        for i, frame in enumerate(frame_generator):
            frames_collected.append(frame)
            if i >= 2:
                camera.release()  # Release camera mid-iteration
            if i >= 5:  # Safety limit
                break

        # Should have collected some frames before stopping
        assert len(frames_collected) >= 3
