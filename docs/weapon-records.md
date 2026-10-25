# Weapon records

A **record** is WA's built-in description of a weapon: how it fires, how its
projectiles behave, and which sounds and sprites it uses. WormForge exposes
these settings as named Lua tables. The names describe behaviour established
through reverse engineering; some native parameters remain unresolved.

A Project X `.wep` file stores this weapon data together with PX metadata.
Importing it supplies the firing behaviour and a default name. Supply custom
art and Lua behaviour through the bundle's usual declarations and callbacks.

## Start with an existing weapon

In a weapon component's install function:

```lua
wa.weapons.replace{
  copy_from = "stock.grenade",
  name = "Heavy Grenade",
  missile = {
    gravity_pct = 150,
    explosion = { power = 60, push_pct = 120 },
  },
}
```

Unspecified settings inherit from the base. Alternatively, use
`wep = "weapons/example.wep"` with a bundle-relative path; `wep` and
`copy_from` are mutually exclusive. Named settings override the imported
values. Profile settings, such as shots and turn-ending behaviour, can apply
further overrides for a match (the profile settings).

For a complete port, see [Chilli Bomb](https://github.com/EdLud/WormForge-mods/blob/main/px/weapons/chilli_bomb.lua):
its record settings, art and Lua behaviour live in the same weapon module.

Choose a base close to the intended behaviour. Several stock weapons share
the same **family**:

| Family | Examples | Settings |
|---|---|---|
| `missile` | Bazooka, Grenade, Sheep, Old Woman | `missile`, `clusters` |
| `gun` | Shotgun, Uzi, Minigun, Handgun | `gun` |
| `strike` | Air Strike, Napalm Strike | `strike`, plus `missile` and `clusters` for their munitions |
| `mine` | Mine | `mine` |
| `special` | Fire Punch, Drill, Jet Pack | Settings specific to that native behaviour |
| `arrow`, `spray` | Longbow, Flame Thrower | Inherited behaviour; dedicated named parameter groups are not exposed yet |

Missiles also have an `action`: `"none"`, `"homing"`, `"bounce"`, `"roam"`
or `"dig"`. Use the corresponding settings below. Primary projectiles and
cluster bits have independent actions.

Setting `action = "bounce"` alone does not make a projectile behave like a
Grenade: collision flags, fuse/countdown settings and bounce parameters also
contribute. Changing the action can change how WA interprets inherited
parameters. For a grenade-like weapon, start with `copy_from = "stock.grenade"`
and change the settings you need.

WormForge rejects fields from the wrong family, and action/payload mismatches
when those selectors are explicitly supplied in the same declaration.

## Values and units

Most numeric fields take whole numbers. `_pct` means percentage, with `100`
as the reference value; `_deg` means degrees. Times are milliseconds.
Speeds documented in pixels/frame use WA's 50 simulation frames per second.
Collision targets use boolean tables. Remaining native bitmasks and effect
selectors use integers; inherit them unless you have a tested replacement.
Enum fields accept the names shown below or native integer values.

### Firing and handling

| Field | Meaning |
|---|---|
| `fires.launch_power_pct` | Missile launch power. `50` is 50%; values above 100 are allowed. `"charged"` or `0` enables charging on launched/thrown weapons. Placement does not become chargeable. |
| `fires.type`, `fires.method` | Native firing-family and method selectors. Normally inherit them from the base. |
| `fires.subtype` | Family-dependent native parameter. Selects a special weapon's particular behaviour; no gameplay use has been identified for strikes. Normally inherit it from the base. |
| `fires.creates_projectile` | Native firing flag. Its detailed effect is not fully documented; inherit it. |
| `handling.remember_selection` | Whether WA remembers and may re-equip this weapon between turns. Does not enable a crosshair. |
| `handling.shots` | Number of uses in a firing sequence, such as the Shotgun's two shots. |
| `handling.ends_turn` | Whether using the weapon ends weapon use for the turn. |
| `handling.retreat` | Native retreat-time setting in milliseconds; preserve inherited special values unless tested. |

### Turn utilities

`utility.effect` selects the native effect of a turn utility: `"low_gravity"`,
`"fast_walk"`, `"laser_sight"`, `"invisibility"`, `"damage_x2"`, `"crate_spy"`,
`"double_turn_time"` or `"crate_shower"`. It requires a turn-utility base,
such as `stock.fast_walk`; it does not apply to Jet Pack or other specials.
Using the weapon toggles its effect for the team; ammo and turn handling
remain the weapon's own settings.

Use `utility = { effect = "scripted" }` when Lua supplies the effect, as
Wind Changer and Gravity Control do. The native use still completes, without
activating a stock utility. This field does not configure Auto-Use.

### Missiles and explosions

Fields below belong under `missile` unless another table is named.

| Field | Meaning |
|---|---|
| `speed_pct`, `gravity_pct`, `wind_pct` | Multipliers for initial speed, gravity and wind response. |
| `random_motion` | Native random-motion parameter. |
| `ends_on_contact` | Named targets whose contact ends the projectile and runs its configured payload. Applies before flight as well as during it. |
| `impact_particles` | Enables the brief particle trail after impact, as used by Holy Hand Grenade. Preserves collision settings when changed on its own. |
| `collision_shape` | Native numeric collision-outline preset; changes physical clearance without resizing the sprite. Inherit it unless you have tested another preset. |
| `alarm_worms` | Allows a nearby worm's alarm cry shortly before the primary projectile's timed explosion. Requires a worm within the native proximity limit. |
| `countdown`, `fuse` | Native countdown and explosion timing in milliseconds. Their interaction depends on the base weapon. |
| `explode_on_space` | Enables the native Space-triggered action. |
| `burst` | Payload: `"nothing"`, `"clusters"` or `"fire"`. |
| `fire.spread_delay_ms` | With `burst = "fire"`, delay before a flame produces the next spreading generation. Native fire checks this in 20 ms steps. |
| `fire.burn_time_ms` | With `burst = "fire"`, nominal settled burn time for ordinary fire. Falling pauses natural decay, and native randomness can shorten the burn. Persistent native fire modes consume this reserve on hits instead. This is not an exact lifetime from creation; `0` does not mean unlimited. |
| `fire.spread_generations` | With `burst = "fire"`, nonnegative whole number of successive spreading generations. `0` retains only the initial flames. Each generation may branch into several flames; this is not a flame count. |
| `fire.decay_mode` | With `burst = "fire"`, `"resting"` consumes the burn reserve while settled; `"on_hit"` consumes it through hits instead. Water and other native extinguishing rules still apply. |
| `explosion.power` | Combined explosion damage and radius, as in WA's weapon power. |
| `explosion.push_pct` | Knockback percentage. Zero removes push while retaining explosion power. |
| `explosion.bias`, `explosion.variation` | Native explosion bias and damage variation. |
| `sprite`, `animation` | Flight sprite and native animation selector. |
| `trail = { sprite, power, speed }` | Visual trail settings. Trail speed does not change projectile speed. |
| `trail.bubbles_per_second` | Underwater bubble emission rate, in steps of `0.25`. `0` disables emission. Independent of the dry trail settings; homing has its own value under `homing.trail`. |
| `flight_sound` | Native flight sound ID; zero disables it. |
| `launch_sound` | Positional sound played once when the primary projectile is created; `0` disables it. Cluster children do not replay it. |
| `explosion_sound = { enabled, sound, before }` | Optional native pre-explosion sound; `before` is milliseconds. |

### Missile actions

Port tables omit storage for unselected actions. Shared particles after
impact, such as the Holy Hand Grenade effect, are preserved independently
of the selected action.

These groups belong under `missile` and require the matching `action`.

| Group | Fields and meaning |
|---|---|
| `bounce` | `bounciness`: extra bounce relative to WA's Grenade (`0`); Banana Bomb uses `60`. `terrain_keep_speed_pct`: percentage of speed retained on terrain contact. `sound`: bounce sound. `max_bounces`: bounce limit; `0` leaves the normal fuse behaviour. |
| `bounce` | `hits`: named targets for physical collisions, added to `ends_on_contact`. `explosion = { bias, push_pct, power, variation }`: the bounce action's contact-explosion parameters. |
| `bounce` | `contact_sides`: native contact-side bitmask controlling which contacts count toward the bounce limit and trigger contact explosions. Separate from object collision flags. `extra_reverse_chance_pct`: percentage chance of an additional horizontal reversal and a kick based on vertical speed, before normal collision processing. |
| `homing` | `kind`: `"off"`, `"lock"` or `"dodge"`. `arm`, `time`: arming delay and homing duration in milliseconds. `sprite`, `animation`, `trail = { sprite, power, speed, bubbles_per_second }`: presentation during homing. |
| `roam` | `walk_speed`: pixels/frame, in steps of `0.02`. `step_height`: maximum vertical terrain search in whole pixels, upward or downward, while walking; independent of jump strength. `terrain_offset`: signed vertical drawing adjustment while grounded. `hits`: additional ordinary movement collision targets. `flight_hits`: additional collision targets during steered animal flight. Both retain contacts required by `ends_on_contact`. |
| `roam.edge_jump`, `roam.jump` | Each takes `angle_deg`, `speed`, `sound`. Speed is nominal pixels/frame, in steps of `0.06`; WA varies it by roughly one sixth in either direction. Negative native angle values can trigger explosion behaviour. |
| `roam.gas` | `start_delay_ms`: nonzero arms an emission countdown; zero leaves it unarmed. `poison_power`: native poison-message amount. `animal_sprite`: the emitting animal's pose. |
| `dig` | `sound`, `dive_sprite`, `sprite_1`, `sprite_2`, `sprite_3`: digging sound and native dive/digging art. |

For roaming Super/Aqua Sheep, `sheep.flight_1` and `sheep.flight_2` select
the two native flying sprites. Use `sheep_sprites` for bundle art.

### Collision targets

Use boolean tables for `ends_on_contact`, `bounce.hits`, `roam.hits`,
`roam.flight_hits`, `gun.hits` and `mine.detects`:

```lua
missile = {
  ends_on_contact = { worms = true },
  bounce = { hits = { land = true } },
}
```

This projectile bounces on land and ends on ordinary worm contact. The
contact-ending targets always participate in collision checks. An empty
`hits = {}` clears the additional targets; omitted settings inherit the base.
Supplying a target table replaces that field's entire target selection:
only entries set to `true` are selected. Omitted or `false` entries are
excluded, rather than preserving individual targets from the base.
Changing `hits` preserves inherited impact particles, and changing
`impact_particles` preserves inherited collision targets.

Targets are `land`, `worms`, `mines`, `crates`, `donor_cards`, `graves`,
`missiles`, `arrows`, `objects` (oil drums and body actors), `water` and the
legacy `canisters`. Selection still follows WA's other collision rules.

`worms` covers ordinary worms. Frozen worms have separate targets. For exact
partial selections, use the following instead of the `worms` shortcut:

| Target | Native group |
|---|---|
| `worms_normal` | Standing, walking, ready, jump preparation/descent and parachuting. |
| `worms_acting` | Firing, melee, getting up, falling, being hit, dying and related action states. |
| `worms_jumping` | Jumping and jetpacking. |
| `worms_roping` | Rope and bungee. |
| `worms_frozen` | Stationary frozen worms. |
| `worms_frozen_moving` | Moving frozen worms. |

These are WA's existing groups; a worm can change groups during one jump.
Do not combine `worms` with its four constituent ordinary groups in one table.
Unmapped imported bits can be preserved with `extra_bits`; shipped PX masks
need no such values.

The former numeric spellings `collides`, `bounce.flags`,
`roam.movement_flags`, `roam.explode_flags` and `gun.hit_flags` remain accepted
and readable for compatibility. Do not combine a numeric alias with its new
name, or with `impact_particles` when they share the same native word.
`mine.detects` accepts named targets while retaining its existing numeric
readback through `wa.weapons.data`.

### Clusters

`clusters.bit` uses the missile body fields and action groups for the child
projectile, plus `sprite_count`. The parent and child can behave differently.
The primary header settings `collision_shape` and `alarm_worms` have no
independent `clusters.bit` equivalents.

| Field | Meaning |
|---|---|
| `clusters.count` | Number of emitted cluster projectiles. |
| `clusters.angle`, `clusters.spread` | Native emission angle and angular spread; preserve special angle values from the base. |
| `clusters.launch_power_pct` | Cluster launch strength relative to 24 pixels/frame. |
| `clusters.power_variation_pct` | Random reduction in cluster launch strength, up to this percentage. |

The two power fields apply to cluster payloads, including the alternate
native cluster mode. They do not apply to fire payloads.
For fire payloads, use `missile.fire` for spreading generations, delay, burn
reserve and decay mode. The legacy `clusters.count` and `clusters.angle`
spellings remain writable for compatibility; reading a fire record returns
the fire names. Inherit untested native decay-mode numbers from the base.

### Guns, mines, strikes and special behaviours

| Group | Fields and meaning |
|---|---|
| `gun` | `bullets`: rounds in the firing sequence. `shot_interval_ms`: interval between rounds. `burst_size`: projectiles emitted per round. `spread_deg`, `burst_spread_deg`: angular spread, centred on the aim. |
| `gun` | `damage`: damage per projectile. `hits`: named raycast targets. `impact_effect`: native visual effect selector. `explosion = { bias, push_pct, variation }`: impact parameters. |
| `mine` | `proximity`: detection radius. `arm`: arming delay in milliseconds. `detects`: named proximity targets. `fuse`: triggered fuse in milliseconds. `explosion = { bias, push_pct, power }`: explosion parameters. |
| `strike` | `count`: dropped munitions. `spacing`: native drop-spacing parameter. `plane`: native plane sprite. `munition`: `"mines"` or `"missiles"`. |
| `strike` | `munition_speed`: initial horizontal speed of dropped munitions along the plane's direction, in pixels/frame, in steps of `0.01`. Does not set the aircraft's speed. `plane_sound`: native aircraft sound ID; `0` disables it. |
| `fire_punch` | `damage`: hit damage. `knockback`: victim's hit strength in pixels/frame, in steps of `0.1`, before native hit modifiers. Applies only to Fire Punch behaviour. |
| `drill` | `duration_ms`: Pneumatic Drill duration. |
| `jet_pack` | `fuel`: native Jet Pack fuel setting, `0` to `255`; `0` means unlimited. |
| `parachute` | `wind_pct`: wind response percentage; `100` is normal and `0` ignores wind. This does not change arrow-key steering or initial momentum. |

## Sprites and other declarations

Record sprite fields accept stock sprite names or numeric IDs. Bundle artwork
uses the separate declarations `sprite`, `cluster.sprite`, `plane`,
`sheep_sprites`, `worm_sprites` and `hold`. For example, a bundle's flight
sheet goes in top-level `sprite`, rather than `missile.sprite`.

The weapon name, panel icon, ammo/crate defaults, component options and Lua
callbacks also use their own declarations, as the bundle guide describes.

## Reading and per-shot overrides

```lua
local data = wa.weapons.data("stock.grenade")
local power = data.missile.explosion.power
local family = data.fires.as  -- read-only family name
```

Use a placed weapon's ID to read its current match record. This includes
`stock.<name>` when that stock weapon is placed; otherwise a stock ID reads
WA's untouched template. Read after the match's weapon table is ready. The
returned table is a snapshot; editing it changes no weapon. Only settings
appropriate to the record's family, action and payload are returned.

In a simulation callback with a firing event `ev`:

```lua
wa.weapons.launch{
  weapon = "stock.grenade", owner = ev.worm,
  x = ev.x, y = ev.y, vx = ev.vx, vy = ev.vy,
  missile = { explosion = { power = 30 } },
}
```

`launch` accepts `missile` and `clusters` overrides for that shot only. The
source must use a compatible missile firing path. Supplied velocity is in
pixels/frame; `fires.launch_power_pct` does not scale it again.

Scripted children inherit the source weapon's missile settings, independently
of `clusters.bit`. Override child-specific fuse, Space detonation and payload
settings in the launch, as [Chilli Bomb](https://github.com/EdLud/WormForge-mods/blob/main/px/weapons/chilli_bomb.lua) does.

Unresolved settings remain accessible through `raw` for existing ports and
advanced experimentation. Prefer named fields wherever available. A field
having a name does not mean every native flag, sentinel or interaction has
been fully documented.
