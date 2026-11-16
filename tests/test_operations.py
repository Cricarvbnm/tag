import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tag.cmd import fix, mv, rm
from tag.output import list_paths


class OperationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'res').mkdir()
        (self.root / 'tag').mkdir()
        (self.root / 'sub').mkdir()
        self.resource = self.root / 'res/song'
        self.resource.touch()
        self.link = self.root / 'tag/song'
        self.link.symlink_to('../res/song')

    def test_move_and_remove_from_subdirectory(self):
        with contextlib.chdir(self.root / 'sub'), contextlib.redirect_stdout(io.StringIO()):
            mv.run(['../res/song', '../res/new'], self.root)
            self.assertEqual(self.link.resolve(), self.root / 'res/new')
            with patch('tag.cmd.rm.confirm', return_value=True):
                rm.run(['../res/new'], self.root)
        self.assertFalse(self.link.is_symlink())
        self.assertTrue((self.root / 'res/new').exists())

    def test_fix_removes_broken_link_only_after_confirmation(self):
        self.resource.unlink()
        with patch('tag.cmd.fix.list_paths', return_value=0), patch('tag.cmd.fix.confirm', return_value=False):
            fix.run([], self.root)
        self.assertTrue(self.link.is_symlink())
        with patch('tag.cmd.fix.list_paths', return_value=0), patch('tag.cmd.fix.confirm', return_value=True):
            fix.run([], self.root)
        self.assertFalse(self.link.is_symlink())

    def test_custom_lister_gets_root_relative_paths(self):
        with patch.dict(os.environ, {'TAG_LISTER': 'custom --plain'}), patch('tag.output.subprocess.run') as run:
            run.return_value.returncode = 0
            list_paths([self.resource], self.root)
        run.assert_called_once_with(['custom', '--plain', '-d', 'res/song'], cwd=self.root)
