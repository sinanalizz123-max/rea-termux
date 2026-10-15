#!/data/data/com.termux/files/usr/bin/python3
"""Merge APKMirror-style split APKs into one installable, aligned, sign-ready APK.

Pure stdlib (zipfile/struct/zlib) — no zipalign needed (x86-only binary won't
run on Termux ARM). Reproduces what matters for the Play installer:

- drops duplicate AndroidManifest.xml / META-INF from splits (base wins)
- stores .so + resources.arsc UNCOMPRESSED (INSTALL_FAILED_INVALID_APK otherwise)
- 4-byte alignment for resources.arsc, 16KB page alignment for .so files
  (Android 12+ mmap requirement) via extra-field padding
- raw DEFLATE streams (zlib.compress adds headers/footers that strict parsers
  reject — use compressobj(wbits=-15))

Also usable to binary-patch the manifest first (e.g. remove
requiredSplitTypes/splitTypes that force multi-split installs).

Usage:
    python3 apk-merge.py base.apk split1.apk [split2.apk ...] -o merged.apk
Then sign, e.g.: apksigner sign --ks key.jks --out signed.apk merged.apk
"""
import struct
import sys
import zipfile
import zlib
import binascii


def raw_deflate(data):
    c = zlib.compressobj(6, zlib.DEFLATED, -15)
    return c.compress(data) + c.flush()


def main():
    args = sys.argv[1:]
    out = args[args.index("-o") + 1]
    ins = [a for a in args if a != "-o" and a != out]
    raw = {}
    for path in ins:
        with zipfile.ZipFile(path) as zin:
            for n in zin.namelist():
                if n.startswith("META-INF/"):
                    continue
                if n in raw:
                    print("SKIP dup:", n, "from", path)
                    continue
                raw[n] = zin.read(n)
    order = sorted(raw)
    stored_of = lambda n: (n == "resources.arsc" or n.endswith(".so"))
    pay = {n: (raw[n] if stored_of(n) else raw_deflate(raw[n])) for n in order}
    U16 = lambda v: struct.pack("<H", v)
    U32 = lambda v: struct.pack("<I", v)
    with open(out, "wb") as f:
        recs = []
        for n in order:
            nb = n.encode()
            align = 16384 if n.endswith(".so") else 4
            pad = (-(f.tell() + 30 + len(nb) + 4)) % align
            extra = (b"\x00\x00" + U16(pad) + b"\x00" * pad) if pad else b""
            crc = binascii.crc32(raw[n]) & 0xFFFFFFFF
            comp = 0 if stored_of(n) else 8
            off = f.tell()
            f.write(U32(0x04034B50) + U16(20) + U16(0) + U16(comp) + U16(0) + U16(0)
                    + U32(crc) + U32(len(pay[n])) + U32(len(raw[n])) + U16(len(nb)) + U16(len(extra)))
            f.write(nb + extra + pay[n])
            recs.append((nb, crc, len(pay[n]), len(raw[n]), comp, off, extra))
        cdpos = f.tell()
        for nb, crc, cs, us, comp, off, extra in recs:
            f.write(U32(0x02014B50) + U16(20) + U16(20) + U16(0) + U16(comp) + U16(0) + U16(0)
                    + U32(crc) + U32(cs) + U32(us) + U16(len(nb)) + U16(len(extra))
                    + U16(0) + U16(0) + U16(0) + U32(0) + U32(off))
            f.write(nb + extra)
        cdlen = f.tell() - cdpos
        f.write(U32(0x06054B50) + U16(0) + U16(0) + U16(len(recs)) + U16(len(recs))
                + U32(cdlen) + U32(cdpos) + U16(0))
    print("wrote", out, len(recs), "entries")


if __name__ == "__main__":
    main()
