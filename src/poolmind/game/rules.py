"""
8-Ball Pool game rules and logic
"""

from enum import Enum
from typing import Any, Dict, Optional, Set


class BallType(Enum):
    CUE = "cue"
    SOLID = "solid"
    STRIPE = "stripe"
    EIGHT = "eight"


class GameState(Enum):
    BREAK = "break"
    OPEN_TABLE = "open_table"
    SOLID_PLAYER = "solid_player"
    STRIPE_PLAYER = "stripe_player"
    EIGHT_BALL = "eight_ball"
    GAME_OVER = "game_over"


class EightBallRules:
    """8-Ball pool game rules implementation"""

    def __init__(self):
        self.state = GameState.BREAK
        self.current_player = 1
        self.player_types = {}  # player_id -> BallType
        self.game_won = False
        self.winner = None
        self.scratched = False

    def reset_game(self):
        """Reset to initial state"""
        self.state = GameState.BREAK
        self.current_player = 1
        self.player_types = {}
        self.game_won = False
        self.winner = None
        self.scratched = False

    def handle_shot(
        self,
        potted_balls: Set[int],
        ball_types: Dict[int, str],
        cue_potted: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a shot and return game events

        Args:
            potted_balls: Set of ball IDs that were potted
            ball_types: Mapping of ball ID to ball type string
            cue_potted: Whether cue ball was potted (scratch)

        Returns:
            Dict with events and state changes
        """
        events: list[Dict[str, Any]] = []

        # Convert string types to enum
        typed_balls = {}
        for ball_id in potted_balls:
            ball_type_str = ball_types.get(ball_id, "unknown")
            if ball_type_str == "cue":
                typed_balls[ball_id] = BallType.CUE
            elif ball_type_str == "solid":
                typed_balls[ball_id] = BallType.SOLID
            elif ball_type_str == "stripe":
                typed_balls[ball_id] = BallType.STRIPE
            elif ball_type_str == "eight":
                typed_balls[ball_id] = BallType.EIGHT

        self.scratched = cue_potted

        if self.state == GameState.BREAK:
            return self._handle_break(typed_balls, events)
        elif self.state == GameState.OPEN_TABLE:
            return self._handle_open_table(typed_balls, events)
        elif self.state in [GameState.SOLID_PLAYER, GameState.STRIPE_PLAYER]:
            return self._handle_normal_shot(typed_balls, events)
        elif self.state == GameState.EIGHT_BALL:
            return self._handle_eight_ball_shot(typed_balls, events)

        return {
            "events": events,
            "state": self.state.value,
            "current_player": self.current_player,
        }

    def _handle_break(
        self, potted_balls: Dict[int, BallType], events: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle break shot"""
        # On break, any ball potted continues turn (except 8-ball which loses)
        eight_ball_potted = any(
            ball_type == BallType.EIGHT for ball_type in potted_balls.values()
        )

        if eight_ball_potted:
            events.append(
                {
                    "type": "eight_ball_break_loss",
                    "info": "8-ball potted on break - game over",
                }
            )
            self.state = GameState.GAME_OVER
            self.winner = 2 if self.current_player == 1 else 1
            self.game_won = True
        elif self.scratched:
            events.append({"type": "break_scratch", "info": "Scratch on break"})
            self._switch_player()
            self.state = GameState.OPEN_TABLE
        elif potted_balls:
            events.append(
                {
                    "type": "break_made",
                    "info": f"{len(potted_balls)} balls potted on break",
                }
            )
            self.state = GameState.OPEN_TABLE
            # Player continues
        else:
            events.append({"type": "break_miss", "info": "No balls potted on break"})
            self._switch_player()
            self.state = GameState.OPEN_TABLE

        return {
            "events": events,
            "state": self.state.value,
            "current_player": self.current_player,
        }

    def _handle_open_table(
        self, potted_balls: Dict[int, BallType], events: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle shot when table is still open"""
        if not potted_balls or self.scratched:
            events.append({"type": "miss", "info": "No balls made or scratch"})
            self._switch_player()
        else:
            # First ball type potted determines player type
            first_type = next(iter(potted_balls.values()))
            if first_type == BallType.SOLID:
                self.player_types[self.current_player] = BallType.SOLID
                self.state = (
                    GameState.SOLID_PLAYER
                    if self.current_player == 1
                    else GameState.STRIPE_PLAYER
                )
                events.append(
                    {
                        "type": "group_assigned",
                        "info": f"Player {self.current_player} assigned solids",
                    }
                )
            elif first_type == BallType.STRIPE:
                self.player_types[self.current_player] = BallType.STRIPE
                self.state = (
                    GameState.STRIPE_PLAYER
                    if self.current_player == 1
                    else GameState.SOLID_PLAYER
                )
                events.append(
                    {
                        "type": "group_assigned",
                        "info": f"Player {self.current_player} assigned stripes",
                    }
                )

        return {
            "events": events,
            "state": self.state.value,
            "current_player": self.current_player,
        }

    def _handle_normal_shot(
        self, potted_balls: Dict[int, BallType], events: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle normal shot during game"""
        player_type = self.player_types.get(self.current_player)

        # Check if player potted their own balls
        own_balls_potted = sum(
            1 for ball_type in potted_balls.values() if ball_type == player_type
        )
        opponent_balls_potted = sum(
            1
            for ball_type in potted_balls.values()
            if ball_type != player_type and ball_type != BallType.CUE
        )

        if self.scratched or opponent_balls_potted > 0:
            events.append({"type": "foul", "info": "Scratch or opponent ball potted"})
            self._switch_player()
        elif own_balls_potted > 0:
            events.append(
                {
                    "type": "legal_pot",
                    "info": f"Player {self.current_player} potted {own_balls_potted} ball(s)",
                }
            )
            # Check if all group balls are cleared for 8-ball shot
            # This would require tracking all balls on table - simplified for now
        else:
            events.append({"type": "miss", "info": "No balls made"})
            self._switch_player()

        return {
            "events": events,
            "state": self.state.value,
            "current_player": self.current_player,
        }

    def _handle_eight_ball_shot(
        self, potted_balls: Dict[int, BallType], events: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle 8-ball shot"""
        eight_potted = any(
            ball_type == BallType.EIGHT for ball_type in potted_balls.values()
        )

        if eight_potted:
            if self.scratched:
                events.append(
                    {
                        "type": "eight_ball_loss",
                        "info": "8-ball potted with scratch - game over",
                    }
                )
                self.winner = 2 if self.current_player == 1 else 1
            else:
                events.append(
                    {
                        "type": "eight_ball_win",
                        "info": f"Player {self.current_player} wins!",
                    }
                )
                self.winner = self.current_player
            self.state = GameState.GAME_OVER
            self.game_won = True
        elif self.scratched:
            events.append({"type": "scratch", "info": "Scratch on 8-ball attempt"})
            self._switch_player()
        else:
            events.append({"type": "eight_ball_miss", "info": "8-ball attempt missed"})
            self._switch_player()

        return {
            "events": events,
            "state": self.state.value,
            "current_player": self.current_player,
        }

    def _switch_player(self):
        """Switch to other player"""
        self.current_player = 2 if self.current_player == 1 else 1

    def get_state_summary(self) -> Dict[str, Any]:
        """Get current game state summary"""
        return {
            "game_state": self.state.value,
            "current_player": self.current_player,
            "player_types": {str(k): v.value for k, v in self.player_types.items()},
            "game_won": self.game_won,
            "winner": self.winner,
            "scratched": self.scratched,
        }
