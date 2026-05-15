"""Command-line interface for the sample indexer.

Usage:
    python -m indexer index --packs <path> --manifest <path>
    python -m indexer stats --manifest <path>
    python -m indexer search --manifest <path> --type kick --genre trap --bpm 90
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from indexer.manifest import build_manifest, search_samples, library_stats


def _cmd_index(args) -> int:
    def progress(done: int, total: int) -> None:
        print(f"  ... {done}/{total}", file=sys.stderr)

    stats = build_manifest(args.packs, args.manifest, on_progress=progress)
    print(json.dumps(stats, indent=2))
    return 0


def _cmd_stats(args) -> int:
    stats = library_stats(args.manifest)
    print(json.dumps(stats, indent=2))
    return 0


def _cmd_search(args) -> int:
    results = search_samples(
        args.manifest,
        sample_type=args.type,
        subtype=args.subtype,
        genre=args.genre,
        mood=args.mood,
        key=args.key,
        bpm=args.bpm,
        bpm_tolerance=args.bpm_tolerance,
        is_loop=args.loops_only or None,
        is_oneshot=args.oneshots_only or None,
        limit=args.limit,
    )
    for row in results:
        print(row["path"])
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m indexer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index", help="Walk packs root and build/update manifest")
    p_index.add_argument("--packs", type=Path, required=True)
    p_index.add_argument("--manifest", type=Path, required=True)
    p_index.set_defaults(func=_cmd_index)

    p_stats = sub.add_parser("stats", help="Print library statistics")
    p_stats.add_argument("--manifest", type=Path, required=True)
    p_stats.set_defaults(func=_cmd_stats)

    p_search = sub.add_parser("search", help="Search the manifest")
    p_search.add_argument("--manifest", type=Path, required=True)
    p_search.add_argument("--type", help="Sample type (kick, snare, hat_closed, ...)")
    p_search.add_argument("--subtype", help="808, sub, growl, ...")
    p_search.add_argument("--genre", help="trap, boom_bap, phonk, ...")
    p_search.add_argument("--mood", help="punchy, vintage, dark, ...")
    p_search.add_argument("--key", help="e.g. F#min, Cmaj")
    p_search.add_argument("--bpm", type=int)
    p_search.add_argument("--bpm-tolerance", type=int, default=5)
    p_search.add_argument("--loops-only", action="store_true")
    p_search.add_argument("--oneshots-only", action="store_true")
    p_search.add_argument("--limit", type=int, default=20)
    p_search.set_defaults(func=_cmd_search)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
