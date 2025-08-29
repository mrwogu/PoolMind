"""
Tests for Web Server module
"""
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from poolmind.web import server


class TestWebServer:
    """Test cases for Web Server functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        # Create test client
        self.client = TestClient(server.app)

        # Mock hub
        self.mock_hub = Mock()
        server.hub = self.mock_hub

    def test_index_route_with_templates(self):
        """Test index route returns HTML"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_state_endpoint_with_hub(self):
        """Test state endpoint with valid hub data"""
        mock_state = {"active_balls": 10, "game_state": "playing", "total_tracked": 15}
        self.mock_hub.snapshot.return_value = (None, mock_state, [])

        response = self.client.get("/state")
        assert response.status_code == 200

        data = response.json()
        assert data == mock_state

    def test_state_endpoint_no_hub(self):
        """Test state endpoint when hub is None"""
        server.hub = None

        response = self.client.get("/state")
        assert response.status_code == 200

        data = response.json()
        # Should return default state
        assert "total_balls" in data
        assert "game_state" in data
        assert data["game_state"] == "waiting"

    def test_state_endpoint_hub_exception(self):
        """Test state endpoint when hub throws exception"""
        self.mock_hub.snapshot.side_effect = Exception("Hub error")

        response = self.client.get("/state")
        assert response.status_code == 200

        data = response.json()
        # Should return default state on exception
        assert data["game_state"] == "waiting"

    def test_events_endpoint_with_data(self):
        """Test events endpoint with event data"""
        mock_events = [
            {"type": "ball_potted", "ball_id": 5, "ts": 1234567890},
            {"type": "game_start", "ts": 1234567891},
        ]
        self.mock_hub.snapshot.return_value = (None, {}, mock_events)

        response = self.client.get("/events")
        assert response.status_code == 200

        data = response.json()
        assert data == mock_events

    def test_events_endpoint_no_hub(self):
        """Test events endpoint when hub is None"""
        server.hub = None

        response = self.client.get("/events")
        assert response.status_code == 200

        data = response.json()
        assert data == []

    def test_events_endpoint_hub_exception(self):
        """Test events endpoint when hub throws exception"""
        self.mock_hub.snapshot.side_effect = Exception("Hub error")

        response = self.client.get("/events")
        assert response.status_code == 200

        data = response.json()
        assert data == []

    @patch("cv2.imencode")
    @patch("numpy.zeros")
    def test_frame_endpoint_with_hub(self, mock_zeros, mock_imencode):
        """Test frame endpoint with valid hub"""
        mock_frame_data = b"fake_jpeg_data"
        self.mock_hub.get_jpeg.return_value = mock_frame_data

        response = self.client.get("/frame.jpg")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert response.content == mock_frame_data

    @patch("cv2.imencode")
    @patch("cv2.putText")
    @patch("numpy.zeros")
    def test_frame_endpoint_no_hub(self, mock_zeros, mock_puttext, mock_imencode):
        """Test frame endpoint when hub is None"""
        server.hub = None

        # Mock image creation
        mock_zeros.return_value = "mock_image"
        mock_imencode.return_value = (True, b"placeholder_image")

        response = self.client.get("/frame.jpg")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert response.content == b"placeholder_image"

    @patch("cv2.imencode")
    @patch("cv2.putText")
    @patch("numpy.zeros")
    def test_frame_endpoint_hub_returns_none(
        self, mock_zeros, mock_puttext, mock_imencode
    ):
        """Test frame endpoint when hub returns None"""
        self.mock_hub.get_jpeg.return_value = None

        # Mock placeholder image creation
        mock_zeros.return_value = "mock_image"
        mock_imencode.return_value = (True, b"placeholder_image")

        response = self.client.get("/frame.jpg")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

    def test_config_endpoint(self):
        """Test config endpoint returns expected configuration"""
        response = self.client.get("/config")
        assert response.status_code == 200

        data = response.json()
        assert "camera" in data
        assert "detection" in data
        assert "calibration" in data
        assert "web" in data

        # Check specific values
        assert data["camera"]["width"] == 1280
        assert data["camera"]["height"] == 720
        assert data["detection"]["method"] == "HoughCircles"

    @patch("os.path.exists")
    def test_markers_download_file_exists(self, mock_exists):
        """Test markers download when file exists"""
        mock_exists.return_value = True

        # Mock file reading
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                b"pdf_content"
            )

            response = self.client.get("/markers/download")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert "attachment" in response.headers["content-disposition"]

    @patch("os.path.exists")
    def test_markers_download_file_not_exists(self, mock_exists):
        """Test markers download when file doesn't exist"""
        mock_exists.return_value = False

        response = self.client.get("/markers/download")
        assert response.status_code == 404

    def test_game_reset_endpoint(self):
        """Test game reset endpoint"""
        response = self.client.post("/game/reset")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "reset" in data["status"].lower()

    def test_set_hub_function(self):
        """Test set_hub function"""
        new_hub = Mock()
        server.set_hub(new_hub)

        assert server.hub == new_hub

    @patch("poolmind.web.server.StreamingResponse")
    @patch("asyncio.sleep")
    def test_stream_endpoint_with_hub(self, mock_sleep, mock_streaming_response):
        """Test MJPEG stream endpoint with hub"""
        # Mock hub returning JPEG data
        mock_jpeg_data = b"fake_jpeg_data"
        self.mock_hub.get_jpeg.return_value = mock_jpeg_data

        # Mock StreamingResponse to return a normal response
        from fastapi.responses import Response

        mock_streaming_response.return_value = Response(
            content=b"fake_stream_data",
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

        response = self.client.get("/stream.mjpg")

        # For streaming response, just check it starts successfully
        assert response.status_code == 200
        assert "multipart/x-mixed-replace" in response.headers["content-type"]

    @patch("poolmind.web.server.StreamingResponse")
    @patch("asyncio.sleep")
    @patch("cv2.imencode")
    @patch("cv2.putText")
    @patch("numpy.zeros")
    def test_stream_endpoint_no_hub(
        self,
        mock_zeros,
        mock_puttext,
        mock_imencode,
        mock_sleep,
        mock_streaming_response,
    ):
        """Test MJPEG stream endpoint without hub"""
        server.hub = None

        # Mock placeholder image creation
        mock_zeros.return_value = "mock_image"
        mock_imencode.return_value = (True, b"placeholder_jpeg")

        # Mock StreamingResponse to return a normal response
        from fastapi.responses import Response

        mock_streaming_response.return_value = Response(
            content=b"fake_stream_data",
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

        response = self.client.get("/stream.mjpg")

        # Stream should start successfully even without hub
        assert response.status_code == 200
        assert "multipart/x-mixed-replace" in response.headers["content-type"]

    def teardown_method(self):
        """Clean up after tests"""
        # Restore hub to avoid affecting other tests
        server.hub = None
