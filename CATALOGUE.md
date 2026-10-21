# Catalogue workspace

`catalogue/` is a Git submodule of
[EdLud/WormForge-mods](https://github.com/EdLud/WormForge-mods).
Edit Lua, assets, profiles, pack versions and `catalogue.toml` there. Its Git
history is independent of this website; commit and push the mods revision
before committing the website's new submodule pointer.

```sh
git submodule update --init --recursive
python3 -m pip install -r catalogue/requirements.txt
python3 catalogue/tools/test_catalogue.py
python3 tools/build-catalogue.py --check --site .
python3 tools/build-catalogue.py --site . --channel staging
```

The builder uses only a clean committed mods revision, signs with the existing
external key, verifies the complete candidate, and updates local downloads.
Review the source pointer and generated downloads together. Building never
commits, pushes or deploys them.

This local checkout uses `origin` for `EdLud/WormForge` (staging) and `upstream`
for `ropahektic/WormForge` (production). Its catalogue migration is prepared on
`catalogue-submodule`, starting from current production. Publishing to the
staging fork is separate from promoting to production.

Promote the same tested mods commit, rebuild against production's retained store
with `--channel production`, and review before deploying. Production players
continue to use the existing catalogue URL. Historical version manifests and
blobs must remain available, including when a pack or profile leaves the current
catalogue.

The [mods README](https://github.com/EdLud/WormForge-mods#catalogue-checks-and-builds)
is the detailed workflow. No signing seed belongs in either repository or in
public CI. The validation workflow uses temporary test keys and never publishes.
