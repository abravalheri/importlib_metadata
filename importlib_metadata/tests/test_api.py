import re
import unittest
import importlib_metadata

try:
    from collections.abc import Iterator
except ImportError:
    from collections import Iterator  # noqa: F401

try:
    from builtins import str as text
except ImportError:
    from __builtin__ import unicode as text


class APITests(unittest.TestCase):
    version_pattern = r'\d+\.\d+(\.\d)?'

    def test_retrieves_version_of_self(self):
        version = importlib_metadata.version('importlib_metadata')
        assert isinstance(version, text)
        assert re.match(self.version_pattern, version)

    def test_retrieves_version_of_pip(self):
        # Assume pip is installed and retrieve the version of pip.
        version = importlib_metadata.version('pip')
        assert isinstance(version, text)
        assert re.match(self.version_pattern, version)

    def test_for_name_does_not_exist(self):
        with self.assertRaises(importlib_metadata.PackageNotFoundError):
            importlib_metadata.distribution('does-not-exist')

    def test_for_top_level(self):
        distribution = importlib_metadata.distribution('importlib_metadata')
        self.assertEqual(
            distribution.read_text('top_level.txt').strip(),
            'importlib_metadata')

    def test_entry_points(self):
        parser = importlib_metadata.entry_points('pip')
        # We should probably not be dependent on a third party package's
        # internal API staying stable.
        entry_point = parser.get('console_scripts', 'pip')
        self.assertEqual(entry_point, 'pip._internal:main')

    def test_metadata_for_this_package(self):
        md = importlib_metadata.metadata('importlib_metadata')
        assert md['author'] == 'Barry Warsaw'
        assert md['LICENSE'] == 'Apache Software License'
        assert md['Name'] == 'importlib-metadata'
        classifiers = md.get_all('Classifier')
        assert 'Topic :: Software Development :: Libraries' in classifiers

    def test_importlib_metadata_version(self):
        assert re.match(self.version_pattern, importlib_metadata.__version__)

    @staticmethod
    def _test_files(files_iter):
        assert isinstance(files_iter, Iterator)
        files = list(files_iter)
        root = files[0].root
        for file in files:
            assert file.root == root
            assert not file.hash or file.hash.value
            assert not file.hash or file.hash.mode == 'sha256'
            assert not file.size or file.size >= 0
            assert file.locate().exists()
            assert isinstance(file.read_binary(), bytes)
            if file.name.endswith('.py'):
                file.read_text()

    def test_files_dist_info(self):
        self._test_files(importlib_metadata.files('pip'))

    def test_files_egg_info(self):
        self._test_files(importlib_metadata.files('importlib_metadata'))
