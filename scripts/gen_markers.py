#!/usr/bin/env python3
import argparse, os, sys
import cv2
import numpy as np
from PIL import Image
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB = True
except Exception:
    REPORTLAB = False

def make_marker(dictionary, id, size_px=800, border_bits=1):
    img = cv2.aruco.generateImageMarker(dictionary, id, size_px)
    if border_bits > 0:
        border = np.ones((size_px + 2*border_bits*10, size_px + 2*border_bits*10), dtype=np.uint8) * 255
        border[border_bits*10:-border_bits*10, border_bits*10:-border_bits*10] = img
        img = border
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="markers", help="output directory")
    ap.add_argument("--dict", default="DICT_4X4_50")
    ap.add_argument("--ids", nargs="+", type=int, default=[0,1,2,3])
    ap.add_argument("--px", type=int, default=800)
    ap.add_argument("--pdf", action="store_true", help="also create a printable A4 PDF")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    dct = getattr(cv2.aruco, args.dict)
    dictionary = cv2.aruco.getPredefinedDictionary(dct)
    pngs = []

    for i in args.ids:
        img = make_marker(dictionary, i, size_px=args.px)
        path = os.path.join(args.out, f"aruco_{i}.png")
        cv2.imwrite(path, img)
        pngs.append(path)
        print("wrote", path)

    if args.pdf:
        if not REPORTLAB:
            print("reportlab not installed; skipping PDF", file=sys.stderr)
            return
        c = canvas.Canvas(os.path.join(args.out, "markers_A4.pdf"), pagesize=A4)
        W, H = A4
        margin = 36
        size = min(W, H) - 2*margin
        # place 4 per page
        per_page = 4
        cols, rows = 2, 2
        cell_w = (W - 3*margin)/cols
        cell_h = (H - 3*margin)/rows
        x0, y0 = margin, H - margin - cell_h
        n=0
        for p in pngs:
            if n>0 and n%per_page==0:
                c.showPage()
                x0, y0 = margin, H - margin - cell_h
            x = x0 + (n%2) * (cell_w + margin)
            y = y0 - (n%4>=2) * (cell_h + margin)
            c.drawImage(p, x, y, width=cell_w, height=cell_h, preserveAspectRatio=True, anchor='sw')
            c.setFont("Helvetica", 10); c.drawString(x, y-12, os.path.basename(p))
            n+=1
        c.save()
        print("wrote", os.path.join(args.out, "markers_A4.pdf"))

if __name__ == "__main__":
    main()
