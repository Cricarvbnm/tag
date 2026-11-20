import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest


class ListerPathsTest(unittest.TestCase):
    def test_orphans_paths_are_relative_to_invocation_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "res").mkdir()
            (root / "tag" / "nested").mkdir(parents=True)
            (root / "res" / "a file").touch()
            lister = root / "custom lister.py"
            lister.write_text(
                "import json, os, sys\n"
                "print(json.dumps([os.getcwd(), sys.argv[1:]]))\n"
            )
            env = dict(os.environ, TAG_ROOT=str(root))
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
            for directory, expected in (
                (root, "res/a file"),
                (root / "tag", "../res/a file"),
                (root / "tag" / "nested", "../../res/a file"),
            ):
                for custom in (False, True):
                    with self.subTest(directory=directory, custom=custom):
                        env["TAG_LISTER"] = (
                            shlex.join([sys.executable, str(lister)]) if custom else ""
                        )
                        result = subprocess.run(
                            [sys.executable, "-m", "tag.cmd.orphans"],
                            cwd=directory, env=env, capture_output=True, text=True,
                        )
                        self.assertEqual(result.returncode, 0, result.stderr)
                        if custom:
                            self.assertEqual(
                                json.loads(result.stdout),
                                [str(directory), ["-d", "--", expected]],
                            )
                        else:
                            self.assertEqual(result.stdout, expected + "\n")


if __name__ == "__main__":
    unittest.main()
