"""Text, JSON and HTML reports."""
import html
import json
import os
import time

from . import APP_NAME, __version__

LABEL = {"fail": "FAIL", "warn": "WARN", "ok": "OK", "info": "info"}


def _num(v, fmt):
    return "n/a" if v is None else fmt % v


def measurement_rows(m):
    return [
        ("Integrated loudness", _num(m["integrated_lufs"], "%.1f LUFS")),
        ("Short-term max", _num(m["short_term_max_lufs"], "%.1f LUFS")),
        ("Momentary max", _num(m["momentary_max_lufs"], "%.1f LUFS")),
        ("Loudness range (LRA)", _num(m["lra_lu"], "%.1f LU")),
        ("True peak", _num(m["true_peak_dbtp"], "%+.1f dBTP")),
        ("Sample peak", _num(m["sample_peak_dbfs"], "%+.1f dBFS")),
        ("Peak to loudness (PLR)", _num(m["plr_db"], "%.1f dB")),
        ("L/R correlation", _num(m["correlation"], "%.2f")),
        ("DC offset", _num(m["dc_offset_dbfs"], "%.0f dBFS")),
    ]


def text(results):
    lines = []
    for r in results:
        if "error" in r:
            lines += ["== %s" % os.path.basename(r["file"]), "  FAIL  %s" % r["error"], ""]
            continue
        lines.append("== %s  [%s]" % (os.path.basename(r["file"]), LABEL[r["status"]]))
        lines.append("   " + r["format"]["description"])
        for name, value in measurement_rows(r["measurements"]):
            lines.append("   %-24s %s" % (name, value))
        lines.append("")
        for f in r["general"]:
            lines.append("  %-5s %s" % (LABEL[f["level"]], f["message"]))
        lines.append("")
        lines.append("   %-17s %8s %10s  %s" % ("Platform", "Gain", "Playback", "Status"))
        for p in r["platforms"]:
            lines.append("   %-17s %+7.1f dB %6.1f LUFS  %s" % (
                p["name"], p["gain_db"], p["playback_lufs"], LABEL[p["status"]]))
            for f in p["findings"]:
                if f["level"] != "info":
                    lines.append("      %-5s %s" % (LABEL[f["level"]], f["message"]))
        lines.append("")
    return "\n".join(lines)


def to_json(results):
    return json.dumps({"app": APP_NAME, "version": __version__, "results": results}, indent=2)


CSS = """
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:900px;
margin:24px auto;padding:0 16px;color:#1d1d1f;background:#fff}
h1{font-size:22px}h2{font-size:18px;margin-top:32px}
table{border-collapse:collapse;width:100%;margin:8px 0}
td,th{border-bottom:1px solid #ddd;padding:6px 8px;text-align:left;font-size:14px}
.fail{color:#b00020;font-weight:600}.warn{color:#a15c00;font-weight:600}
.ok{color:#1b7f3b;font-weight:600}.info{color:#555}
small{color:#666}
"""


def to_html(results):
    e = html.escape
    out = ["<!doctype html><meta charset=utf-8><title>%s report</title><style>%s</style>"
           % (APP_NAME, CSS),
           "<h1>%s report</h1><small>%s %s, %s</small>"
           % (APP_NAME, APP_NAME, __version__, time.strftime("%Y-%m-%d %H:%M"))]
    for r in results:
        name = e(os.path.basename(r["file"]))
        if "error" in r:
            out.append("<h2>%s <span class=fail>FAIL</span></h2><p>%s</p>" % (name, e(r["error"])))
            continue
        out.append("<h2>%s <span class=%s>%s</span></h2><p>%s</p>" % (
            name, r["status"], LABEL[r["status"]], e(r["format"]["description"])))
        out.append("<table>" + "".join("<tr><td>%s</td><td>%s</td></tr>" % (e(k), e(v))
                                       for k, v in measurement_rows(r["measurements"]))
                   + "</table>")
        out.append("<ul>" + "".join("<li><span class=%s>%s</span> %s</li>" % (
            f["level"], LABEL[f["level"]], e(f["message"])) for f in r["general"]) + "</ul>")
        out.append("<table><tr><th>Platform</th><th>Gain on playback</th><th>Plays at</th>"
                   "<th>Status</th><th>Notes</th></tr>")
        for p in r["platforms"]:
            notes = "<br>".join(e(f["message"]) for f in p["findings"])
            out.append("<tr><td>%s</td><td>%+.1f dB</td><td>%.1f LUFS</td>"
                       "<td class=%s>%s</td><td>%s</td></tr>" % (
                           e(p["name"]), p["gain_db"], p["playback_lufs"], p["status"],
                           LABEL[p["status"]], notes))
        out.append("</table>")
    out.append("<p><small>Loudness per ITU-R BS.1770-5, LRA per EBU Tech 3342. Platform "
               "values marked estimated in the source are not published by the platform.</small>")
    return "\n".join(out)
