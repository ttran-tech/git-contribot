"""
This file handles all unit test purposes.
"""
import unittest
from src.common import *
from src.main import *
from src.repo import *

class TestGitContribot(unittest.TestCase):
    def test_is_repo_exist(self):
        self.assertEqual(is_remote_repo_exist(TEST_REPO_URL), True, "Result mismatch") # Test for pass result
        self.assertEqual(is_remote_repo_exist(DUMMY_REPO_URL), False, "Result mismatch") # Test for fail result

    def test_repo_name(self):
        self.assertIsNotNone(extract_repo_name(TEST_REPO_URL))


if __name__ == '__main__':
    unittest.main(verbosity=2)