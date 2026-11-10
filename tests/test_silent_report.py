import json
import os
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from master_check import audio, analysis, report, cli

class SilentReports(unittest.TestCase):
    def test_silence_and_below_gate_export_all_formats(self):
        with tempfile.TemporaryDirectory() as folder:
            results = []
            for level in (0, 1e-8, .1):
                path = os.path.join(folder, str(level) + '.wav')
                x = level * np.sin(2*np.pi*1000*np.arange(44100)/44100)
                audio.write_wav_float(path, np.column_stack((x,x)), 44100)
                results.append(analysis.analyze(path))
            for r in results[:2]:
                self.assertTrue(all(p['playback_lufs'] is None for p in r['platforms']))
            json.loads(report.to_json(results), parse_constant=lambda x: self.fail(x))
            self.assertIn('n/a', report.text(results))
            self.assertIn('n/a', report.to_html(results))

    def test_failed_replace_preserves_previous_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'report.json')
            with open(path, 'w') as f: f.write('previous')
            with patch('master_check.report.os.replace', side_effect=OSError('disk failure')):
                with self.assertRaises(OSError): report.save(path, 'new')
            with open(path) as f: self.assertEqual(f.read(), 'previous')
            self.assertEqual(os.listdir(folder), ['report.json'])

    def test_failed_serialization_preserves_previous_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'report.json')
            with open(path, 'w') as f: f.write('previous')
            with patch.object(cli, 'run', return_value=[]), patch.object(report, 'to_json', side_effect=ValueError('bad data')):
                with self.assertRaises(ValueError): cli.main(['fake.wav', '--json', path])
            with open(path) as f: self.assertEqual(f.read(), 'previous')
