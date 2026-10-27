# Requirements and compatibility

## What you need

- **Worms Armageddon 3.8.1** with WormKit modules enabled: `wkLua.dll` sits
  next to `WA.exe`.
- **Windows 10 or later.** On macOS or Linux, Wine or CrossOver works.
  Windows 7 and 8 cannot load WormForge. WA then shows:

  > Failed to load WormKit module wkLua.dll: LoadLibrary failed: Error
  > 0000007F

  and WormForge writes no log.
- **The Direct3D 9 (shader) renderer**, picked in WA's graphics options.
  WormForge draws its own sprites, animated GIFs, effects, tooltips and fog of
  war through it. With any other renderer the match still runs, but those
  are not drawn.
- **The same WormForge version for every player** in an online match.
  
## WormKit modules

These WormKit modules don't work:

### wkFKeyRearrange: causes desyncs in online matches

 **Remove `wkFKeyRearrange.dll` from your WA
folder before playing online with WormForge.**


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
