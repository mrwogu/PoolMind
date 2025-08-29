#!/usr/bin/env python3
"""
Quick ArUco Detection Test
Tests if ArUco markers in virtual table are properly detected
"""
import sys
import time

import cv2

# Add paths
sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from virtual_table import VirtualPoolTable


def test_aruco_detection():
    """Test ArUco detection on virtual table"""
    print("🔍 Testing ArUco Detection...")

    # Create virtual table
    virtual_table = VirtualPoolTable()

    # Generate a few test frames
    for frame_num in range(5):
        print(f"\n📸 Frame {frame_num + 1}:")

        # Generate frame
        frame = virtual_table.generate_frame(frame_num)

        # Try to detect ArUco markers
        try:
            import cv2.aruco as aruco

            aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Try detection
            try:
                parameters = aruco.DetectorParameters()
                detector = aruco.ArucoDetector(aruco_dict, parameters)
                corners, ids, _ = detector.detectMarkers(gray)

                if ids is not None:
                    print(f"  ✅ Detected {len(ids)} markers: {ids.flatten()}")

                    # Show marker positions
                    for i, corner_set in enumerate(corners):
                        marker_id = ids[i][0]
                        center = corner_set[0].mean(axis=0)
                        print(
                            f"     Marker {marker_id}: center at ({center[0]:.1f}, {center[1]:.1f})"
                        )
                else:
                    print("  ❌ No markers detected")

            except Exception as e:
                print(f"  ❌ Detection failed: {e}")

        except ImportError:
            print("  ❌ ArUco module not available")

        time.sleep(0.1)

    print("\n🎯 ArUco detection test completed!")


def main():
    """Main function"""
    print("🎱 PoolMind ArUco Detection Test")
    print("=" * 40)

    try:
        test_aruco_detection()
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    main()
