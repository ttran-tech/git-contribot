"""
Main entry point for the git-contribot project.
 
Repository:   https://github.com/ttran-tech/git-contribot.git
Author:       ttran.tech
Email:        duy@ttran.tech
Github:       https://github.com/ttran-tech
"""
from .common import *
from .repo import *
from .core import *
from .user_input import get_user_input


def main():
    print_banner()
    user_input = get_user_input()

    repo_url = user_input['repo-url']
    repo_name = user_input['repo-name']
    print_separator()
    if is_remote_repo_exist(repo_url):
        clone_repo(repo_url, repo_name)
        commit_file = create_target_file(repo_name)
        make_commit(user_input, commit_file)

        print("\n => COMPLETED.")


if __name__ == '__main__':
    main()
    # commit_dates = generate_commit_dates('2023-01-01', '2023-03-01', 2, 5, 8, 17, 1, 8)
    
    # if commit_dates:
    #     commit_dates_json = json.dumps(commit_dates, indent=2)
    #     print(commit_dates_json)
    