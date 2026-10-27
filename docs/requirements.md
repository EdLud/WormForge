# Requirements and compatibility

What WormForge needs to run, and the WormKit modules known to clash with it.

## What you need

- **Worms Armageddon 3.8.1** with WormKit modules enabled: `wkLua.dll` sits
  next to `WA.exe`.
- **Windows 10 or later.** On macOS or Linux, Wine or CrossOver works.
  Windows 7 and 8 cannot load WormForge. WA then shows:

  > Failed to load WormKit module wkLua.dll: LoadLibrary failed: Error
  > 0000007F

  and WormForge writes no log, because none of its code ever runs. This
  will not change: the language WormForge is written in (Rust) needs
  Windows 10.
- **The Direct3D 9 (shader) renderer**, picked in WA's graphics options.
  WormForge draws its own sprites, animated GIFs, effects, tooltips and fog of
  war through it. With any other renderer the match still runs, but those
  are not drawn.
- **The same WormForge version for every player** in an online match. Use
  the mod loader's **Check online → Update all** after updating `wkLua.dll`,
  so everyone also has the same mods.

## WormKit modules

Most WormKit modules work alongside WormForge. These don't:

### wkFKeyRearrange: causes desyncs in online matches

wkFKeyRearrange lets you choose which weapons each F-key cycles through,
from `wkFKeyRearrange.ini`. **Remove `wkFKeyRearrange.dll` from your WA
folder before playing online with WormForge.**

Why: when a player presses an F-key, WA sends the key itself to every
player, and each player's game then works out which weapon that key means,
as part of the shared game simulation. wkFKeyRearrange changes that step on
your machine only, using your `.ini`. So when anyone presses an F-key, your
game can hand their worm a different weapon than everyone else's game does,
and the match falls out of sync: WA reports a desynchronisation and drops a
player. It doesn't matter who presses the key, or whose turn it is.

This was confirmed on a real match (October 2026): replaying it with
wkFKeyRearrange loaded reproduced the desync on the exact frame it happened;
the same replay without it ran clean.

The same applies without WormForge whenever the players' `.ini` files
differ. WormForge also moves weapons between F-key rows (custom panel
layouts, mod weapons on other slots), so with WormForge it happens far more
often.

### wkFOW: use WormForge's own fog of war instead

wkFOW draws in the same places WormForge does, and WormForge then turns its
own drawing off (`wkLua.log` says "bytes differ"). WormForge has fog of war
built in: select the **Fog of war** add-on in a profile.

### Seen working with WormForge

Modules players have used in WormForge matches without known problems:
wkWormNAT2, wkTerrainSync, wkZRealTime, wkRemapKeys, wkSuperFrontend,
wkKick38, wkMapGEN, wkTrackMeBetter381, wkPin and wkWormOrder.

## Reporting a desync

If a match desyncs, send:

- **every player's replay** of that match (`User/Games/*.WAgame` in each
  WA folder: each machine records its own, and comparing them shows where
  and how they split);
- **the list of `wk*.dll` files** in each player's WA folder;
- each player's `wkLua.log`, if they still have it.
