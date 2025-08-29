#!/usr/bin/env python3
"""
Debug ArUco marker generation and detection
"""
import sys

import cv2
import numpy as np


def test_marker_generation():
    """Test marker generation directly"""
    print("🔍 Testing ArUco marker generation...")

    try:
        import cv2.aruco as aruco

        # Create dictionary
        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

        # Generate a test marker
        marker_size = 200
        marker_img = aruco.generateImageMarker(aruco_dict, 0, marker_size)

        print(f"✅ Generated marker shape: {marker_img.shape}")
        print(f"✅ Marker dtype: {marker_img.dtype}")
        print(f"✅ Marker min/max: {marker_img.min()}/{marker_img.max()}")

        # Convert to 3-channel
        marker_bgr = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)

        # Create test frame with marker
        frame = np.zeros((400, 400, 3), dtype=np.uint8)
        frame[100 : 100 + marker_size, 100 : 100 + marker_size] = marker_bgr

        # Try to detect it
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        try:
            # Try the same parameters as PoolMind uses
            try:
                parameters = aruco.DetectorParameters_create()  # Old API
            except AttributeError:
                parameters = aruco.DetectorParameters()  # New API

            # Try both detection methods
            try:
                detector = aruco.ArucoDetector(aruco_dict, parameters)
                corners, ids, _ = detector.detectMarkers(gray)
            except AttributeError:
                # Old API fallback
                corners, ids, _ = aruco.detectMarkers(
                    gray, aruco_dict, parameters=parameters
                )

            if ids is not None:
                print(f"✅ Detection successful! Found markers: {ids.flatten()}")
            else:
                print("❌ Detection failed - no markers found")

                # Try with different parameters
                if hasattr(parameters, "adaptiveThreshWinSizeMin"):
                    parameters.adaptiveThreshWinSizeMin = 3
                    parameters.adaptiveThreshWinSizeMax = 23
                    parameters.adaptiveThreshWinSizeStep = 10

                    try:
                        detector = aruco.ArucoDetector(aruco_dict, parameters)
                        corners, ids, _ = detector.detectMarkers(gray)
                    except AttributeError:
                        corners, ids, _ = aruco.detectMarkers(
                            gray, aruco_dict, parameters=parameters
                        )

                    if ids is not None:
                        print(f"✅ Detection with adjusted params: {ids.flatten()}")
                    else:
                        print("❌ Still no detection with adjusted params")

                # Save images for debugging
                cv2.imwrite("debug_frame.jpg", frame)
                cv2.imwrite("debug_gray.jpg", gray)
                cv2.imwrite("debug_marker.jpg", marker_img)
                print(
                    "🔍 Saved debug images: debug_frame.jpg, debug_gray.jpg, debug_marker.jpg"
                )

        except Exception as e:
            print(f"❌ Detection error: {e}")

    except ImportError as e:
        print(f"❌ ArUco not available: {e}")


def main():
    test_marker_generation()


if __name__ == "__main__":
    main()
