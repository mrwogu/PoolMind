#!/usr/bin/env python3
"""
Debug ArUco marker detection in virtual table
"""
import os
import sys

import cv2
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from virtual_table import VirtualPoolTable


def main():
    """Debug ArUco marker detection in virtual table"""

    print("🔍 Debugging virtual table markers...")

    # Initialize ArUco detector
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)

    # Create virtual table
    config = {
        "frame_width": 1280,
        "frame_height": 720,
        "table_center": [640, 360],
        "table_size": [1080, 540],
        "marker_size": 120,
        "ball_radius": 15,
        "num_balls": 16,
    }

    virtual_table = VirtualPoolTable("config/config.yaml")

    print("=== Marker Detection Debug ===")
    print(f"Markers available: {list(virtual_table.markers.keys())}")

    # Check individual markers
    for marker_id in virtual_table.markers:
        marker = virtual_table.markers[marker_id]
        print(f"  Marker {marker_id}: shape {marker.shape}")

    print(f"Table: x={virtual_table.table_x}, y={virtual_table.table_y}")
    print(f"Table size: {virtual_table.table_width}x{virtual_table.table_height}")
    print(f"Frame size: {config['frame_width']}x{config['frame_height']}")
    print(f"Marker size: {virtual_table.marker_size}")

    # Generate virtual table frame
    frame = virtual_table.generate_frame()

    # Print expected marker positions
    marker_offset = 50
    positions = [
        (
            virtual_table.table_x - marker_offset,
            virtual_table.table_y - marker_offset,
        ),  # 0: top-left
        (
            virtual_table.table_x
            + virtual_table.table_width
            - virtual_table.marker_size
            + marker_offset,
            virtual_table.table_y - marker_offset,
        ),  # 1: top-right
        (
            virtual_table.table_x
            + virtual_table.table_width
            - virtual_table.marker_size
            + marker_offset,
            virtual_table.table_y
            + virtual_table.table_height
            - virtual_table.marker_size
            + marker_offset,
        ),  # 2: bottom-right
        (
            virtual_table.table_x - marker_offset,
            virtual_table.table_y
            + virtual_table.table_height
            - virtual_table.marker_size
            + marker_offset,
        ),  # 3: bottom-left
    ]

    print("\n=== Expected Marker Positions ===")
    for i, (x, y) in enumerate(positions):
        # Check bounds
        x_adj = max(0, min(x, frame.shape[1] - virtual_table.marker_size))
        y_adj = max(0, min(y, frame.shape[0] - virtual_table.marker_size))

        print(f"Marker {i}: calculated ({x},{y}) -> placed ({x_adj},{y_adj})")

        # Check if position changed (indicating clipping)
        if x != x_adj or y != y_adj:
            print(f"  ⚠️  Marker {i} position was clipped!")

    # Convert to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect markers in virtual table
    corners, ids, _ = detector.detectMarkers(gray)

    print("\n=== Detection Results ===")
    if ids is not None:
        print(f"✅ Found {len(ids)} markers: {ids.flatten().tolist()}")

        # Draw detected markers
        frame_with_markers = frame.copy()
        cv2.aruco.drawDetectedMarkers(frame_with_markers, corners, ids)

        # Save debug images
        cv2.imwrite("debug_virtual_detected.jpg", frame_with_markers)
        print("� Saved debug_virtual_detected.jpg")

    else:
        print("❌ No markers found in virtual table frame")

        # Test with simplified manual placement
        print("\n=== Manual Test - Simple Background ===")
        test_frame = np.ones((720, 1280, 3), dtype=np.uint8) * 200  # Light gray

        # Place marker 0 in clear area
        if 0 in virtual_table.markers:
            marker_0 = virtual_table.markers[0]
            x, y = 200, 200  # Clear position
            test_frame[y : y + 120, x : x + 120] = marker_0

            test_gray = cv2.cvtColor(test_frame, cv2.COLOR_BGR2GRAY)
            _, test_ids, _ = detector.detectMarkers(test_gray)

            if test_ids is not None:
                print(f"✅ Manual test detected: {test_ids.flatten().tolist()}")
            else:
                print("❌ Manual test also failed")

            cv2.imwrite("debug_manual_simple.jpg", test_frame)
            cv2.imwrite("debug_manual_simple_gray.jpg", test_gray)
            print("💾 Saved manual test images")

    # Always save the full frame for inspection
    cv2.imwrite("debug_virtual_full.jpg", frame)
    cv2.imwrite("debug_virtual_gray.jpg", gray)
    print("💾 Saved full frame debug images")

    print("🎯 Debug completed!")


if __name__ == "__main__":
    main()
