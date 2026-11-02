<div align="center">

![description](https://i.imgur.com/6Yfe1p6.png)

<a href="https://edlud.github.io/WormForge">Web Weapon Editor</a>

<a href="docs/verbs.md">Lua verbs</a>

<a href="https://github.com/EdLud/WormForge/releases">Download</a>

<a href="https://github.com/ropahektic/WormForge-engine">Engine Repo</a> 

WormForge is a Lua modding layer for WA 3.8.1 that lets you code custom weapon and scheme behaviour.

You don’t need to be a C++ reverse engineer or even a programmer to ship something. Read the [guides](docs/starting-guide-1-your-first-mod.md), drop a folder under `Mods/`, pick its weapons and add-ons for your profile in the mod loader and you’re in. The module ships working examples — Highlander rules with a full custom weapon arsenal, turrets, swimming worms, worm toss, random sprite swaps, inventory demos, custom vehicles and much much more — so you can learn and/or copy.

Replays and WormNET are supported out of the box. Start from the [site](https://edlud.github.io/WormForge), check [features](docs/verbs.md), grab a [build](https://github.com/EdLud/WormForge/releases), enable an example, and see how far past “just another scheme” you can push a match or improve existing schemes.

**INSTALL:** Drop `wkLua.dll` next to `WA.exe`, click **Check Online** and **Install**.

**REQUIRES:** Windows 10 or later (or Wine/CrossOver), WormKit, Direct3D 9 (shader). Some WormKit modules clash with WormForge: [Requirements and compatibility](docs/requirements.md)

**STATUS:** Stable, but replay backwards compatibility is not yet guaranteed.

</div>

## Credits

Originally created by [ropahektic](https://github.com/ropahektic/), now maintained by [EdLud](https://github.com/EdLud), with contributions from [reddaz](https://github.com/reddazxfi).

**Project X.** The Project X ports bring PX's weapons, rules and art to WormForge, from 0rang3's current PX build. Project X is by Entuser and many authors. Each port is credited to the authors its PX scripts name:

0rang3 · Curtis · Danylo · DannyB · Entuser · [\_Kilburn](https://github.com/UnderscoreKilburn) · Pablo · PyroMan · rafa\`\`2 · raffie · ravander · reddaz · StepS · Twicken · Zed

The mod loader shows who made each weapon. If a name is missing or wrong, please open an issue.

**Code and ideas from other WormKit modules:**

- [wkVista](https://github.com/ropahektic/wkVista) by [Ropa](https://github.com/ropahektic/) (MIT): full-colour maps and zoom, rebuilt on WormForge's own renderer
- [wkZoom](https://github.com/ConnerPetzold/wkZoom) by [Syc](https://github.com/ConnerPetzold/), used with permission: smooth zoom
- [wkJellyWorm](https://github.com/rm-rf-worms/wkJellyWorm) by [nizikawa](https://github.com/rm-rf-worms), with [JSG](https://github.com/jsgnextortex/)'s improvements in [wkJollyWorm](https://github.com/jsgnextortex/wkJellyWorm/tree/Wkjollyworm): weapon-record research
- [wkRGBA](https://github.com/rUNaW4y/wkRGBA) by [rUNaW4y](https://github.com/rUNaW4y): the idea of giving WA a proxy map, so a full-colour map still plays and replays without the module

**Core utilities:** Agility by Zed and 0rang3, ExTurnSide and Live HP by reddaz.

Worms Armageddon is © Team17. WormForge is a fan project, not affiliated with or endorsed by Team17.
