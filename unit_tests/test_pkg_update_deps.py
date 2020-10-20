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

    @mock.patch.object(pkg_update_deps.os.path, 'isfile')
    def test_find_package_line_in_req_file(self, _isfile):
        _isfile.return_value = True
        open_name = '%s.open' % 'pkg_update_deps'
        requirements_text = """
python3-eventlet (>= 0.18.2)
python3-pecan (>= 1.3.2)
"""
        with mock.patch(
                open_name, mock.mock_open(read_data=requirements_text)):
            pkg = pkg_update_deps.find_package_line_in_req_file(
                'test', 'python3-pecan')
        self.assertEqual(pkg, "python3-pecan (>= 1.3.2)\n")

    def test_swap_package_name_and_min_version_with_min_version(self):
        res = pkg_update_deps.swap_package_name_and_min_version(
            'pecan>=1.3.2', 'pecan', 'python3-pecan', True
        )
        self.assertEqual(res, 'python3-pecan (>= 1.3.2)')

    def test_swap_package_name_and_min_version_without_min_version(self):
        res = pkg_update_deps.swap_package_name_and_min_version(
            'pecan', 'pecan', 'python3-pecan', False
        )
        self.assertEqual(res, 'python3-pecan')

    def test_process_requirements_files_phase1(self):
        pass

    def test_process_requirements_files_phase2(self):
        pass

    def test_process_control_file_phase1(self):
        pass

    def test_process_control_file_phase2(self):
        pass
