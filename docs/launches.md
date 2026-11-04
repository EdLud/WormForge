# Launching a weapon that isn't on the panel

Since 0.9.8.

Some components fire another weapon's missiles with `wa.weapons.launch`
without a worm ever using that weapon. Project X's oil drums are one: the
nuke drum bursts into the Nuke Rocket's rockets. A missile needs its weapon's
record, and a weapon only has a record in a match when it has a slot. Up to
0.9.7 only a weapon placed on the panel had one.

`launches` gives the weapon a slot without putting it on the panel.

## Declaring it

In the component's entry in `mod.toml`:

```toml
[[components]]
id = "px.oil_drums"
type = "feature"
entry = "components/oil_drums.lua"
launches = ["px.nuke_rocket"]
```

Any component may declare it, a weapon or an add-on. List every weapon your
code passes to `wa.weapons.launch` by its id.

## What a profile gets

**If the profile places the weapon,** nothing changes: it is an ordinary
weapon on the panel.

**If the profile doesn't place it,** the weapon is loaded for the match off
the panel:

- It gets a slot after every placed weapon, so the placed ones keep theirs.
- Its `install` runs after the placed weapons. `ctx.launch_only` is `true`
  and `ctx.position` is `nil`. Its own options take their defaults, and
  `ctx.data` is its defaults.
- Its record, sprites and sounds load, as a placed weapon's do.
- No team holds it: it has no ammo, no crate brings it, no turn grant gives
  it, and it isn't on the panel or the F-keys. The profile's weapon settings
  don't apply to it.

The match, peers and replays get it from the same manifests as everything
else, so every player runs the same weapon.

## What your code sees

| | A weapon only launched |
|---|---|
| `wa.weapons.launch{ weapon = id, ... }` | fires it as itself |
| `wa.weapons.data(id)` | its record |
| A missile's `m.weapon`, missile and explosion events | its id |
| `collects_crates` in its data | applies to its missiles |
| `ctx.weapons`, `ctx.placed` | not listed |
| `ctx.selected(id)` | `false` |
| `worm:ammo`, `worm:equip`, `worm:delay`, `wa.weapons.click`, `wa.weapons.fire`, `wa.weapons.notify_grant`, `wa.weapons.panel_icon`, `wa.panel.set_layout` | absent, as a weapon not on the panel |

A rule that deals or counts weapons from `ctx.placed` (Highlander's pools)
never sees it, so it is never dealt.

**A bundle that sets up its weapons from `ctx.weapons`** (Project X's shared
loader does) must set up the launched weapon itself, because `ctx.weapons`
doesn't list it. The oil drums do it with `loader.also("weapons/nuke_rocket")`.

## Errors

The profile can't be built when a component launches:

- a weapon that isn't installed,
- an add-on: only a weapon can be launched,
- a diagnostics-only weapon, on a public build.

WA's own weapons need no entry: `wa.weapons.launch{ weapon = "stock.mine" }`
launches WA's Mine from its own slot, placed or not.

## `launches` or `requires`

`requires` says another component must be selected. The profile is refused
until the player places or ticks it. Use it when your component needs that
component to run for the player.

`launches` loads a weapon only so that your code can fire its missiles. The
player doesn't have to do anything.

## Older WormForge versions

WormForge 0.9.7 and older don't know `launches` and refuse the whole
`mod.toml` that uses it. Publish a pack that uses it only once the release
that reads it is out.
