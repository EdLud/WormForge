# Moving actors

An **actor** is anything a pack spawns with `wa.actors.spawn`: a bee, a
turret, a bouncing ball, a shell casing. This page is about how it moves and
how it learns what it ran into. The short version: decide **who moves it**,
WA or your Lua, and never both.

## Who moves your actor

| Your actor… | Spawn it with | It moves by | Example |
|---|---|---|---|
| flies or walks by itself and must stop at land | `body = { hits = { land = true, ... } }`, `gravity = false` (or `true` for a walker) | WA, every frame; you set `a.vx`, `a.vy` to steer | a bee, a drone |
| is thrown, lands, bounces and comes to rest | `body = { physics = "mine" }` | WA, as it moves a mine | the Sentry Gun's turret |
| is decoration and touches nothing | no `body`, `collide = false`, `gravity = false` | your Lua: `a:gravity()` and `a:move{}` each frame | a shell casing |

**WA moves any actor that collides with something or has gravity.** Every
frame, before your `frame` callback runs, WA's own collision code moves it by
its speed. That is the code that moves mines, grenades and worms: it steps
pixel by pixel, stops the actor at land and at whatever its `body.hits`
allows, and never lets it sink into terrain.

**WA does not move an actor that collides with nothing and has no gravity.**
Nothing moves it unless your Lua does.

### Don't add a second step

`a:move{ terrain = true, worms = false }` is not WA's collision code. It adds
the actor's speed to its position once, and reports whether there is land
under its feet. It does not stop at land, bounce or meet worms.

On an actor WA already moves, `a:move()` is a second step on top of WA's: the
actor goes twice as fast, and that second step can push it into land.

Use `a:move()` only for actors WA doesn't move (the third row above).

## Steering an actor WA moves

Set its speed; WA does the rest.

```lua
wa.actors.spawn{
  sprite = "sprites/bee.png", x = x, y = y,
  gravity = false,
  body = { shape = "sprites/bee_mask.png", hits = { land = true, worms = true } },
  on = {
    frame = function(a)
      -- steer toward a target: change the speed a little each frame
      a.vx = a.vx + (want_vx - a.vx) * 0.15
      a.vy = a.vy + (want_vy - a.vy) * 0.15
    end,
  },
}
```

- `body.hits` is what the actor's own movement stops on: `land`, `worms`,
  `mines`, `crates`, `objects` (oil drums and other bodies), `missiles`.
- `body.hit_by` is what may hit it: blasts, fire, arrows and so on.
- `body.shape` is its outline: a pack image path, `"worm"` (default),
  `"missile"`, or `"sprite"`.
- To jump an actor WA moves to another place, use `a:warp{ x, y, vx, vy }`
  rather than writing `a.x`, `a.y`: it also resets WA's "at rest" state and
  keeps the actor from being drawn sliding across.

## What did it run into?

Three tools, for three questions:

| Question | Tool |
|---|---|
| My own movement ran into something: what, from which side, how fast? | `on.bump` |
| Something moving ran into me: a missile, a worm, a rolling ball | `on.contact` |
| Would I fit at this spot, before I go there? | `a:fits(x, y)` |

### `on.bump`

```lua
on = {
  bump = function(a, ev)
    -- ev.other              "land", or the worm / object / actor it ran into
    -- ev.nx, ev.ny          the side WA reported, pointing away from it
    -- ev.surface_nx, _ny    on a land floor only: the floor's slope, from WA
    -- ev.vx, ev.vy          its speed going in (pixels per frame)
    -- ev.x, ev.y            where it was when WA stopped it
    -- ev.first              true if it wasn't touching this the frame before
    -- ev.frame              the simulation frame
    -- a.vx, a.vy            already WA's response: stopped, or bounced
  end,
}
```

- You get one event per obstacle per frame, after WA has moved everything.
- WA's response is already done when `bump` runs. To do something else, set
  `a.vx`, `a.vy`: that is the speed WA moves it with next frame.
- An actor that keeps pushing against something (resting on a floor, sliding
  along a wall) bumps it every frame. `ev.first` tells a new bump from a
  continuing one.
- `on.bump` needs an actor that collides with something (`body.hits`); an
  actor WA doesn't move never bumps, and spawning one with `bump` is an error.

**The side and the slope.** WA moves a body one axis at a time, sideways
then up or down, and bounces it on the axis it was stopped on. So `ev.nx`,
`ev.ny` is always straight: `(0, -1)` a floor, `(0, 1)` a ceiling, `(1, 0)`
or `(-1, 0)` a wall. On a hillside that is "floor", not the hill's angle.

For the angle, `ev.surface_nx`, `ev.surface_ny` comes from WA's own gradient
routine, the one WA uses to tilt a mine lying on a slope: it needs land right
under the actor and measures the floor's height a few pixels to each side. So
it exists for floors only. Walls, ceilings and bumps into worms or objects
don't have it.

A ball that bounces off everything at a steady speed, using the slope where
there is one:

```lua
bump = function(a, ev)
  local nx, ny = ev.nx, ev.ny
  if ev.surface_nx then nx, ny = ev.surface_nx, ev.surface_ny end
  local d = ev.vx * nx + ev.vy * ny
  if d < 0 then                     -- moving into it: reflect
    local vx, vy = ev.vx - 2 * d * nx, ev.vy - 2 * d * ny
    local len = math.sqrt(vx * vx + vy * vy)
    a.vx, a.vy = vx / len * SPEED, vy / len * SPEED
  end
end,
```

### `on.contact`

`on = { contact = function(a, ev) ... end }` is the other direction:
something WA moved ran into this actor. `ev.other` is what hit it (a missile
that exploded on it arrives as a snapshot with `alive = false`), `ev.vx`,
`ev.vy` its speed going in, `ev.nx`, `ev.ny` the side. WA applies no push for
you: the callback decides. The Highlander sentries use it to be shoved.

### `a:fits(x, y)`

A question, not an event: would the actor's shape at `(x, y)` touch anything
it collides with? Good for finding a free spot to spawn or to pull a stuck
actor out to. It says nothing about what WA did this frame.

## Mine physics

`body = { physics = "mine" }` hands the actor to WA's mine movement: gravity
(on by default), WA's mine bounce (about 60% of the speed back on the axis it
hit), friction, and settling, where WA stops moving a body that has come to
rest. That is right for something thrown that should land and lie still,
like a turret.

What runs into a mine-physics actor pushes it, as mines push each other: WA
trades their speeds. `body.pushed_by = { mines = 0.2 }` keeps only that share
of the push, here a fifth of what a mine gives it (keys `worms`, `missiles`,
`arrows`, `mines`, `actors`; 0 none, 1 WA's whole push). The Electromagnet
uses it so the mines it pulls in can't knock it away.

It is wrong for anything that drives itself: friction and settling eat the
small speed a steering brain adds each frame, and the actor crawls whatever
speed you ask for. A flier or walker wants a plain `body` (first row of the
table).

## Online play

Every machine in an online match runs the whole game itself; only the
players' inputs travel. So everything that changes the game must come out
the same on every machine:

- `frame`, `bump`, `contact` and `hit` are simulation callbacks: they run on
  every machine in the same order, and may change speed, position, health.
- `wa.on.draw` and `wa.on.hud` run on one machine only, to draw: they may not
  change the game.
- Use `wa.random` and `wa.math.sin` / `cos` / `atan`, not Lua's `math.random`
  or `math.sin`, which can differ between machines.

## See also

- `contributing-with-an-agent.md` in the engine repository: the full field
  lists for `wa.actors.spawn`, `body`, `on.bump` and `on.contact`.
- The [verb list](verbs.md#onbump): every `wa` function.
- [Weapon records](weapon-records.md): how a weapon's own projectiles behave.
