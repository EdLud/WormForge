# Land stamps next to worms

`wa.land.stamp` writes a sprite into the map as solid land. If any of that
new land lands on a worm, the worm is stuck inside it. This page shows how
the Javelin (px.ports) ran into this, and the small library that now places
its spear and the Girder Launcher's girder clear of every worm. The same check
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
half is new land right through the worm's body, and the worm can't move. The
Girder Launcher's girder has the same back half: fired at a wall the shooter
stands against, it would be laid through him.

Turrets such as the Sentry Gun don't have this problem because they never
stamp land. A turret is an actor with its own collision shape, drawn behind
the terrain, and it lets its planter walk out before it starts blocking him.
A stamp is plain land, so a stamp has to be placed where it holds no worm.

## The fix

Before stamping, the weapon checks the stamp against every worm near the
impact:

1. **At the impact:** if the stamp holds no worm, it goes there, as before.
2. **Deeper:** otherwise it moves forward along its flight a pixel at a time,
   deeper into the land, until it clears every worm. Its back end may go up to
   10 px past the impact, and a step counts only while its front end is in
   land, so it never ends up floating in the air.
3. **Hit instead:** if no depth clears, the worm it can't clear takes the
   weapon's normal hit (the Javelin's 20 damage, the Girder Launcher's 3, each
   with a push) and nothing is stamped.

## The library: `lib/stuck_stamp.lua`

px.ports keeps this rule in one file, `px/lib/stuck_stamp.lua`, which the
Javelin and the Girder Launcher share. Another pack can carry a copy of it in
its own `lib/`.

```lua
local stuck_stamp = require("lib/stuck_stamp")
local x, y, deeper = stuck_stamp.place(ev.x, ev.y, frame, bar)
```

- `ev.x`, `ev.y` is the impact, and `frame` the stamp's frame.
- `bar` describes the stamp as a bar along its frame's axis:
  `{ half_length = ..., half_width = ... }`, in pixels from its centre.
- It returns the centre to stamp at and how many pixels deeper that is, or
  `nil` and the worm it cannot clear.

It assumes the sheet's frame `f` points `f * 11.25` degrees clockwise from
up, as PX's 32-frame spear and girder sheets do. Both were measured from their
PNGs: the spear is 20 px each way along its axis and 4 px across, the girder
11 and 4.

The Javelin, with its spear:

```lua
local SPEAR = { half_length = 20, half_width = 4 }
-- ...
local frame = orientation(vx, vy)
local sx, sy, deeper
if not target then
  sx, sy, deeper = stuck_stamp.place(ev.x, ev.y, frame, SPEAR)
  if not sx then
    target = sy  -- the worm no depth clears takes the hit below
  end
end
if target then
  target.vx, target.vy = vx / 4, vy / 4
  if target.kind == "worm" then target:hurt(20)
  else target:hit(20, vx / 2, vy / 2, "projectile") end
  return
end
wa.land.stamp{
  sprite = "sprites/javelin/stamp.png", frame = frame, x = sx, y = sy,
  buried = JAVELIN_BURIED,
}
```

The Girder Launcher does the same with `{ half_length = 11, half_width = 4 }`
and its own hit, and stamps its girder without `buried`, drawn whole over
the land.

## How it checks

### Where the stamp's pixels land

The engine plots a stamp around the pixel its position rounds down to, so
the check starts from `math.floor(x)`, `math.floor(y)`. The bar's pixels are
listed once per frame and size, as offsets from that pixel. Half-pixel steps
along and across leave no pixel out when the bar lies on a slant:

```lua
for t2 = -2 * bar.half_length, 2 * bar.half_length do
  for s2 = -2 * bar.half_width, 2 * bar.half_width do
    local t, s = t2 / 2, s2 / 2
    local ox, oy = math.floor(dx * t - dy * s + 0.5), math.floor(dy * t + dx * s + 0.5)
    -- kept once each in `list`
  end
end
```

### Whether they hold a worm

A worm is WA's 9x16 shape, with its hotspot at (4, 9). The check keeps the
stamp a pixel clear of it on every side, so a pixel of error in the sprite's
measurements can't trap a worm. Pixels that are land already don't count:
stamping over them changes nothing for the worm.

```lua
local function holds(w, px, py, list, solid)
  local x0, x1 = math.floor(w.x) - 5, math.floor(w.x) + 5
  local y0, y1 = math.floor(w.y) - 10, math.floor(w.y) + 7
  for _, o in ipairs(list) do
    local x, y = px + o[1], py + o[2]
    -- Land already there gains nothing: the stamp's buried part.
    if x >= x0 and x <= x1 and y >= y0 and y <= y1 and not solid(x, y) then return true end
  end
  return false
end
```

### Going deeper

```lua
for d = 0, bar.half_length + 10 do
  local cx, cy = x + dx * d, y + dy * d
  local px, py = math.floor(cx), math.floor(cy)
  if d == 0 or solid(px + math.floor(dx * bar.half_length + 0.5), py + math.floor(dy * bar.half_length + 0.5)) then
    held = nil
    for _, w in ipairs(near) do
      if holds(w, px, py, list, solid) then held = w; break end
    end
    if not held then return cx, cy, d end
  end
end
return nil, held
```

`near` holds the living worms within 80 px of the impact, sorted by `id`.
Everything that decides where land goes runs the same on every machine:
`wa.math.sin` / `wa.math.cos` for the axis instead of `math.sin` /
`math.cos`, a fixed worm order, and only `+ - * /` and `math.floor`
otherwise.
