"""Measures one master and checks it against every delivery profile."""
import math

from . import audio, loudness, stats
from .profiles import PROFILES

FAIL, WARN, OK, INFO = "fail", "warn", "ok", "info"
SEVERITY = {FAIL: 3, WARN: 2, INFO: 1, OK: 0}


def finding(level, message):
    return {"level": level, "message": message}


def worst(findings):
    levels = [f["level"] for f in findings] or [OK]
    top = max(levels, key=SEVERITY.get)
    return OK if top == INFO else top


def measure_file(path):
    a = audio.read(path)
    x = a.samples
    m = loudness.measure(x, a.rate)
    head, tail = stats.edge_silence(x, a.rate)
    m.update({
        "clip_runs": stats.clip_runs(x),
        "overs": stats.overs(x),
        "dc_offset_dbfs": stats.dc_offset_db(x),
        "correlation": stats.correlation(x[:, 0], x[:, 1]) if a.channels == 2 else None,
        "dual_mono": stats.is_dual_mono(x),
        "head_silence_s": head,
        "tail_silence_s": tail,
        "effective_bits": stats.effective_bits(x, a.bits, a.is_float),
    })
    fmt = {
        "container": a.container,
        "encoding": a.encoding,
        "format_tag": a.format_tag,
        "rate": a.rate,
        "bits": a.bits,
        "float": a.is_float,
        "channels": a.channels,
        "duration_s": a.duration,
        "description": a.describe(),
    }
    return fmt, m


def general_findings(fmt, m):
    out = []
    if fmt["duration_s"] < 1.0:
        out.append(finding(FAIL, "Shorter than 1 second; stores reject it."))
    if m["clip_runs"]:
        out.append(finding(FAIL, "Clipped in %d places (3+ samples in a row at full scale)."
                           % m["clip_runs"]))
    if m["overs"]:
        out.append(finding(WARN, "%d samples above 0 dBFS. They clip as soon as this float "
                                 "file is converted to 16 or 24-bit." % m["overs"]))
    if m["dc_offset_dbfs"] > -40.0:
        out.append(finding(WARN, "DC offset of %.1f dBFS. Use a high-pass or DC filter."
                           % m["dc_offset_dbfs"]))
    if fmt["channels"] == 1:
        out.append(finding(WARN, "Mono file. Stores expect stereo masters."))
    elif fmt["channels"] > 2:
        out.append(finding(WARN, "%d channels. Stores expect stereo masters." % fmt["channels"]))
    if m["dual_mono"]:
        out.append(finding(INFO, "Left and right are identical (mono in a stereo file)."))
    elif m["correlation"] is not None and m["correlation"] < 0.0:
        out.append(finding(WARN, "L/R correlation is %.2f. Part of the track cancels in mono; "
                                 "check for a flipped polarity." % m["correlation"]))
    if m["head_silence_s"] > 1.0:
        out.append(finding(WARN, "%.1f s of silence at the start." % m["head_silence_s"]))
    if m["tail_silence_s"] > 5.0:
        out.append(finding(WARN, "%.1f s of silence at the end." % m["tail_silence_s"]))
    if not fmt["float"] and 0 < m["effective_bits"] < fmt["bits"]:
        out.append(finding(WARN, "Declared %d-bit but the audio is really %d-bit."
                           % (fmt["bits"], m["effective_bits"])))
    if not out:
        out.append(finding(OK, "No clipping, DC offset, phase or format problems."))
    return out


def platform_gain(profile, m):
    """dB the platform applies on playback (negative = turned down)."""
    i = m["integrated_lufs"]
    if profile.get("target_lufs") is None or i == loudness.NEG_INF:
        return 0.0
    gain = profile["target_lufs"] - i
    if gain > 0:
        if not profile.get("turns_up"):
            return 0.0
        headroom = profile["max_true_peak"] - m["true_peak_dbtp"]
        gain = max(0.0, min(gain, headroom))
    return gain


def check_profile(profile, fmt, m):
    out = []
    i, tp = m["integrated_lufs"], m["true_peak_dbtp"]
    if fmt["rate"] < profile.get("min_rate", 0):
        out.append(finding(FAIL, "Sample rate %d Hz; needs at least %d Hz."
                           % (fmt["rate"], profile["min_rate"])))
    if profile.get("reject_extensible_wav") and fmt["format_tag"] == audio.WAV_EXTENSIBLE:
        out.append(finding(FAIL, "WAV uses the EXTENSIBLE header (format code 0xFFFE), which "
                                 "%s rejects. Re-export as plain PCM WAV or FLAC."
                           % profile["name"]))
    if "allowed_containers" in profile and fmt["container"] not in profile["allowed_containers"]:
        out.append(finding(FAIL, "%s file; deliver WAV or AIFF." % fmt["container"]))
    if "allowed_bits" in profile and (fmt["float"] or fmt["bits"] not in profile["allowed_bits"]):
        out.append(finding(WARN, "%d-bit%s; deliver 16 or 24-bit." %
                           (fmt["bits"], " float" if fmt["float"] else "")))

    limit = profile["max_true_peak"]
    loud_limit = profile.get("max_true_peak_loud")
    if loud_limit is not None and i > profile["target_lufs"]:
        limit = loud_limit
    if tp > limit:
        out.append(finding(WARN, "True peak %+.1f dBTP is above %+.1f dBTP; it may distort "
                                 "after lossy encoding." % (tp, limit)))

    gain = platform_gain(profile, m)
    if profile.get("target_lufs") is not None:
        if gain < -0.05:
            out.append(finding(INFO, "Turned down %.1f dB on playback." % -gain))
        elif gain > 0.05:
            out.append(finding(INFO, "Turned up %.1f dB on playback." % gain))
        else:
            out.append(finding(INFO, "Played back at its own level."))
        wanted = profile["target_lufs"] - i
        if wanted > 0.5 and gain < wanted - 0.5:
            out.append(finding(WARN, "Plays %.1f dB quieter than other tracks." % (wanted - gain)))
    else:
        lo, hi = profile["club_range"]
        if i < lo:
            out.append(finding(WARN, "%.1f LUFS is quieter than typical club masters (%.0f to "
                                     "%.0f LUFS); DJs will have to gain it up." % (i, lo, hi)))
        elif i > hi:
            out.append(finding(WARN, "%.1f LUFS is louder than typical club masters (%.0f to "
                                     "%.0f LUFS); expect audible limiting." % (i, lo, hi)))
        else:
            out.append(finding(INFO, "%.1f LUFS sits in the usual club range." % i))
    return {
        "id": profile["id"],
        "name": profile["name"],
        "gain_db": gain,
        "playback_lufs": i + gain if i != loudness.NEG_INF else i,
        "status": worst(out),
        "findings": out,
    }


def analyze(path, profile_ids=None):
    fmt, m = measure_file(path)
    profiles = [p for p in PROFILES if profile_ids is None or p["id"] in profile_ids]
    general = general_findings(fmt, m)
    platforms = [check_profile(p, fmt, m) for p in profiles]
    status = worst(general + [finding(p["status"], "") for p in platforms])
    return {"file": path, "format": fmt, "measurements": _clean(m), "general": general,
            "platforms": platforms, "status": status}


def _clean(m):
    """JSON has no -inf; silence reads as null."""
    return {k: (None if isinstance(v, float) and math.isinf(v) else v) for k, v in m.items()}
