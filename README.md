# rea-termux

Termux-compatible surface for [REA](https://github.com/morluto/rea) (`morluto/rea`) on `android/arm64`.

Upstream REA's JADX/Ghidra/Hopper/IDA engines refuse android/arm64 hosts, so this
wrapper passes through every engine-free REA command and redirects engine-backed
ones to Termux-native fallbacks — all under a strict RAM cap (1 GB heap, ≤2 threads).

## Install

```bash
cp rea-termux ~/bin/rea-termux
chmod +x ~/bin/rea-termux
```

Needs on PATH: `node` (REA checkout at `~/rea`), `java` (JDK 17+), `aapt2`
(Android SDK build-tools), plus `apktool.jar` / skylot `jadx` pointed at by the
env vars at the top of the script. For `decompile-native` you need rizin +
the on-device rz-ghidra build — see
[termux-rz-ghidra](https://github.com/sinanalizz123-max/termux-rz-ghidra).

## Usage

```bash
rea-termux doctor                        # Termux readiness (not upstream doctor)
rea-termux manifest <apk>                # aapt2 badging
rea-termux manifest-xml <apk>            # aapt2 AndroidManifest xmltree
rea-termux package-info <apk>            # package/version/permissions summary
rea-termux decode <apk> <outdir>         # apktool (smali + res, -Xmx1024m)
rea-termux decompile <apk> <outdir>      # skylot jadx, -j 2 (tip: per-dex for big APKs)
rea-termux decompile-native <lib.so> <sym>  # Ghidra pdg via rizin core_ghidra
rea-termux classes <dir> <keyword>       # grep java/smali sources
rea-termux methods <file> <method>       # grep method in jadx output
rea-termux uuids <decoded-dir>           # BT UUID inventory
rea-termux urls <decoded-dir>            # https endpoint inventory
rea-termux <rea-command> [args...]       # passthru for engine-free REA commands
```

Android engine commands (`inspect-android-package`, `search-android-classes`,
`inspect-android-class/method`, `trace-android-references`) are blocked with a
fallback hint — use `decompile` + `classes` instead.

## Provenance

Built while reverse-engineering Nothing X 3.10.0 fully on-device (Termux only,
1.5–1.8 GB RAM cap): full-APK jadx OOMs at 1 GB heap, so big APKs go per-dex
(`unzip` each `classesN.dex`, `rea-termux decompile` one at a time, `-j1`).

Independent community project. Not affiliated with the REA authors.
