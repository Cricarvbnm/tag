from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest

from tag.output import print_tree


class TreeFormatTest(unittest.TestCase):
    def test_custom_formats_and_default_spacing(self):
        root = Path("/library")
        output = StringIO()
        with redirect_stdout(output):
            print_tree(
                [root / "group" / "a{b}", root / "plain"], root,
                formats={
                    root / "group": "+ {name}",
                    root / "group" / "a{b}": " [{name}] -> target{{literal}}",
                },
            )
        self.assertEqual(output.getvalue(), (
            "├──+ group\n"
            "│   └── [a{b}] -> target{literal}\n"
            "└── plain\n"
        ))


if __name__ == "__main__":
    unittest.main()
