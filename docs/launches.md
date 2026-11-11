# Launching a weapon that isn't on the panel

A component can fire another weapon's missiles with `wa.weapons.launch`
without any worm using that weapon. Project X's oil drums do: the nuke drum
bursts into the Nuke Rocket's rockets. A missile needs its weapon's record,
and a weapon has a record only when it has a slot. `launches` gives the
weapon a slot without putting it on the panel.

## Declaring it

In the component's entry in `mod.toml`:

```toml
[[components]]
id = "px.oil_drums"
type = "feature"
entry = "components/oil_drums.lua"
launches = ["px.nuke_rocket"]
```

Any component can declare it, a weapon or an add-on. List every weapon your
code passes to `wa.weapons.launch`, by its id. Stock weapons need no entry:
`wa.weapons.launch{ weapon = "stock.mine" }` always works.

## What a profile gets

**If the profile places the weapon,** nothing changes: it is an ordinary
weapon on the panel.

**If the profile doesn't place it,** the weapon is loaded off the panel:

- It gets a slot after every placed weapon, so the placed ones keep theirs.
- Its `install` runs after the placed weapons, with `ctx.launch_only = true`
  and `ctx.position = nil`. Its options and `ctx.data` are its defaults.
- Its record, sprites and sounds load as a placed weapon's do.
- No team holds it: no ammo, no crates, no turn grants, no panel entry. The
  profile's weapon settings don't apply to it.

Peers and replays get it like everything else, so every player runs the same
weapon.

## What your code sees

| | A weapon only launched |
|---|---|
| `wa.weapons.launch{ weapon = id, ... }` | fires it as itself |
| `wa.weapons.data(id)` | its record |
| A missile's `m.weapon`, missile and explosion events | its id |
| `collects_crates` in its data | applies to its missiles |
| `ctx.weapons`, `ctx.placed` | not listed |
| `ctx.selected(id)` | `false` |
| `worm:ammo`, `worm:equip`, `worm:delay`, `wa.weapons.click`, `wa.weapons.fire`, `wa.weapons.notify_grant`, `wa.weapons.panel_icon`, `wa.panel.set_layout` | absent, as for any weapon not on the panel |

A rule that deals weapons from `ctx.placed`, such as Highlander's pools,
never deals it.

A bundle that sets up its weapons from `ctx.weapons`, as Project X's loader
does, has to set up the launched weapon itself. The oil drums call
`loader.also("weapons/nuke_rocket")`.

## Errors

The profile can't be built when a component launches:

- a weapon that isn't installed,
- an add-on: only a weapon can be launched,
- a diagnostics-only weapon, on a public build.

## `launches` or `requires`

`requires` says another component must be selected: the profile is refused
until the player places or selects it. Use it when your component needs that
component to run.

`launches` loads a weapon only so that your code can fire its missiles. The
player doesn't have to do anything.
