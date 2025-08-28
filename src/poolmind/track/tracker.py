import math
from collections import OrderedDict

import numpy as np


class CentroidTracker:
    def __init__(self, cfg):
        self.nextObjectID = 1
        self.objects = OrderedDict()  # id -> (x,y,r)
        self.disappeared = OrderedDict()  # id -> count
        self.maxDisappeared = cfg.get("max_disappeared", 8)
        self.maxDistance = cfg.get("max_distance", 40)

    def update(self, detections):
        # detections: list of (x,y,r) or (x,y,r,color_type)
        if len(detections) == 0:
            # mark disappeared
            to_delete = []
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    to_delete.append(objectID)
            for oid in to_delete:
                self.objects.pop(oid, None)
                self.disappeared.pop(oid, None)
            return self.objects

        # Normalize detections to handle both (x,y,r) and (x,y,r,color) formats
        normalized_detections = []
        for det in detections:
            if len(det) >= 4:  # has color info
                x, y, r, color = det[0], det[1], det[2], det[3]
            else:  # old format
                x, y, r, color = det[0], det[1], det[2], "unknown"
            normalized_detections.append((x, y, r, color))

        if len(self.objects) == 0:
            for x, y, r, color in normalized_detections:
                self.objects[self.nextObjectID] = (x, y, r, color)
                self.disappeared[self.nextObjectID] = 0
                self.nextObjectID += 1
            return self.objects

        objectIDs = list(self.objects.keys())
        objectCentroids = np.array([(v[0], v[1]) for v in self.objects.values()])
        inputCentroids = np.array([(x, y) for (x, y, _, _) in normalized_detections])

        D = self._dist_matrix(objectCentroids, inputCentroids)

        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]

        usedRows = set()
        usedCols = set()

        for row, col in zip(rows, cols):
            if row in usedRows or col in usedCols:
                continue
            if D[row, col] > self.maxDistance:
                continue
            objectID = objectIDs[row]
            x, y, r, color = normalized_detections[col]
            self.objects[objectID] = (int(x), int(y), int(r), color)
            self.disappeared[objectID] = 0
            usedRows.add(row)
            usedCols.add(col)

        unusedRows = set(range(0, D.shape[0])).difference(usedRows)
        unusedCols = set(range(0, D.shape[1])).difference(usedCols)

        for row in unusedRows:
            objectID = objectIDs[row]
            self.disappeared[objectID] += 1
            if self.disappeared[objectID] > self.maxDisappeared:
                self.objects.pop(objectID, None)
                self.disappeared.pop(objectID, None)

        for col in unusedCols:
            x, y, r, color = normalized_detections[col]
            self.objects[self.nextObjectID] = (int(x), int(y), int(r), color)
            self.disappeared[self.nextObjectID] = 0
            self.nextObjectID += 1

        return self.objects

    def _dist_matrix(self, A, B):
        return np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(axis=2))
