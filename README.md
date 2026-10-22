# Master Check

**Release QC for finished masters.** Drop in a master (or a folder of them) and see,
before you upload it:

- **Loudness**: integrated LUFS, short-term and momentary max, loudness range (LRA),
  true peak, sample peak and peak-to-loudness ratio.
- **What each platform does to it**: how many dB Spotify, Apple Music, YouTube, Amazon
  Music, TIDAL and Deezer will turn it down (or up), and how it sits next to other club
  masters for Beatport and DJ sets.
- **Delivery problems that get a release rejected or ruined**: wrong sample rate,
  WAV files with the EXTENSIBLE header (Spotify rejects them), clipping, overs in float
  files, DC offset, flipped polarity, mono files, long silences, 16-bit audio padded
  into a 24-bit file.

Then save the result as an HTML report for your label or client, or as JSON.

Free and open source (MIT), made by [ROMMUSER](https://rommuser.com). Part of a set of
tools for producers and engineers with [Mix Ready](https://github.com/axelfj/mix-ready),
[Ref Match](https://github.com/axelfj/ref-match) and
[Stem Organizer](https://github.com/axelfj/stem-organizer).

## Download

Get the latest version from the [Releases page](https://github.com/axelfj/master-check/releases/latest):

| System | File |
|---|---|
| Windows 10/11 (64-bit) | `MasterCheck-Setup.exe` (installer) |
| macOS 12+ on Apple silicon | `MasterCheck.dmg` (drag *Master Check* to Applications) |

The apps are not code-signed yet, so the first launch shows a warning once:

- **Windows**: SmartScreen says "Windows protected your PC". Click *More info*, then *Run anyway*.
- **macOS**: open the app once, then go to *System Settings > Privacy & Security* and
  click *Open Anyway*.

## Using it

Click **Check files...** or **Check a folder...**. Each file gets a block like this:

```
== My Track (Original Mix).wav  [WARN]
   WAV, 44100 Hz, 24-bit int, 2 ch, 372.1 s
   Integrated loudness      -7.9 LUFS
   Short-term max           -6.1 LUFS
   Loudness range (LRA)     4.2 LU
   True peak                +0.4 dBTP
   ...
   Platform              Gain   Playback  Status
   Spotify              -6.1 dB  -14.0 LUFS  WARN
      WARN  True peak +0.4 dBTP is above -2.0 dBTP; it may distort after lossy encoding.
   Beatport / club      +0.0 dB   -7.9 LUFS  WARN
```

- **FAIL**: fix before releasing (clipping, rejected format, too low sample rate).
- **WARN**: worth a look (true peak too hot for streaming, loudness outside the club range).
- **OK**: nothing found.

### Command line

```
python app.py "My Track.wav" --html report.html --json report.json
python app.py masters/ --platforms spotify,club
```

Exit code is 1 when any file has a FAIL, so it works in scripts.

## What it measures, and how

| Number | Method |
|---|---|
| Integrated / momentary / short-term loudness | ITU-R BS.1770-5: K-weighting, 400 ms blocks with 75 % overlap, -70 LUFS absolute and -10 LU relative gates |
| Loudness range | EBU Tech 3342: 3 s windows, -20 LU relative gate, 10th to 95th percentile |
| True peak | 4x oversampling (2x at 88.2/96 kHz) |
| Platform gain | Target minus integrated loudness. Platforms that raise quiet tracks only do it up to their true-peak ceiling |

The meter is tested against the EBU reference signals (a 1 kHz tone at -23 dBFS reads
-23.0 LUFS at 44.1, 48 and 96 kHz).

### Platform profiles

| Profile | Target | True-peak advice | Source |
|---|---|---|---|
| Spotify | -14 LUFS | -1 dBTP, -2 dBTP if louder than -14 LUFS | [Spotify](https://support.spotify.com/artists/article/loudness-normalization/) |
| Apple Music | -16 LUFS | -1 dBTP | estimated (Sound Check) |
| YouTube | -14 LUFS, only turns down | -1 dBTP | estimated |
| Amazon Music | -14 LUFS, only turns down | -1 dBTP | estimated |
| TIDAL | -14 LUFS, only turns down | -1 dBTP | estimated |
| Deezer | -15 LUFS, only turns down | -1 dBTP | estimated |
| Beatport / club | no normalization; -10 to -6 LUFS is the usual range | under 0 dBTP, 16 or 24-bit WAV/AIFF | [LabelGrid](https://help.labelgrid.com/en/distribution/beatport-requirements/) |

"Estimated" means the platform does not publish the number; it is what engineers
measure. All values live in [`master_check/profiles.py`](master_check/profiles.py)
and are easy to change.

## Run from source

```
pip install -r requirements.txt
python app.py
```

Tests: `python -m unittest discover -s tests -v`. See [CONTRIBUTING.md](CONTRIBUTING.md)
for development and releases, and [CHANGELOG.md](CHANGELOG.md) for what changed.

## En español

**Master Check** revisa tu master antes de lanzarlo: LUFS integrados, true peak y LRA,
cuánto le va a bajar o subir el volumen cada plataforma (Spotify, Apple Music,
YouTube...) y los problemas de entrega que hacen que rechacen un lanzamiento, como el
encabezado WAV EXTENSIBLE, clipping o una frecuencia de muestreo baja. Descargá el
instalador de Windows o el .dmg de Mac en
[Releases](https://github.com/axelfj/master-check/releases/latest).

¿Necesitás mezcla o master? [ROMMUSER Studio](https://rommuser.com/estudio).

## License

MIT. See [LICENSE](LICENSE).
