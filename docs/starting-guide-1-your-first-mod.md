# WormForge starting guide, part 1: Your first mod

This guide is for people who write Lua and want to mod Worms Armageddon with
WormForge. Part 1 builds one small weapon from an empty folder, plays it, and
sets out the few rules every mod follows. The later parts go deeper, one
subject each.

The weapon is the **Moon Grenade**: WA's Grenade with about a third of the
gravity, where one burst in four also digs a crater. The finished mod is
[examples/starting_guide](https://github.com/EdLud/WormForge-mods/tree/main/examples/starting_guide)
in the mods repository.

The short version:

- A **mod** is a folder in `WormForge/Mods/` with a `mod.toml` and Lua files.
  It offers **components**: weapons, and features (anything that isn't a
  weapon).
- Nothing in a mod runs by itself. A **profile** picks the weapons and
  features a game uses, and where each weapon sits on the panel.
- A weapon's file returns its data and an `install` function, which builds
  the weapon on one of WA's own:
  `wa.weapons.replace{ copy_from = "stock.grenade", ... }`.
- Put your mod beside `wf-lib`, never inside it.
- Your files are read again at every match start: edit, save, start a new
  match.
- Online, the host's profile and mods travel to every player. Replays carry
  them too.
- Three rules: a weapon is an id, never a slot number; Lua speaks pixels;
  only the simulation changes the game.

## What a mod is

A mod is what you install; a profile is what you play.

- A **mod** is a folder: `mod.toml`, which names the mod and lists its
  components, plus their Lua files, sprites and sounds. A mod has no on/off
  switch: every installed mod is there for every profile to use.
- A **component** is one thing a mod offers. A **weapon** goes on the panel.
  A **feature** is anything else: a rule, an effect, a HUD. The loader calls
  features *add-ons*. Every component has an id, unique among all installed
  mods.
- A **profile** is what a game runs: its weapons and where each sits on the
  panel, each weapon's settings (ammo, delay, crates, ...), the features and
  their options, and WA's game scheme. Players make profiles in the loader
  and save them in `WormForge/Profiles/`. A mod can ship its own, in its
  `profiles/` folder.

When a match starts, only what the profile selects runs. The rest of an
installed mod costs nothing: none of its code runs, none of its sprites load.

> **Coming from Project X.** A PX library, with its scripts, `.wep` weapons
> and files, becomes a mod. A PX `.wep` can still be a weapon's base:
> `wep = "weapons/name.wep"` in place of `copy_from` (part 2).

## Where your mod lives

WormForge keeps everything in one folder, `WormForge`, next to `WA.exe`:

```text
Worms Armageddon/
  WA.exe, wkLua.dll
  wkLua.log, wkluaerror.txt     what WormForge logs (see below)
  WormForge/
    wormforge.toml              the loader's settings and the profile being edited
    Profiles/                   saved profiles
    Mods/
      wf-lib/                   mods installed from the catalogue: the loader's
      starting_guide/           your mod
```

The **Open Mods folder** button in the WormForge Mods window opens `Mods/`.
If WA's folder can't be written to (an install under Program Files), the
`WormForge` folder is `%LOCALAPPDATA%\WormForge` instead.

### wf-lib belongs to the loader

**Install** and **Update all** put each mod from the online catalogue in a
folder of its own in `Mods/wf-lib/`, and remember every file they wrote.

- **Make your own mod beside `wf-lib`, never inside it,** under an id of
  your own. The catalogue's installs and updates never touch such a mod.
- Edit a file inside `wf-lib`, and that mod shows **Local changes**: Update
  all skips it from then on. **Replace (backup)** installs the catalogue's
  copy again and moves yours to `WormForge/Backups/Packs/`.
- `wf-lib/...` is also how shared code is named: a library mod can offer
  modules that other mods load with `require("wf-lib/<name>")`. A later part
  covers it; it has nothing to do with where your files go.

### To change someone else's mod

Copy its folder out of `wf-lib` into `Mods/`, then give the copy its own
identity:

- a new `id` in its `mod.toml`, and a new id for each of its components. Two
  installed mods may not offer the same component: while they do, no profile
  loads ("component ... is declared by both ...");
- the same new ids in its `profiles/`, and wherever its Lua names its own
  weapons.

A folder whose name starts with `_` or `.` is skipped, which keeps an old
copy out of the game.

## The files

```text
starting_guide/
  mod.toml
  weapons/
    moon_grenade.lua
  profiles/
    Moon Grenade.toml
```

`mod.toml` and the `profiles/` folder have fixed names. The rest is yours to
arrange; `mod.toml` says where each file is.

### mod.toml

```toml
id = "example.starting_guide"
name = "Starting guide"
version = "0.1.0"
author = "WormForge"
api_version = 4
format_version = 2

[[components]]
id = "guide.moon_grenade"
type = "weapon"
name = "Moon Grenade"
description = "WA's Grenade with about a third of the gravity. One burst in four also digs a crater."
entry = "weapons/moon_grenade.lua"
icon = "grenade"
default_position = { row = "F2", column = 6 }
```

| Key | What it is |
|---|---|
| `id` | The mod's id: lowercase letters, digits, `.`, `_` and `-`. |
| `name`, `version`, `author` | What the loader shows on the mod's card. |
| `api_version`, `format_version` | `4` and `2`: the Lua API and the `mod.toml` format the mod is written for. WormForge refuses a mod written for others, and says why. |
| `[[components]]` | One block per weapon or feature. |
| component `id` | Unique among all installed mods: up to 64 lowercase letters, digits, `.`, `_` and `-`. `stock.` is taken: it names WA's own weapons. Start yours with something of your own, as `guide.` here. |
| `type` | `"weapon"` or `"feature"`. |
| `name` | What players read, in the loader and, for a weapon, in the game. |
| `description` | A sentence for the loader. |
| `entry` | The component's Lua file, inside the mod. |
| `icon` | A weapon's picture in the loader: one of WA's weapons by name, or a 32x32 `.png` in the mod. |
| `default_position` | Where the weapon goes when a player adds it to a profile: a row (`"F1"` to `"F12"`, or `"utility"`) and a column from 1 to 10. If that place is taken, the first free one. WA's own F2 row ends at column 5, so column 6 is free. |

Everything else `mod.toml` can hold is optional; later parts bring it in as
they need it.

### The weapon file

A component's file runs when a match loads, and returns what the component
is. For a weapon, that is a table with two keys:

```lua
-- Moon Grenade: WA's Grenade with about a third of the gravity.
-- One burst in four also digs a crater.

return {
  -- The weapon's data. The profile's settings for it (the loader's
  -- Manage Weapon Panel) are laid over these, field by field.
  defaults = {
    ammo = { round_start = 3 },
  },

  install = function()
    local last_crater -- set by the simulation, shown by the HUD

    wa.weapons.replace{
      copy_from = "stock.grenade",
      missile = { gravity_pct = 35 },

      -- Simulation: runs on every player's machine at the same moment,
      -- so it may change the game and roll WA's dice.
      on_explode = function(ev)
        if wa.random(4) == 1 then
          wa.land.cut{ x = ev.x, y = ev.y, shape = "circle", radius = 40 }
          last_crater = ("%d, %d"):format(math.floor(ev.x), math.floor(ev.y))
          wa.log("crater at " .. last_crater)
        end
      end,
    }

    -- Drawing: runs on each machine when it draws a frame, so it only reads.
    wa.on.hud(function()
      if last_crater then
        wa.hud.line("Moon Grenade: last crater at " .. last_crater)
      end
    end)
  end,
}
```

- `defaults` is the weapon's **data**: here, three Moon Grenades at the start
  of a round (`-1` would be infinite). Players change it for their profile
  in the loader's **Manage Weapon Panel**, and what they set is laid over
  your defaults, field by field. Part 2 lists every field.
- `install` builds the weapon. `wa` is for `install` and what it sets up:
  the file itself only returns data, and a use of `wa` while it runs is
  refused. `install` also receives a `ctx` table, with where the weapon was
  placed and its data; part 2 covers it.
- `wa.weapons.replace{ ... }` makes the weapon. `copy_from = "stock.grenade"`
  starts from WA's Grenade, `missile = { gravity_pct = 35 }` changes one of
  its settings (35% of WA's gravity), and everything not named stays the
  Grenade's. [Weapon records](weapon-records.md) lists what can be changed.
  It names no slot and no name: it makes the weapon the profile placed, and
  the name is the one in `mod.toml`.
- `on_explode` runs where the grenade bursts, with its position in `ev.x`,
  `ev.y`. One time in four, it cuts a 40-pixel circle out of the land there.
- `wa.on.hud` adds a line to the screen once there is a crater to report.
  Every match runs the file afresh, so `last_crater` starts empty each match.

In the game's weapon panel, the Moon Grenade shows the Grenade's icon, the
weapon it copies. Part 2 gives it one of its own.

### The profile

`profiles/Moon Grenade.toml` places the Moon Grenade next to what you need
to try it:

```toml
description = "The starting guide's Moon Grenade, with WA's Grenade beside it to compare, a Ninja Rope and Skip Go."

[weapons]
"guide.moon_grenade" = true
"stock.grenade" = true
"stock.ninja_rope" = true
"stock.skip_go" = true

[weapon_settings."stock.ninja_rope"]
ammo = -1
```

- `[weapons]` is the panel. `true` puts a weapon at its default position; a
  profile saved by the loader gives each one a row and a column instead. WA's
  own weapons are listed the same way, by id.
- A profile that lists weapons owns the whole panel: the weapons it doesn't
  list aren't in the game. This one has four.
- `[weapon_settings."stock.ninja_rope"]` gives the rope infinite ammo
  (`-1`). The Moon Grenade has no settings here, so it keeps its defaults:
  three.
- A profile also holds WA's game scheme. This one sets none of it, so it
  plays Intermediate's settings, whatever scheme the lobby shows.

## Try it

1. Copy the `starting_guide` folder into `WormForge/Mods/`.
2. Start WA. The WormForge Mods window opens beside it. If WA was already
   running, press **Refresh** in that window.
3. In the profile line at the top of the window, switch **My profiles** to
   **Bundled profiles** and pick **Moon Grenade — Starting guide**. That opens
   a working copy of the mod's profile; saving it under a name of yours makes
   it one of your profiles.
4. Start an offline game: a hotseat match with two teams is quickest. As it
   loads, the game says *Weapons come from the WormForge profile, not the
   lobby's weapon settings*.
5. Press F2 until the Moon Grenade is selected, and throw it. It floats.
   Throw a few more: about one in four leaves a crater, and the screen shows
   *Moon Grenade: last crater at ...*.

To use the Moon Grenade in another profile, open the loader's **Manage
Weapon Panel**, search for it and double-click it.

## When something goes wrong

Two files next to `WA.exe` tell you what happened:

- **`wkLua.log`**: everything WormForge logs, your own lines included.
  `wa.log("...")` writes one, tagged with your component's id:
  `[guide.moon_grenade] crater at 812, 403`. Lua's `print` doesn't reach the
  log; use `wa.log`.
- **`wkluaerror.txt`**: the errors alone. It starts empty each time WA
  starts, so look here first.

| What's wrong | Where it shows |
|---|---|
| A mistake in `mod.toml` | The mod's card in the WormForge Mods window says *doesn't load:*, with every problem. |
| A Lua error as the match loads: a typo, a field that doesn't exist | The game says *WormForge: the profile's mods failed to load (...). Playing plain WA.*, and `wkluaerror.txt` has the error. |
| A Lua error in a callback during play | `wkluaerror.txt` names the callback and the error (`missile on_explode: ...`); the game goes on. |

## Changing your mod

- Lua files, sprites, sounds and `mod.toml` are read again at the start of
  every match. Save, start a new match, and your change is in it: no need to
  restart WA. A match already running keeps what it loaded.
- After adding a mod folder or a profile file, press **Refresh** in the
  WormForge Mods window to see it.
- An opened bundled profile is a working copy: after editing
  `profiles/Moon Grenade.toml`, pick it again from Bundled profiles.
- Only a new WormForge (`wkLua.dll`) needs WA restarted.

## Online and in replays

The other players don't need your mod installed:

- When the **host lights the ready bulb**, WormForge copies the host's
  profile and every mod it uses (with the libraries they need), and sends
  them to every player in the lobby. The game can start only once every
  player has them; until then the host's lobby says what the start is
  waiting for.
- Every machine then plays the host's copy: the same code and the same
  settings, whatever each player has in their own `Mods/`.
- What the host edits after lighting the bulb doesn't reach that game. Put
  the bulb out and light it again to send the new version.
- Every player needs WormForge, the same version as the host's. A player
  without it can't play a game with mods: the start waits, and says so.
- A **replay** carries the profile and the mods' files the same way, so it
  plays on a machine that doesn't have your mod, with your code as it was
  when the game was played.

## Three rules

### 1. A weapon is an id, never a slot

WA numbers its weapons by slot. WormForge keeps those numbers away from
Lua: a weapon is its **id**. `stock.grenade` is WA's Grenade,
`guide.moon_grenade` is yours. The profile decides where a weapon sits, so
the same file works wherever a player puts it, next to any other mod's
weapons. Wherever Lua names a weapon, it uses the id: `copy_from`, a
profile's `[weapons]`, the `weapon` of an event such as `on_explode`'s `ev`.

### 2. Lua speaks pixels

Positions and sizes are in pixels, speeds in pixels per frame (WA runs 50
frames a second), and fractions are fine: `ev.x` may be `812.5`, which is
why the Moon Grenade rounds it down to print it. WormForge converts to and
from WA's own units; you never multiply by 65536.

### 3. The simulation changes the game; drawing only looks

In an online game every machine runs the whole match itself, and only the
players' keys travel between them. So whatever changes the game must come
out the same on every machine. WormForge splits your code in two:

- **Simulation callbacks** run on every machine at the same moment of the
  game: a weapon's callbacks, such as `on_explode`, and the `wa.on` events
  such as `turn_start`, `hurt` or `worm_message`. They may change the game:
  cut land, move and hurt worms, spawn things, change ammo.
- **Drawing callbacks**, `wa.on.draw` and `wa.on.hud`, run on each machine
  whenever it draws a frame, and each machine draws at its own pace. They
  may read anything and change nothing: WormForge refuses a change to the
  game from them, with an error.

The Moon Grenade does both: `on_explode` cuts the land and records
`last_crater`; the HUD only reads it.

What goes with it:

- **Dice:** `wa.random(n)` gives a whole number from 1 to n from WA's own
  dice, the same on every machine and in replays. Simulation only. Lua's
  `math.random` is gone; for looks, in drawing, `wa.draw.random()` gives a
  number from 0 to 1.
- **Angles:** where the result reaches the game, use `wa.math.sin`,
  `wa.math.cos` and `wa.math.atan`. Lua's `math.sin` and its kin can differ
  in the last digit between machines; in drawing they are fine.
- **Order:** `pairs()` walks a table in a different order on each machine.
  Where the order matters to the game, walk a list with `ipairs`, or a
  table's keys with `wa.sorted(t)`.
- **No outside world:** there is no `io`, `os` or `load`, and each mod's
  `require` loads only its own files.

> **Coming from Project X.** STEPS's Friendly Mine, improved by 0rang3,
> shows all three in PX's terms:
>
> ```cpp
> override void CWorm::FireFinal(CWeapon* Weap,CShootDesc* Desc)
> // ...
>         if (Weap->CheckName("Friendly Mine"))
> // ...
>       local AddFuse = GS->GetRandom() % 12 * 125;
> // ...
> void FriendlyMine::Render()
> ```
>
> - PX hooks every worm's shot and asks which weapon it is by its name. In
>   WormForge the code sits in the weapon's own file, and a weapon is named
>   by its id, which stays the same whatever the weapon is called.
> - `GS->GetRandom()` is WA's dice, as `wa.random` is.
> - `Render()` is drawing, as `wa.on.draw` and `wa.on.hud` are.
> - PX's `float` was already WA's units counted in pixels: `SpY = -9` there
>   is a speed of `-9` here too.

## Next

Part 2, *Weapons*, goes through a weapon component in full: every field of
its data, the `ctx` its `install` receives, and what `wa.weapons.replace`
can change.

See also:

- [Weapon records](weapon-records.md): everything a weapon's record holds.
- [Moving actors](actor-movement.md): things your Lua spawns, and how they
  move.
- The [verb list](https://ropahektic.github.io/WormForge/capabilities.html#verb=wa.weapons.replace)
  on the capabilities page: every `wa` function.
