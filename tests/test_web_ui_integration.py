"""
Integration tests for PoolMind Web UI functionality and real-time data updates
"""
import threading
import time
from unittest.mock import patch

from fastapi.testclient import TestClient

from poolmind.web.hub import FrameHub
from poolmind.web.server import app, set_hub


class TestWebUIIntegration:
    """Integration tests for web UI functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.hub = FrameHub()
        set_hub(self.hub)

    def test_index_page_loads_with_ui_elements(self):
        """Test that index page loads with all UI elements"""
        response = self.client.get("/")
        assert response.status_code == 200

        content = response.text
        # Check for key UI elements
        assert "PoolMind" in content
        assert "Live Feed" in content
        assert "Game Status" in content
        assert "Quick Actions" in content
        assert "Recent Events" in content
        assert "Session Analytics" in content

        # Check for button elements
        assert "Fullscreen" in content
        assert "Snapshot" in content
        assert "Download ArUco Markers" in content
        assert "Reset Game" in content

    @patch("poolmind.web.server.StreamingResponse")
    def test_live_stream_endpoint_functionality(self, mock_streaming_response):
        """Test MJPEG stream endpoint"""
        import numpy as np
        from fastapi.responses import Response

        # Set up test frame in hub
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.hub.update_frame(test_frame)

        # Mock StreamingResponse to return a regular response instead of infinite stream
        mock_streaming_response.return_value = Response(
            content=b"--frame\r\nContent-Type: image/jpeg\r\n\r\nfake_jpeg_data\r\n",
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

        response = self.client.get("/stream.mjpg")
        assert response.status_code == 200
        assert (
            response.headers["content-type"]
            == "multipart/x-mixed-replace; boundary=frame"
        )

    def test_state_endpoint_real_time_updates(self):
        """Test that state endpoint provides real-time game state"""
        # Mock game state
        test_state = {
            "total_tracked": 12,
            "active_balls": 10,
            "potted": 2,
            "active_cue": 1,
            "active_solid": 5,
            "active_stripe": 4,
            "solid_potted": 1,
            "stripe_potted": 1,
            "game_state": "open_table",
        }

        # Update hub with test state
        import numpy as np

        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.hub.update_frame(test_frame, test_state)

        response = self.client.get("/state")
        assert response.status_code == 200

        data = response.json()
        assert data["total_tracked"] == 12
        assert data["active_balls"] == 10
        assert data["game_state"] == "open_table"

    def test_events_endpoint_game_events(self):
        """Test that events endpoint provides game events"""
        # Add test events to hub
        test_events = [
            {"type": "pot", "ts": time.time(), "info": "Ball 5 potted"},
            {"type": "break", "ts": time.time(), "info": "Game started"},
            {"type": "foul", "ts": time.time(), "info": "Cue ball scratched"},
        ]

        for event in test_events:
            self.hub.push_event(event)

        response = self.client.get("/events")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 3
        assert data[0]["type"] == "pot"
        assert data[1]["type"] == "break"
        assert data[2]["type"] == "foul"

    def test_frame_snapshot_endpoint(self):
        """Test frame snapshot functionality"""
        import numpy as np

        # Create test frame with some content
        rng = np.random.default_rng(42)
        test_frame = rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)
        self.hub.update_frame(test_frame)

        response = self.client.get("/frame.jpg")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert len(response.content) > 0

    def test_game_reset_endpoint(self):
        """Test game reset functionality"""
        response = self.client.post("/game/reset")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "message" in data

    def test_config_endpoint_provides_settings(self):
        """Test that config endpoint provides application settings"""
        response = self.client.get("/config")
        assert response.status_code == 200

        data = response.json()
        # Should contain basic config structure
        assert "camera" in data
        assert "detection" in data
        assert "web" in data

    def test_aruco_markers_download(self):
        """Test ArUco markers download functionality"""
        # Mock file existence
        with patch("os.path.exists", return_value=True):
            response = self.client.get("/markers/download")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"

    def test_aruco_markers_download_not_found(self):
        """Test ArUco markers download when file doesn't exist"""
        with patch("os.path.exists", return_value=False):
            response = self.client.get("/markers/download")
            assert response.status_code == 404


class TestRealTimeDataUpdates:
    """Test real-time data update functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.hub = FrameHub()
        set_hub(self.hub)

    def test_data_refresh_interval_compliance(self):
        """Test that data updates at expected intervals"""
        import numpy as np

        # Simulate multiple rapid updates
        updates = []
        for i in range(5):
            test_state = {"frame_count": i, "timestamp": time.time()}
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            self.hub.update_frame(test_frame, test_state)

            response = self.client.get("/state")
            assert response.status_code == 200
            updates.append(response.json())
            time.sleep(0.1)

        # Verify updates are distinct
        frame_counts = [u["frame_count"] for u in updates]
        assert len(set(frame_counts)) == 5  # All unique

    def test_event_queue_fifo_behavior(self):
        """Test that events maintain FIFO ordering"""
        # Add events in sequence
        for i in range(10):
            event = {
                "type": "test_event",
                "id": i,
                "ts": time.time() + i,
                "info": f"Event {i}",
            }
            self.hub.push_event(event)

        response = self.client.get("/events")
        assert response.status_code == 200

        events = response.json()
        assert len(events) <= 10  # Hub has max queue size

        # Check ordering (most recent first in response)
        if len(events) > 1:
            for i in range(len(events) - 1):
                assert events[i]["ts"] >= events[i + 1]["ts"]

    def test_connection_status_tracking(self):
        """Test connection status is properly tracked"""
        import numpy as np

        # Initial state - no data
        response = self.client.get("/state")
        # Verify initial response is valid
        assert response.status_code == 200

        # Add frame and state
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        current_time = time.time()
        test_state = {"connected": True, "last_update": current_time, "active_balls": 8}

        self.hub.update_frame(test_frame, test_state)

        # Verify updated state
        response = self.client.get("/state")
        updated_data = response.json()
        assert updated_data["active_balls"] == 8

    def test_concurrent_api_access(self):
        """Test API handles concurrent access properly"""
        import numpy as np

        # Set up test data
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_state = {"concurrent_test": True}
        self.hub.update_frame(test_frame, test_state)

        # Simulate concurrent requests
        def make_request(endpoint):
            response = self.client.get(endpoint)
            return response.status_code

        threads = []
        results = []

        # Create multiple threads hitting different endpoints
        endpoints = ["/state", "/events", "/config", "/frame.jpg"]
        for _ in range(10):
            for endpoint in endpoints:
                thread = threading.Thread(
                    target=lambda ep=endpoint: results.append(make_request(ep))
                )
                threads.append(thread)
                thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert all(status == 200 for status in results)

    def test_memory_efficiency_large_dataset(self):
        """Test system handles large amounts of data efficiently"""
        # Generate large number of events
        for i in range(100):
            event = {
                "type": "stress_test",
                "id": i,
                "ts": time.time(),
                "data": f"Large event data string {i}" * 10,
            }
            self.hub.push_event(event)

        # Events should be limited by maxlen
        self.client.get("/events")

        # Should still be responsive
        response_time_start = time.time()
        self.client.get("/state")
        response_time = time.time() - response_time_start
        assert response_time < 1.0  # Should respond quickly

    def test_websocket_simulation_rapid_updates(self):
        """Simulate WebSocket-like rapid updates"""
        import numpy as np

        # Rapid state changes simulating live game
        game_states = ["break", "open_table", "solid_player", "stripe_player"]

        for i, state in enumerate(game_states * 5):  # 20 rapid changes
            rng = np.random.default_rng(42 + i)
            test_frame = rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)
            test_state = {
                "game_state": state,
                "frame_id": i,
                "balls_remaining": 16 - (i % 16),
            }

            self.hub.update_frame(test_frame, test_state)

            # Simulate brief processing time
            time.sleep(0.01)

        # Final state should be latest
        response = self.client.get("/state")
        final_state = response.json()
        assert final_state["frame_id"] == 19  # Last update


class TestWebUIButtonFunctionality:
    """Test all web UI buttons are functional"""

    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.hub = FrameHub()
        set_hub(self.hub)

    @patch("poolmind.web.server.StreamingResponse")
    def test_fullscreen_button_endpoint(self, mock_streaming_response):
        """Test fullscreen functionality (client-side, so test supporting endpoints)"""
        # Fullscreen is client-side JS, but test stream endpoint it uses
        import numpy as np
        from fastapi.responses import Response

        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.hub.update_frame(test_frame)

        # Mock StreamingResponse to prevent hanging
        mock_streaming_response.return_value = Response(
            content=b"--frame\r\nContent-Type: image/jpeg\r\n\r\nfake_jpeg_data\r\n",
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

        response = self.client.get("/stream.mjpg")
        assert response.status_code == 200

    def test_snapshot_button_functionality(self):
        """Test snapshot button endpoint"""
        import numpy as np

        rng = np.random.default_rng(42)
        test_frame = rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)
        self.hub.update_frame(test_frame)

        response = self.client.get("/frame.jpg")
        assert response.status_code == 200
        assert "image/jpeg" in response.headers["content-type"]

    def test_reset_game_button_functionality(self):
        """Test reset game button endpoint"""
        response = self.client.post("/game/reset")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"

    def test_download_markers_button_functionality(self):
        """Test download ArUco markers button"""
        with patch("os.path.exists", return_value=True):
            response = self.client.get("/markers/download")
            assert response.status_code == 200

    def test_theme_toggle_persistence(self):
        """Test theme toggle (client-side localStorage, verify page supports it)"""
        # Theme toggle is client-side, but verify page loads with theme support
        response = self.client.get("/")
        assert response.status_code == 200

        content = response.text
        assert "theme-toggle" in content
        assert "dark" in content  # Dark mode support

    def test_analytics_view_functionality(self):
        """Test analytics view (via state endpoint)"""
        import numpy as np

        # Create comprehensive state for analytics
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        analytics_state = {
            "total_tracked": 15,
            "active_balls": 12,
            "potted": 3,
            "tracking_accuracy": 87.5,
            "session_duration": 1800,  # 30 minutes
            "frame_rate": 30,
        }

        self.hub.update_frame(test_frame, analytics_state)

        response = self.client.get("/state")
        assert response.status_code == 200

        data = response.json()
        assert data["total_tracked"] == 15
        assert data["active_balls"] == 12

    def test_settings_view_functionality(self):
        """Test settings view (via config endpoint)"""
        response = self.client.get("/config")
        assert response.status_code == 200

        config = response.json()
        assert isinstance(config, dict)
        assert len(config) > 0

    def test_share_view_functionality(self):
        """Test share view functionality (frame endpoint for sharing)"""
        import numpy as np

        rng = np.random.default_rng(42)
        test_frame = rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)
        self.hub.update_frame(test_frame)

        # Frame endpoint should be shareable
        response = self.client.get("/frame.jpg")
        assert response.status_code == 200
        assert len(response.content) > 0
