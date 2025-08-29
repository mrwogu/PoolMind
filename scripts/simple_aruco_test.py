#!/usr/bin/env python3
"""
Simple ArUco test - generate and detect
"""
import cv2
import numpy as np


def simple_test():
    print("Testing basic ArUco generation and detection...")

    try:
        import cv2.aruco as aruco

        # Create dictionary and parameters
        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        parameters = aruco.DetectorParameters()
        detector = aruco.ArucoDetector(aruco_dict, parameters)

        # Generate marker
        marker_img = aruco.generateImageMarker(aruco_dict, 0, 200)
        print(f"Generated marker: {marker_img.shape}, dtype: {marker_img.dtype}")

        # Create frame with marker
        frame = np.ones((500, 500), dtype=np.uint8) * 255  # White background
        frame[150:350, 150:350] = marker_img

        # Convert to BGR for consistency
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # Detect markers
        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            print(f"✅ SUCCESS! Detected {len(ids)} markers: {ids.flatten()}")
        else:
            print("❌ FAILED: No markers detected")

            # Save for inspection
            cv2.imwrite("test_frame.jpg", frame_bgr)
            cv2.imwrite("test_gray.jpg", frame)
            print("Saved test images for inspection")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    simple_test()
