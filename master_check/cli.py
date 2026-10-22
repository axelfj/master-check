"""Command line: master-check FILE_OR_FOLDER... [--json out.json] [--html out.html]"""
import argparse
import os
import sys

from . import APP_NAME, __version__, audio, report
from .analysis import analyze
from .profiles import PROFILES


def collect(paths):
    files = []
    for p in paths:
        files += audio.list_audio_files(p) if os.path.isdir(p) else [p]
    return files


def run(files, profile_ids=None, progress=None):
    results = []
    for n, path in enumerate(files):
        if progress:
            progress(n, len(files), path)
        try:
            results.append(analyze(path, profile_ids))
        except (audio.AudioError, OSError, ValueError) as e:
            results.append({"file": path, "error": str(e), "status": "fail"})
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(prog="master-check", description="%s %s: release QC for "
                                 "finished masters." % (APP_NAME, __version__))
    ap.add_argument("paths", nargs="+", help="audio files or folders")
    ap.add_argument("--platforms", help="comma-separated subset of: "
                    + ",".join(p["id"] for p in PROFILES))
    ap.add_argument("--json", metavar="FILE", help="also write a JSON report")
    ap.add_argument("--html", metavar="FILE", help="also write an HTML report")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)

    ids = args.platforms.split(",") if args.platforms else None
    files = collect(args.paths)
    if not files:
        print("No audio files found.", file=sys.stderr)
        return 2
    results = run(files, ids)
    print(report.text(results))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(report.to_json(results))
    if args.html:
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(report.to_html(results))
    return 1 if any(r["status"] == "fail" for r in results) else 0
