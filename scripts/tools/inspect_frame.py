#!/usr/bin/env python3
"""
Inspect generated virtual table frame for marker visibility
"""
import os
import sys

import cv2
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from virtual_table import VirtualPoolTable


def inspect_virtual_frame():
    """Inspect the virtual frame and marker regions"""

    # Create virtual table
    virtual_table = VirtualPoolTable("config/config.yaml")

    # Generate frame
    frame = virtual_table.generate_frame()

    print("=== Frame Inspection ===")
    print(f"Frame shape: {frame.shape}")
    print(f"Frame dtype: {frame.dtype}")
    print(f"Frame min/max: {frame.min()}/{frame.max()}")

    # Check marker positions
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

    # Extract and save marker regions
    for i, (x, y) in enumerate(positions):
        # Adjust positions to frame bounds
        x = max(0, min(x, frame.shape[1] - virtual_table.marker_size))
        y = max(0, min(y, frame.shape[0] - virtual_table.marker_size))

        # Extract marker region
        marker_region = frame[y : y + 120, x : x + 120]

        print(f"\nMarker {i} at ({x},{y}):")
        print(f"  Region shape: {marker_region.shape}")
        print(f"  Region min/max: {marker_region.min()}/{marker_region.max()}")
        print(f"  Mean values: {marker_region.mean(axis=(0,1))}")

        # Save region
        cv2.imwrite(f"marker_region_{i}.jpg", marker_region)

        # Convert to grayscale and check
        gray_region = cv2.cvtColor(marker_region, cv2.COLOR_BGR2GRAY)
        print(f"  Gray min/max: {gray_region.min()}/{gray_region.max()}")

        # Check for binary pattern (ArUco should have black/white)
        unique_values = np.unique(gray_region)
        print(
            f"  Unique gray values: {len(unique_values)} (should be ~2 for good ArUco)"
        )

        cv2.imwrite(f"marker_region_{i}_gray.jpg", gray_region)

    # Test ArUco detection on individual regions
    print("\n=== Testing ArUco Detection on Regions ===")
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)

    for i, (x, y) in enumerate(positions):
        x = max(0, min(x, frame.shape[1] - virtual_table.marker_size))
        y = max(0, min(y, frame.shape[0] - virtual_table.marker_size))

        marker_region = frame[y : y + 120, x : x + 120]
        gray_region = cv2.cvtColor(marker_region, cv2.COLOR_BGR2GRAY)

        _, ids, _ = detector.detectMarkers(gray_region)

        if ids is not None:
            print(f"  Marker {i}: ✅ Detected {ids.flatten().tolist()}")
        else:
            print(f"  Marker {i}: ❌ Not detected")

    print("\n💾 Saved individual marker regions as marker_region_*.jpg")


if __name__ == "__main__":
    inspect_virtual_frame()
