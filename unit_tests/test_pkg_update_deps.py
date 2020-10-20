import mock
import unittest

import pkg_update_deps


class UpdateDepsTests(unittest.TestCase):
    def test_get_ubuntu_package_name(self):
        self.assertEqual(
            pkg_update_deps.get_ubuntu_package_name('cryptography'),
            'python3-cryptography')

    def test_non_existent_package_name(self):
        self.assertEqual(
            pkg_update_deps.get_ubuntu_package_name('something-random'),
            'ENOTFOUND')

    @mock.patch.object(pkg_update_deps.subprocess, 'run')
    def test_rmadison(self, _run):
        m = mock.MagicMock()
        m.stdout.decode.return_value = 'this is a test'
        _run.return_value = m
        open_name = '%s.open' % 'pkg_update_deps'
        mock_open = mock.mock_open()
        with mock.patch(open_name, mock_open, create=True):
            # mock_open.return_value = mock.MagicMock(spec=file)
            pkg_update_deps.rmadison(['test'])
        _run.assert_called_once_with(
            ['rmadison', 'test'],
            check=True, stdout=pkg_update_deps.subprocess.PIPE)
        mock_open.assert_called()
        handle = mock_open()
        handle.write.assert_called_once_with('this is a test')
