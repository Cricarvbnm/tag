import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tag.library import find_root, find_resource_links, relative, find_resources
from tag.output import print_tree


class CliTests(unittest.TestCase):
    def test_output_uses_library_root_from_subdirectory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "res").mkdir()
            (base / "tag").mkdir()
            child = base / "sub"
            child.mkdir()
            with patch.dict(os.environ, {"TAG_ROOT": str(base)}), patch("pathlib.Path.cwd", return_value=child):
                self.assertEqual(relative(base / "res/song", base), "res/song")

    def test_root_walk_and_explicit_invalid_root(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "res").mkdir()
            (base / "tag").mkdir()
            child = base / "sub"
            child.mkdir()
            with patch.dict(os.environ, {}, clear=True), patch("pathlib.Path.cwd", return_value=child):
                self.assertEqual(find_root(), base)
            with patch.dict(os.environ, {"TAG_ROOT": str(child)}), patch("pathlib.Path.cwd", return_value=base):
                with self.assertRaises(FileNotFoundError):
                    find_root()

    def test_symlink_scan_and_sorted_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "res").mkdir()
            (base / "tag" / "music").mkdir(parents=True)
            resource = base / "res" / "song"
            resource.touch()
            (base / "tag/music/song").symlink_to("../../res/song")
            with patch("pathlib.Path.cwd", return_value=base):
                self.assertEqual(find_resources(base / "tag"), [resource])
                self.assertEqual(len(find_resource_links(resource, base)), 1)
            with patch("builtins.print") as output:
                print_tree([base / "tag/z", base / "tag/a/deep"], base)
            self.assertEqual(output.call_args_list[1].args[0], "    ├── a")


if __name__ == "__main__":
    unittest.main()
