# DSL GAP REPORT: COMPLETE ARCENGINE API ENUMERATION (v0.9.3)
**Author:** PipelineIQ Research Lead  
**Engine Source:** `tools/engine_source/arcengine` & `tools/engine_source/arc_agi`  

---

## 1. Class & Method Enumeration

| Class | Method / Property | Parameters | Reversible | Target Environments | Priority |
|:---|:---|:---|:---:|:---|:---:|
| `Sprite` | `move(dx, dy)` | `dx: int, dy: int` | Yes | `ls20, wa30, tr87, sp80, su15, ka59, lf52, m0r0, r11l, s5i5, sb26, tu93, lp85, re86, ar25, bp35, cd82` | **CORE (INCLUDED)** |
| `Sprite` | `set_interaction(mode)` | `mode: InteractionMode` | Yes | `cn04, dc22, ft09, g50t, lp85, re86, cd82, ar25, bp35` | **CORE (INCLUDED)** |
| `Sprite` | `set_visible(bool)` | `visible: bool` | Yes | `vc33, tn36, sk48, sc25, cd82, su15, lf52` | **CORE (INCLUDED)** |
| `Sprite` | `rotate(delta)` | `delta: int (90° inc)` | Yes | `lp85, g50t, sk48` | **CORE (INCLUDED)** |
| `Sprite` | `set_scale(scale)` | `scale: int` | Yes | Procedural hidden scaling puzzles | **CORE (INCLUDED)** |
| `Sprite` | `set_position(x, y)` | `x: int, y: int` | Yes | Dynamic entity teleportation | **CORE (INCLUDED)** |
| `Sprite` | `color_remap(old, new)`| `old: int, new: int` | Yes | `ft09, cn04, dc22, vc33, tn36, sc25` | **HIGH (INCLUDED)** |
| `Sprite` | `merge(other)` | `other: Sprite` | No | Compound object assembly | **MEDIUM** |
| `Sprite` | `set_mirror_ud/lr(bool)`| `mirror: bool` | Yes | `m0r0, lf52` mirror reflections | **MEDIUM** |
| `Sprite` | `set_blocking(mode)` | `mode: BlockingMode` | Yes | Ghost/pass-through barriers | **MEDIUM** |
| `ARCBaseGame` | `try_move_sprite(...)` | `sprite, dx, dy` | Yes | Collision-aware entity translation | **CORE (INCLUDED)** |
| `ARCBaseGame` | `win()` / `next_level()`| `None` | No | All 25 public + 75 hidden games | **CORE (INCLUDED)** |
| `ARCBaseGame` | `_get_valid_clickable_actions`| `None` | — | `lp85, vc33, ft09, dc22, tn36, cd82` | **HIGH (INCLUDED)** |
