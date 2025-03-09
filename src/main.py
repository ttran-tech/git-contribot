"""
Main entry point for the git-contribot project.
 
Repository:   https://github.com/ttran-tech/git-contribot.git
Author:       ttran.tech
Email:        duy@ttran.tech
Github:       https://github.com/ttran-tech
"""
from .common import print_banner, print_separator
from .repo import is_remote_repo_exist, clone_repo, cleanup_repo
from .core import make_commit_concurrent
from .config import get_user_config


def main():
    print_banner()
    user_config = get_user_config()

    repo_url = user_config['repo-url']
    repo_name = user_config['repo-name']
    local_repo_path = user_config['local-repo-path']
    print_separator()
    if is_remote_repo_exist(repo_url):
        clone_repo(repo_url, repo_name)
        make_commit_concurrent(user_config)
        cleanup_repo(local_repo_path)
        print("\n → Finished.")


# if __name__ == '__main__':
#     main()