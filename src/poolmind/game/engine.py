import math
from collections import defaultdict

from .rules import EightBallRules


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class GameEngine:
    def __init__(self, table, cfg=None):
        self.table = table
        cfg = cfg or {}
        self.max_disappeared_for_pot = cfg.get("disappear_for_pot", 6)
        self.pocket_radius = cfg.get("pocket_radius", 36)
        self.track_history = {}  # id -> list of (x,y)
        self.disappear_counts = {}  # id -> frames disappeared
        self.potted_ids = set()
        self.events = []  # recent events (type, info)
        self.score = defaultdict(int)
        self.ball_types = {}  # id -> color type
        self.last_shot_potted = set()  # balls potted in current shot
        self.shot_in_progress = False

        # 8-ball rules engine
        self.rules_engine = EightBallRules()
        self.enable_8ball_rules = cfg.get("enable_8ball_rules", True)

        self.pockets = table.default_pockets(self.pocket_radius)

    def update(self, tracks):
        # Update histories & detect disappearances
        current_ids = set(tracks.keys())

        # Detect if a shot is in progress (movement detected)
        # This is a simplified version - in real implementation you'd track ball velocities
        if current_ids and not self.shot_in_progress:
            self.shot_in_progress = True
            self.last_shot_potted = set()

        # Update positions and ball types
        for oid, track_data in tracks.items():
            # Handle both old (x,y,r) and new (x,y,r,color) formats
            if len(track_data) >= 4:
                x, y, _, color = track_data
                self.ball_types[oid] = color
            else:
                x, y, _ = track_data[0], track_data[1], track_data[2]

            self.track_history.setdefault(oid, [])
            self.track_history[oid].append((x, y))
            self.track_history[oid] = self.track_history[oid][-120:]
            self.disappear_counts[oid] = 0

        # mark disappeared
        new_pots_this_frame = set()
        for oid in list(self.disappear_counts.keys()):
            if oid not in current_ids and oid not in self.potted_ids:
                self.disappear_counts[oid] += 1
                # If recently near any pocket and now disappeared → pot
                if self.disappear_counts[oid] == self.max_disappeared_for_pot:
                    if self._was_near_pocket(oid):
                        self.potted_ids.add(oid)
                        self.last_shot_potted.add(oid)
                        new_pots_this_frame.add(oid)
                        ball_type = self.ball_types.get(oid, "unknown")
                        self.score["potted"] += 1
                        self.score[f"{ball_type}_potted"] = (
                            self.score.get(f"{ball_type}_potted", 0) + 1
                        )

                        self.events.append(
                            {
                                "type": "pot",
                                "info": f"{ball_type} ball ID {oid}",
                                "ball_id": oid,
                                "ball_type": ball_type,
                            }
                        )

                        # Special handling for cue ball (scratch)
                        if ball_type == "cue":
                            self.events.append(
                                {
                                    "type": "scratch",
                                    "info": "Cue ball potted",
                                    "ball_id": oid,
                                }
                            )

            elif oid in current_ids:
                self.disappear_counts[oid] = 0

        # Process 8-ball rules if enabled and balls were potted
        if self.enable_8ball_rules and new_pots_this_frame:
            cue_potted = any(
                self.ball_types.get(oid) == "cue" for oid in new_pots_this_frame
            )
            rule_result = self.rules_engine.handle_shot(
                new_pots_this_frame, self.ball_types, cue_potted
            )

            # Add rule events to our events
            for event in rule_result.get("events", []):
                self.events.append(event)

        # Reset shot tracking when no balls are moving (simplified)
        if len(current_ids) > 0 and self.shot_in_progress:
            # In a real implementation, check if all balls have stopped moving
            # For now, we'll just reset after a delay
            pass

        # keep last 100 events
        self.events = self.events[-100:]

    def _was_near_pocket(self, oid):
        hist = self.track_history.get(oid, [])
        if not hist:
            return False
        last = hist[-1]
        for px, py, pr in self.pockets:
            if dist(last, (px, py)) <= pr * 1.2:
                return True
        return False

    def get_state(self):
        active_by_type = defaultdict(int)
        for oid in self.track_history:
            if oid not in self.potted_ids:
                ball_type = self.ball_types.get(oid, "unknown")
                active_by_type[ball_type] += 1

        base_state = {
            "potted": self.score.get("potted", 0),
            "cue_potted": self.score.get("cue_potted", 0),
            "solid_potted": self.score.get("solid_potted", 0),
            "stripe_potted": self.score.get("stripe_potted", 0),
            "active_balls": len(
                [i for i in self.track_history if i not in self.potted_ids]
            ),
            "active_cue": active_by_type["cue"],
            "active_solid": active_by_type["solid"],
            "active_stripe": active_by_type["stripe"],
            "total_tracked": len(self.track_history),
        }

        # Add 8-ball rules state if enabled
        if self.enable_8ball_rules:
            rules_state = self.rules_engine.get_state_summary()
            base_state.update(rules_state)

        return base_state

    def reset_game(self):
        """Reset game state"""
        self.potted_ids.clear()
        self.last_shot_potted.clear()
        self.shot_in_progress = False
        self.score.clear()
        if self.enable_8ball_rules:
            self.rules_engine.reset_game()
        self.events.append({"type": "game_reset", "info": "New game started"})

    def consume_events(self):
        evs = list(self.events)
        self.events.clear()
        return evs
