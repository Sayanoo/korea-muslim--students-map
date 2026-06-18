r"""Decode UbiReport inline zlib blobs (resultHeader/resultBody/etc.) from an
academyinfo.go.kr RdViewer HTML page.

The viewer embeds report data as JS string literals where each byte of a
zlib stream is encoded as \uXXXX (low 8 bits) or a short escape for control
bytes. We reconstruct the bytes and inflate.
"""
import re
import sys
import zlib


# JS short escapes used by the encoder -> byte value.
_SHORT = {
    "t": 0x09, "n": 0x0A, "r": 0x0D, "f": 0x0C,
    "b": 0x08, "v": 0x0B, "e": 0x00, "0": 0x00,
    "\\": 0x5C, " ": 0x20,
}


def extract_literal(html: str, var: str) -> str | None:
    """Return the raw JS string-literal contents assigned to `var`."""
    # Matches:  var x = '...';  /  x = "...";  /  obj.params.x = '...';
    pat = re.compile(re.escape(var) + r"""\s*=\s*(['"])(.*?)\1\s*;""", re.S)
    m = pat.search(html)
    if not m:
        return None
    # The HTML stores each backslash doubled (JS source-level escaping).
    # Collapse one level so UbiReport's own \uXXXX / short escapes remain.
    return m.group(2).replace("\\\\", "\\")


def to_bytes(literal: str) -> bytes:
    out = bytearray()
    i = 0
    n = len(literal)
    while i < n:
        c = literal[i]
        if c == "\\" and i + 1 < n:
            nxt = literal[i + 1]
            if nxt == "u" and i + 5 < n:
                hexpart = literal[i + 2:i + 6]
                out.append(int(hexpart, 16) & 0xFF)
                i += 6
                continue
            if nxt in _SHORT:
                out.append(_SHORT[nxt])
                i += 2
                continue
            # unknown escape -> the literal char
            out.append(ord(nxt) & 0xFF)
            i += 2
            continue
        out.append(ord(c) & 0xFF)
        i += 1
    return bytes(out)


def inflate(data: bytes) -> bytes:
    return zlib.decompress(data)


def decode_var(html: str, var: str) -> bytes | None:
    lit = extract_literal(html, var)
    if lit is None:
        return None
    raw = to_bytes(lit)
    return inflate(raw)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "pipeline/data/raw/rdviewer_item33.html"
    with open(path, encoding="utf-8") as f:
        html = f.read()
    for var in ("resultHeader", "resultBody", "resultSum", "strQuery", "resultMaster"):
        try:
            out = decode_var(html, var)
        except Exception as exc:  # noqa: BLE001
            print(f"=== {var}: DECODE FAILED: {exc!r} ===")
            continue
        if out is None:
            print(f"=== {var}: not found ===")
            continue
        print(f"=== {var}: {len(out)} bytes inflated ===")
        sys.stdout.buffer.write(out[:1200])
        sys.stdout.write("\n\n")
