import unittest
from main import *

# Brief:        This file contains the unit tests for git-contribot project.
#
# Repository:   https://github.com/ttran-tech/git-contribot.git
# Author:       ttran.tech
# Email:        duy@ttran.tech
# Github:       https://github.com/ttran-tech
# 

class TestGitContribot(unittest.TestCase):
    def test_is_repo_exist(self):
        self.assertEqual(is_repo_exist(TEST_REPO_URL), True, "Result mismatch") # Test for pass result
        self.assertEqual(is_repo_exist(DUMMY_REPO_URL), False, "Result mismatch") # Test for fail result

if __name__ == '__main__':
    unittest.main(verbosity=2)