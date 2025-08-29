#!/usr/bin/env python3
"""
Test pure ArUco marker generation and detection
"""
import cv2
import numpy as np


def test_pure_aruco():
    """Test ArUco marker generation and detection in isolation"""

    # Generate ArUco marker
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_size = 120

    # Create marker
    marker_gray = cv2.aruco.generateImageMarker(aruco_dict, 0, marker_size)
    marker_bgr = cv2.cvtColor(marker_gray, cv2.COLOR_GRAY2BGR)

    print(f"Generated marker shape: {marker_bgr.shape}")
    print(f"Marker gray unique values: {np.unique(marker_gray)}")
    print("Marker BGR unique values per channel:")
    for i, color in enumerate(["B", "G", "R"]):
        unique = np.unique(marker_bgr[:, :, i])
        print(f"  {color}: {unique}")

    # Test detection on pure marker
    detector_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)

    _, ids, _ = detector.detectMarkers(marker_gray)

    if ids is not None:
        print(f"✅ Pure marker detected: {ids.flatten()}")
    else:
        print("❌ Pure marker NOT detected")

    # Test on BGR version
    _, ids_bgr, _ = detector.detectMarkers(cv2.cvtColor(marker_bgr, cv2.COLOR_BGR2GRAY))

    if ids_bgr is not None:
        print(f"✅ BGR marker detected: {ids_bgr.flatten()}")
    else:
        print("❌ BGR marker NOT detected")

    # Save for inspection
    cv2.imwrite("pure_marker_gray.jpg", marker_gray)
    cv2.imwrite("pure_marker_bgr.jpg", marker_bgr)
    print("💾 Saved pure_marker_*.jpg")

    # Test with different backgrounds
    test_backgrounds = [
        (50, "Dark gray"),
        (200, "Light gray"),
        (255, "White"),
        (0, "Black"),
    ]

    for bg_value, bg_name in test_backgrounds:
        # Create frame with marker on different background
        test_frame = np.ones((300, 300, 3), dtype=np.uint8) * bg_value
        test_frame[90:210, 90:210] = marker_bgr

        test_gray = cv2.cvtColor(test_frame, cv2.COLOR_BGR2GRAY)
        _, test_ids, _ = detector.detectMarkers(test_gray)

        if test_ids is not None:
            print(f"✅ {bg_name} background: detected {test_ids.flatten()}")
        else:
            print(f"❌ {bg_name} background: NOT detected")

        cv2.imwrite(f"test_bg_{bg_value}.jpg", test_frame)


if __name__ == "__main__":
    test_pure_aruco()
