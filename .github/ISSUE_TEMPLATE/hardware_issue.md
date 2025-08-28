---
name: Hardware Issue
about: Report issues with hardware setup or compatibility
title: '[HARDWARE] '
labels: hardware
assignees: ''
---

## Hardware Information
- **Device**: [e.g. Raspberry Pi 4B]
- **RAM**: [e.g. 4GB]
- **OS**: [e.g. Raspberry Pi OS 64-bit]
- **Camera**: [e.g. Logitech C920, /dev/video0]
- **Display**: [e.g. HDMI monitor, 1920x1080]

## Issue Description
A clear and concise description of the hardware issue.

## Camera Detection
```bash
# Output of: v4l2-ctl --list-devices
[paste output here]
```

## System Information
```bash
# Output of: uname -a && lscpu && free -h
[paste output here]
```

## Error Messages
If applicable, paste any error messages:
```
[paste error messages here]
```

## Troubleshooting Steps Tried
- [ ] Checked camera connections
- [ ] Verified camera permissions (`ls -l /dev/video*`)
- [ ] Tested camera with other software (e.g., `ffplay /dev/video0`)
- [ ] Checked system logs (`dmesg | grep -i camera`)
- [ ] Tried different USB ports
- [ ] Updated system packages

## Additional Context
Add any other context about the problem here.
