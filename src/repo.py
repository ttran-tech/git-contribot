"""
This file handles repo validation and operations.
"""
from .common import *

import os
import re
import subprocess
import traceback
import shutil


def is_remote_repo_exist(repo_url:str) -> bool:
    """Check if remote repo exists"""
    print(f"\n [+] Checking remote repository: {repo_url} ... ", end="")
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


def cleanup_repo(local_repo_path:str) -> bool:
    """Clean up local and remote repository, remove all dummy files"""
    print(f"\n [+] Cleaning up local and remote repository ... ", end="")
    try:
        subprocess.run(['git', 'rm', '*'], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(['git', 'commit', '-m', 'Chore: clean up repository'], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(['git', 'push'], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("ok")
        print("\n → Local repository cleanup completed.")
        print("\n ⚠ Note: The directory still exists. Delete it manually if necessary.")
        print(f"\n → Local repository path: {local_repo_path}")
        return True
        # if _force_delete_local_repo(local_repo_path):
        #     return True
    except subprocess.CalledProcessError:
        print("failed")
    return False
    

def _force_delete_local_repo(local_repo_path:str) -> bool:
    """Force delete the local repository and its contents"""
    print(" [+] Deleting local repository ... ", end="")
    try:
        shutil.rmtree(local_repo_path)
        if not os.path.exists(local_repo_path):
            print("ok")
            return True
    except FileNotFoundError:
        print(f"Directory '{local_repo_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return False