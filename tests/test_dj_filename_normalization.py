"""File-operation regression checks, without network calls or real audio."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("dj-mp3-sourcer", "dj-set-ripper")


class FilenameNormalizationTests(unittest.TestCase):
    def run_helper(self, skill, tracks, files, apply=True, symlink=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        output = root / "audio"
        output.mkdir()
        for name in files:
            (output / name).write_bytes(name.encode())
        if symlink:
            outside = root / "outside.mp3"
            outside.write_bytes(b"outside")
            (output / symlink).symlink_to(outside)
        tracklist = root / "tracks.json"
        tracklist.write_text(json.dumps(tracks))
        command = [sys.executable, str(ROOT / "skills" / skill / "scripts" / "normalize_filenames.py"), str(output), str(tracklist)]
        if apply:
            command.append("--apply")
        result = subprocess.run(command, capture_output=True, text=True)
        return result, output

    def test_preview_preserves_files_and_apply_processes_multiple_tracks(self):
        tracks = [{"artist": "Artist", "title": "One"}, {"artist": "Artist", "title": "Two"}]
        files = ["Artist One Official.mp3", "Artist Two Video.mp3"]
        for skill in SKILLS:
            with self.subTest(skill=skill):
                result, output = self.run_helper(skill, tracks, files, apply=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(sorted(p.name for p in output.iterdir()), sorted(files))
                result, output = self.run_helper(skill, tracks, files)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual((output / "Artist - One.mp3").read_bytes(), files[0].encode())
                self.assertEqual((output / "Artist - Two.mp3").read_bytes(), files[1].encode())

    def test_metadata_cannot_escape_directory(self):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                result, output = self.run_helper(skill, [{"artist": "../Artist", "title": "../Song"}], ["Artist Song.mp3"])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(list(output.iterdir())), 1)
                self.assertEqual(next(output.iterdir()).read_bytes(), b"Artist Song.mp3")
                self.assertEqual(sorted(p.name for p in output.parent.iterdir()), ["audio", "tracks.json"])

    def test_ambiguous_files_existing_targets_and_symlinks_are_untouched(self):
        tracks = [{"artist": "Artist", "title": "Song"}]
        scenarios = [(["Artist Song A.mp3", "Artist Song B.mp3"], None),
                     (["Artist Song Video.mp3", "Artist - Song.mp3"], None),
                     ([], "Artist Song.mp3")]
        for skill in SKILLS:
            for files, symlink in scenarios:
                with self.subTest(skill=skill, files=files, symlink=symlink):
                    result, output = self.run_helper(skill, tracks, files, symlink=symlink)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(sorted(p.name for p in output.iterdir()), sorted(files + ([symlink] if symlink else [])))

    def test_only_the_matching_version_can_claim_a_source(self):
        tracks = [{"artist": "Artist", "title": "Song"}, {"artist": "Artist", "title": "Song Remix"}]
        for skill in SKILLS:
            with self.subTest(skill=skill):
                result, output = self.run_helper(skill, tracks, ["Artist Song Remix.mp3"])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(sorted(p.name for p in output.iterdir()), ["Artist - Song Remix.mp3"])
                self.assertEqual((output / "Artist - Song Remix.mp3").read_bytes(), b"Artist Song Remix.mp3")

    def test_extra_version_performer_and_unknown_words_are_preserved(self):
        variants = ["Remix", "(Guest Remix)", "Live", "(Extended Mix)", "Acoustic",
                    "Remastered", "Bootleg", "Radio Edit", "(2020)", "(feat Guest)",
                    "(from Album)", "Official Future Remix", "(Club Version)", "UploadTag"]
        for skill in SKILLS:
            for variant in variants:
                with self.subTest(skill=skill, variant=variant):
                    name = "Artist Song " + variant + ".mp3"
                    result, output = self.run_helper(skill, [{"artist": "Artist", "title": "Song"}], [name])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(sorted(p.name for p in output.iterdir()), [name])
                    self.assertEqual((output / name).read_bytes(), name.encode())

    def test_exact_remix_keeps_its_name_while_downloader_labels_are_removed(self):
        tracks = [{"artist": "Artist", "title": "Song (Guest Remix)"}]
        name = "Artist Song (Guest Remix) Official Audio Lyrics HD.mp3"
        for skill in SKILLS:
            with self.subTest(skill=skill):
                result, output = self.run_helper(skill, tracks, [name])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(sorted(p.name for p in output.iterdir()), ["Artist - Song (Guest Remix).mp3"])
                self.assertEqual((output / "Artist - Song (Guest Remix).mp3").read_bytes(), name.encode())

    def test_different_or_missing_remix_qualifier_is_not_substituted(self):
        tracks = [{"artist": "Artist", "title": "Song (Guest Remix)"}]
        for skill in SKILLS:
            for name in ["Artist Song.mp3", "Artist Song (Other Remix).mp3",
                         "Artist Song (Guest Remix VIP).mp3"]:
                with self.subTest(skill=skill, name=name):
                    result, output = self.run_helper(skill, tracks, [name])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(sorted(p.name for p in output.iterdir()), [name])

    def test_matching_original_is_selected_without_renaming_an_extra_remix(self):
        tracks = [{"artist": "Artist", "title": "Song"}]
        files = ["Artist Song Official Audio.mp3", "Artist Song Remix.mp3"]
        for skill in SKILLS:
            with self.subTest(skill=skill):
                result, output = self.run_helper(skill, tracks, files)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(sorted(p.name for p in output.iterdir()), ["Artist - Song.mp3", files[1]])
                self.assertEqual((output / "Artist - Song.mp3").read_bytes(), files[0].encode())

    def test_eligible_files_and_shared_eligible_source_remain_ambiguous(self):
        scenarios = [
            ([{"artist": "Artist", "title": "Song"}],
             ["Artist Song Official.mp3", "Artist Song Video.mp3"]),
            ([{"artist": "Artist", "title": "Song Remix"},
              {"artist": "Artist", "title": "Remix Song"}],
             ["Artist Song Remix Official.mp3"]),
        ]
        for skill in SKILLS:
            for tracks, files in scenarios:
                with self.subTest(skill=skill, tracks=tracks, files=files):
                    result, output = self.run_helper(skill, tracks, files)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(sorted(p.name for p in output.iterdir()), sorted(files))

    def test_clean_specific_version_is_not_renamed_to_another_track(self):
        tracks = [{"artist": "Artist", "title": "Song Remix"}, {"artist": "Artist", "title": "Song"}]
        for skill in SKILLS:
            result, output = self.run_helper(skill, tracks, ["Artist - Song Remix.mp3"])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "Artist - Song Remix.mp3").exists())

    def test_empty_tracklist_is_valid_and_malformed_entries_fail_before_renaming(self):
        for skill in SKILLS:
            result, output = self.run_helper(skill, [], ["Artist Song.mp3"])
            self.assertEqual(result.returncode, 0, result.stderr)
            tracks = [{"artist": "Artist", "title": "Song"}, {"artist": None, "title": "Invalid"}]
            result, output = self.run_helper(skill, tracks, ["Artist Song.mp3"])
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((output / "Artist Song.mp3").exists())


if __name__ == "__main__":
    unittest.main()
