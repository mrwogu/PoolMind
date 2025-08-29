# ArUco Markers

To prepare table corner markers:

```bash
# in repo:
./scripts/tools/gen_markers.py --out markers --ids 0 1 2 3 --px 1200 --pdf
```

- PNG files will be saved in `markers/`.
- If you have `reportlab`, `markers/markers_A4.pdf` ready for printing will also be created.
- Dictionary: default `DICT_4X4_50`; you can change with `--dict`.

Attach markers in order: **0 (LT), 1 (RT), 2 (RB), 3 (LB)** and keep them in frame.
