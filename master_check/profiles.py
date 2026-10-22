"""
Delivery profiles. Each one says what a platform does to loudness and what
it accepts as a file. Values marked "estimated" are not published by the
platform itself; they are what engineers measure and are easy to edit here.
"""

PROFILES = [
    {
        "id": "spotify",
        "name": "Spotify",
        "target_lufs": -14.0,
        "turns_up": True,          # quiet masters are raised, but only up to -1 dBTP
        "max_true_peak": -1.0,
        "max_true_peak_loud": -2.0,  # Spotify asks for -2 dBTP above -14 LUFS
        "min_rate": 44100,
        "reject_extensible_wav": True,
        "source": "support.spotify.com/artists/article/loudness-normalization",
    },
    {
        "id": "apple",
        "name": "Apple Music",
        "target_lufs": -16.0,
        "turns_up": True,
        "max_true_peak": -1.0,
        "min_rate": 44100,
        "source": "Sound Check reference level, estimated",
    },
    {
        "id": "youtube",
        "name": "YouTube",
        "target_lufs": -14.0,
        "turns_up": False,
        "max_true_peak": -1.0,
        "min_rate": 44100,
        "source": "estimated",
    },
    {
        "id": "amazon",
        "name": "Amazon Music",
        "target_lufs": -14.0,
        "turns_up": False,
        "max_true_peak": -1.0,
        "min_rate": 44100,
        "source": "estimated",
    },
    {
        "id": "tidal",
        "name": "TIDAL",
        "target_lufs": -14.0,
        "turns_up": False,
        "max_true_peak": -1.0,
        "min_rate": 44100,
        "source": "estimated",
    },
    {
        "id": "deezer",
        "name": "Deezer",
        "target_lufs": -15.0,
        "turns_up": False,
        "max_true_peak": -1.0,
        "min_rate": 44100,
        "source": "estimated",
    },
    {
        "id": "club",
        "name": "Beatport / club",
        "target_lufs": None,        # no normalization: DJs play files as they are
        "club_range": (-10.0, -6.0),
        "max_true_peak": 0.0,
        "min_rate": 44100,
        "allowed_bits": (16, 24),
        "allowed_containers": ("WAV", "AIFF", "RF64"),
        "source": "Beatport delivery via LabelGrid; loudness range is common practice",
    },
]


def by_id(profile_id):
    for p in PROFILES:
        if p["id"] == profile_id:
            return p
    raise KeyError(profile_id)
