# Land stamps next to worms

`wa.land.stamp` writes a sprite into the map as solid land. If any of that
new land lands on a worm, the worm is stuck inside it. This page shows how
the Javelin (px.ports) ran into this and how it now avoids it. The same check
fits any weapon that stamps land where worms can be.

## The issue

When a Javelin hits land, it stamps a spear centred on the impact. The front
half lies in the ground and fades into it, so the spear looks stuck:

```lua
wa.land.stamp{
  sprite = "sprites/javelin/stamp.png", frame = frame, x = ev.x, y = ev.y,
  buried = { soften = 3, blend = "mix" },
}
```

The back half points back along the flight, toward whoever threw it. When a
worm throws almost straight down into the ground at its own feet, that back
half is new land right through the worm's body, and the worm can't move.

Turrets such as the Sentry Gun don't have this problem because they never
stamp land. A turret is an actor with its own collision shape, drawn behind
the terrain, and it lets its planter walk out before it starts blocking him.
A stamp is plain land, so a stamp has to be placed where it holds no worm.

## The fix

Before stamping, the Javelin checks the spear against every worm near the
impact:

1. **At the impact:** if the spear holds no worm, it sticks there, as before.
2. **Deeper:** otherwise it moves forward along its flight a pixel at a time,
   deeper into the land, until it clears every worm. Its tail may go up to
   10 px past the impact, and a step counts only while the spear's point is in
   land, so it never ends up floating in the air.
3. **Hit instead:** if no depth clears, the worm it can't clear takes the
   Javelin's normal hit (20 damage and a push) and nothing is stamped.

### Describe the stamp's shape

The test needs the shape of what is stamped. For the Javelin it was measured
from `stamp.png`: frame `f` points `f * 11.25` degrees clockwise from up, and
the spear reaches 20 px either way from its centre and about 4 px either side
of its axis. A worm is WA's 9x16 shape, with its hotspot at (4, 9).

```lua
local SHAFT, HALF_WIDTH, DEEPEST = 20, 4, 30
local function holds(w, cx, cy, dx, dy, solid)
  local x0, x1 = math.floor(w.x) - 4, math.floor(w.x) + 4
  local y0, y1 = math.floor(w.y) - 9, math.floor(w.y) + 6
  for t = -SHAFT, SHAFT do
    for s = -HALF_WIDTH, HALF_WIDTH do
      local px = math.floor(cx + dx * t - dy * s + 0.5)
      local py = math.floor(cy + dy * t + dx * s + 0.5)
      -- Land already there gains nothing: the spear's buried part.
      if px >= x0 and px <= x1 and py >= y0 and py <= y1 and not solid(px, py) then return true end
    end
  end
  return false
end
```

Pixels that are land already don't count: stamping over them changes nothing
for the worm.

### Find a place that clears every worm

```lua
local rad = math.rad(frame * 11.25)
local dx, dy = wa.math.sin(rad), -wa.math.cos(rad)
-- ...
for d = 0, DEEPEST do
  local cx, cy = x + dx * d, y + dy * d
  if d == 0 or solid(math.floor(cx + dx * SHAFT + 0.5), math.floor(cy + dy * SHAFT + 0.5)) then
    held = nil
    for _, w in ipairs(near) do
      if holds(w, cx, cy, dx, dy, solid) then held = w; break end
    end
    if not held then return cx, cy, d end
  end
end
return nil, held
```

`near` holds the living worms within 80 px of the impact, sorted by `id`.
Everything that decides where land goes runs the same on every machine:
`wa.math.sin` / `wa.math.cos` instead of `math.sin` / `math.cos`, a fixed worm
order, and only `+ - * /` and `math.floor` otherwise.

### Stamp there, or hit the worm

```lua
sx, sy, deeper = plant(ev.x, ev.y, frame)
if not sx then
  target = sy  -- the worm no depth clears takes the hit below
end
-- ...
wa.land.stamp{
  sprite = "sprites/javelin/stamp.png", frame = frame, x = sx, y = sy,
  buried = JAVELIN_BURIED,
}
```

## In game

- A Javelin thrown into the ground at the thrower's feet sticks deeper, its
  tail at the surface, and the thrower can walk away.
- A Javelin that bursts in the air on its own thrower now hits him and leaves
  no spear. Before, he took no damage and the spear was stamped around him.
- Both cases are logged in `wkLua.log` as `Javelin: ...` lines.

Replays recorded with an older px.ports in which a Javelin stuck next to a
worm no longer play back.
