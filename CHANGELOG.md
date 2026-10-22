# Changelog

All notable changes to Master Check are listed here. Versions follow
[Semantic Versioning](https://semver.org).

## [0.1.0] - 2026-10-22

First release.

- Integrated, short-term max and momentary max loudness (ITU-R BS.1770-5), loudness
  range (EBU Tech 3342), true peak (4x oversampled), sample peak and PLR.
- Playback gain and status for Spotify, Apple Music, YouTube, Amazon Music, TIDAL,
  Deezer and a Beatport / club profile.
- Delivery checks: sample rate, bit depth, WAV EXTENSIBLE header (rejected by Spotify),
  clipping, float overs, DC offset, phase, mono, silence at the edges, 16-bit audio
  padded to 24-bit.
- Reads WAV (including RF64 and 32-bit float), AIFF, FLAC, MP3 and OGG.
- Window app plus command line, with HTML and JSON reports.
- Windows installer and macOS (Apple silicon) disk image.
