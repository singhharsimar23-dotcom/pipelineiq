from dataclasses import dataclass
from typing import Dict

@dataclass
class Primitive:
    name: str
    arity: int  # number of parameters beyond action
    cost: float  # bits contributed to |P|

GAME_DSL: Dict[str, Primitive] = {
    "move": Primitive(name="move", arity=3, cost=2.5),
    "toggle_interaction": Primitive(name="toggle_interaction", arity=2, cost=2.5),
    "toggle_display": Primitive(name="toggle_display", arity=2, cost=2.0),
    "rotate": Primitive(name="rotate", arity=2, cost=2.0),
    "scale": Primitive(name="scale", arity=2, cost=2.5),
    "set_position": Primitive(name="set_position", arity=3, cost=3.0),
    "win_check": Primitive(name="win_check", arity=2, cost=2.0),
    "next_level": Primitive(name="next_level", arity=0, cost=1.0),
}
