import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class AddOutputTest(unittest.TestCase):
    def test_reports_existing_and_created_directories_and_link_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "res").mkdir()
            (root / "res" / "a file").touch()
            (root / "tag" / "existing").mkdir(parents=True)
            (root / "tag" / "unrelated").mkdir()
            env = dict(os.environ, TAG_ROOT=str(root))
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
            result = subprocess.run(
                [sys.executable, "-m", "tag.cmd.add", "../res/a file",
                 "new/child", "../tag/existing", "new/other"],
                cwd=root / "tag", env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, (
                "└── tag\n"
                "    ├── existing\n"
                "    │   └── a file -> ../../res/a file\n"
                "    └──+ new\n"
                "        ├──+ child\n"
                "        │   └── a file -> ../../../res/a file\n"
                "        └──+ other\n"
                "            └── a file -> ../../../res/a file\n"
            ))
            for tag in ("existing", "new/child", "new/other"):
                link = root / "tag" / tag / "a file"
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), root / "res" / "a file")

            repeated = subprocess.run(
                [sys.executable, "-m", "tag.cmd.add", "../res/a file", "existing"],
                cwd=root / "tag", env=env, capture_output=True, text=True,
            )
            self.assertEqual(repeated.returncode, 1)
            self.assertEqual(repeated.stdout, "")
            self.assertIn("File exists", repeated.stderr)
            self.assertEqual(
                (root / "tag" / "existing" / "a file").resolve(),
                root / "res" / "a file",
            )


if __name__ == "__main__":
    unittest.main()
