"""
This file handles repo validation and operations.
"""
from .common import *

import os
import re
import subprocess
import traceback


def is_remote_repo_exist(repo_url:str) -> bool:
    """Check if remote repo exists"""
    print(f" [+] Checking remote repository: {repo_url} ... ", end="")
    try:
        subprocess.run(['git', 'ls-remote', repo_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True) # subprocess.DEVNUL same as 2>/dev/null
        print("ok")
        return True
    except subprocess.CalledProcessError:
        print("failed")
        return False


def is_local_repo_exist(repo_name:str) -> bool:
    """Check if local repo exists"""
    return os.path.exists(os.path.join(REPO_DIR, repo_name))


def extract_repo_name(repo_url:str) -> str:
    """Extract the repo name from repo URL"""
    #print(" [+] Extracting repository name ... ", end="")
    try:
        repo_name = re.search(r'/[\w-]+\.git$', repo_url).group(0)
        repo_name = repo_name.replace('/', '').split('.')[0]
        #print("ok")
        #print(f"   => Repository Name: {repo_name}")
        return repo_name
    except AttributeError:
        #print("failed")
        traceback.print_exc()
        return None


def clone_repo(repo_url:str, repo_name:str) -> bool:
    """Clone a repo to from the remote repo"""
    if not is_local_repo_exist(repo_name):
        print(" [+] Cloning repository ... ", end="")
        try:
            os.chdir(REPO_DIR) # change current working directory to "repo", the next line clones a remote repo in "repo" folder
            subprocess.run(['git', 'clone', repo_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if is_local_repo_exist(repo_name):
                print("ok")
                return True 
        except AttributeError:
            print("failed")
            traceback.print_exc()
            return False
