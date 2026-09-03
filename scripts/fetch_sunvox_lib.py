#!/usr/bin/env python3
"""Download the SunVox library into thirdparty/ and apply local patches.

The SunVox binaries are not tracked in git. This script fetches the pinned
release, verifies its checksum, and lays it out where CMakeLists.txt expects it.

To bump the library, change SUNVOX_URL and SUNVOX_SHA256 below, or pass
--url/--sha256 once to discover the new checksum via the mismatch error.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

SUNVOX_VERSION = "2.1.4d"
SUNVOX_URL = "https://www.warmplace.ru/soft/sunvox/sunvox_lib-2.1.4d.zip"
SUNVOX_SHA256 = "abe851de9d65a10e06673bf33257154591a2ff63ad2bb298488a5941cc5f4057"

# Subset extracted from the archive. android/, ios/, js/, examples/, make/ and
# main/ are unused by this build; lib_arm/ and the *_lofi variants are never
# selected by CMakeLists.txt. docs/ ships because the SunVox license requires
# the TXT files to accompany the product.
KEEP_DIRS = (
    "docs/",
    "headers/",
    "resources/",
    "linux/lib_arm64/",
    "linux/lib_x86/",
    "linux/lib_x86_64/",
    "macos/lib_arm64/",
    "macos/lib_x86_64/",
    "windows/lib_x86/",
    "windows/lib_x86_64/",
)
DROP_NAMES = ("sunvox_lofi.so", "sunvox_lofi.dll")

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "thirdparty" / "sunvox_lib"
CACHE = ROOT / "thirdparty" / ".cache"
STAMP = DEST / ".fetched"

# Local edits to headers/sunvox.h. Each entry is (description, before, after).
# Exact matches are required: if upstream changes any of this text the patch
# fails loudly rather than silently reverting or misapplying.
HEADER_PATCHES = [
    (
        "LPCTSTR needs windows.h, which is only included under SUNVOX_MAIN",
        """    #define LIBNAME "sunvox.dll"
    typedef LPCTSTR LIBNAME_STR_TYPE;
""",
        """    #define LIBNAME "sunvox.dll"
    #ifdef SUNVOX_MAIN
        #include <windows.h>
        typedef LPCTSTR LIBNAME_STR_TYPE;
    #else
        typedef const char* LIBNAME_STR_TYPE;
    #endif
""",
    ),
    (
        "MSVC C rejects a trailing __stdcall on static-lib declarations",
        """    #ifdef __GNUC__
\t#define SUNVOX_FN_ATTR __attribute__((stdcall))
    #else
\t#define SUNVOX_FN_ATTR __stdcall
    #endif
""",
        """    #ifdef __GNUC__
\t#define SUNVOX_FN_ATTR __attribute__((stdcall))
    #elif defined(SUNVOX_STATIC_LIB)
\t/* For static lib mode with MSVC, use empty attribute (C doesn't support trailing __stdcall) */
\t#define SUNVOX_FN_ATTR /**/
    #else
\t#define SUNVOX_FN_ATTR __stdcall
    #endif
""",
    ),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url}")
    with urllib.request.urlopen(url) as response, dest.open("wb") as out:
        shutil.copyfileobj(response, out)


def extract(archive: Path, dest: Path) -> None:
    """Extract the nested sunvox_lib/sunvox_lib/ payload to dest."""
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        prefix = "sunvox_lib/sunvox_lib/"
        members = [
            n for n in names
            if n.startswith(prefix)
            and not n.endswith("/")
            and n[len(prefix):].startswith(KEEP_DIRS)
            and not n.endswith(DROP_NAMES)
        ]
        if not members:
            raise SystemExit(f"{archive.name}: no {prefix} entries; archive layout changed")
        if dest.exists():
            shutil.rmtree(dest)
        for name in members:
            target = dest / name[len(prefix):]
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(name) as src, target.open("wb") as out:
                shutil.copyfileobj(src, out)
    print(f"extracted {len(members)} files to {dest.relative_to(ROOT)}")


def patch_header(dest: Path) -> None:
    header = dest / "headers" / "sunvox.h"
    text = header.read_text()
    for description, before, after in HEADER_PATCHES:
        if text.count(after) == 1 and before not in text:
            continue  # already applied
        if text.count(before) != 1:
            raise SystemExit(
                f"sunvox.h: cannot apply patch '{description}': "
                f"expected exactly one match, found {text.count(before)}. "
                "Upstream changed this region; update HEADER_PATCHES."
            )
        text = text.replace(before, after)
    header.write_text(text)
    print(f"patched headers/sunvox.h ({len(HEADER_PATCHES)} hunks)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=SUNVOX_URL)
    parser.add_argument("--sha256", default=SUNVOX_SHA256)
    parser.add_argument("--force", action="store_true", help="re-extract even if present")
    args = parser.parse_args()

    if STAMP.is_file() and STAMP.read_text().strip() == args.sha256 and not args.force:
        print(f"sunvox_lib {SUNVOX_VERSION} already present in {DEST.relative_to(ROOT)}")
        return 0

    archive = CACHE / Path(args.url).name
    if not archive.is_file() or sha256(archive) != args.sha256:
        download(args.url, archive)

    digest = sha256(archive)
    if digest != args.sha256:
        archive.unlink()
        raise SystemExit(
            f"checksum mismatch for {args.url}\n  expected {args.sha256}\n  got      {digest}"
        )

    extract(archive, DEST)
    patch_header(DEST)
    STAMP.write_text(digest + "\n")
    print(f"sunvox_lib {SUNVOX_VERSION} ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
