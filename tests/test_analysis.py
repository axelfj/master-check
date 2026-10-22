import os
import tempfile
import unittest

import numpy as np

from master_check import audio, report
from master_check.analysis import analyze, platform_gain
from master_check.cli import main as cli_main
from master_check.profiles import by_id


def track(rate=44100, seconds=12, dbfs=-8.0, seed=0):
    """Band-limited noise with a slow envelope: loud enough to look like a master."""
    rng = np.random.default_rng(seed)
    n = int(rate * seconds)
    x = rng.normal(0, 1, (n, 2))
    x[:, 1] = 0.7 * x[:, 0] + 0.3 * x[:, 1]
    x /= np.max(np.abs(x))
    return x * 10 ** (dbfs / 20)


def levels(findings):
    return [f["level"] for f in findings]


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def write(self, name, x, rate=44100, bits=24, **kw):
        p = os.path.join(self.dir, name)
        audio.write_wav_pcm(p, x, rate, bits, **kw)
        return p

    def platform(self, result, pid):
        return next(p for p in result["platforms"] if p["id"] == pid)

    def test_clean_master_passes(self):
        r = analyze(self.write("clean.wav", track(dbfs=-3)))
        self.assertEqual(levels(r["general"]), ["ok"])
        self.assertNotEqual(r["status"], "fail")
        spotify = self.platform(r, "spotify")
        self.assertLess(spotify["gain_db"], 0)
        self.assertAlmostEqual(spotify["playback_lufs"], -14.0, places=5)

    def test_extensible_wav_fails_spotify_only(self):
        r = analyze(self.write("ext.wav", track(dbfs=-3), extensible=True))
        self.assertEqual(self.platform(r, "spotify")["status"], "fail")
        self.assertNotEqual(self.platform(r, "apple")["status"], "fail")

    def test_clipping_and_hot_true_peak(self):
        x = track(dbfs=0)
        x[1000:1010] = 1.0
        r = analyze(self.write("clip.wav", x))
        self.assertIn("fail", levels(r["general"]))
        self.assertEqual(r["status"], "fail")
        self.assertEqual(self.platform(r, "spotify")["status"], "warn")

    def test_low_sample_rate_fails(self):
        r = analyze(self.write("lo.wav", track(rate=32000, dbfs=-3), rate=32000))
        self.assertTrue(all(p["status"] == "fail" for p in r["platforms"]))

    def test_padded_16_bit_is_flagged(self):
        x = np.round(track(dbfs=-3) * 32768) / 32768
        r = analyze(self.write("pad.wav", x, bits=24))
        self.assertTrue(any("really 16-bit" in f["message"] for f in r["general"]))

    def test_float_master_warns_for_club(self):
        p = os.path.join(self.dir, "f.wav")
        audio.write_wav_float(p, track(dbfs=-3), 44100)
        club = self.platform(analyze(p), "club")
        self.assertEqual(club["status"], "warn")

    def test_quiet_master_gain(self):
        m = {"integrated_lufs": -20.0, "true_peak_dbtp": -4.0}
        self.assertAlmostEqual(platform_gain(by_id("spotify"), m), 3.0)   # capped at -1 dBTP
        self.assertAlmostEqual(platform_gain(by_id("youtube"), m), 0.0)   # never turns up
        self.assertAlmostEqual(platform_gain(by_id("apple"), m), 3.0)

    def test_reports_and_cli(self):
        good = self.write("good.wav", track(dbfs=-3))
        bad = os.path.join(self.dir, "broken.wav")
        with open(bad, "wb") as f:
            f.write(b"RIFF\x00\x00\x00\x00WAVE")
        out_json = os.path.join(self.dir, "r.json")
        out_html = os.path.join(self.dir, "r.html")
        code = cli_main([self.dir, "--json", out_json, "--html", out_html])
        self.assertEqual(code, 1)  # the broken file fails
        with open(out_html, encoding="utf-8") as f:
            page = f.read()
        self.assertIn("good.wav", page)
        self.assertIn("broken.wav", page)
        self.assertIn("Spotify", report.text([analyze(good)]))


if __name__ == "__main__":
    unittest.main()
