"""
Main entry point for the git-contribot project.
 
Repository:   https://github.com/ttran-tech/git-contribot.git
Author:       ttran.tech
Email:        duy@ttran.tech
Github:       https://github.com/ttran-tech
"""
from .common import print_banner, print_separator
from .repo import is_remote_repo_exist, clone_repo
from .core import make_commit_concurrent
from .user_input import get_user_input


def main():
    print_banner()
    user_input = get_user_input()

    repo_url = user_input['repo-url']
    repo_name = user_input['repo-name']
    print_separator()
    if is_remote_repo_exist(repo_url):
        clone_repo(repo_url, repo_name)
        make_commit_concurrent(user_input)
        print("\n => Finished.")


# if __name__ == '__main__':
#     main()