"""
This file contains common constants and functions used in other modules.
"""
from typing import Dict
import os
import string
import secrets
import platform
import sys

VERSION = "1.0.0"


# Initial setup
USER_OS = platform.system()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
REPO_DIR = os.path.join(BASE_DIR, 'repo')
if not os.path.isdir(REPO_DIR):
    os.makedirs(REPO_DIR, mode=0o777)
    if USER_OS == 'Linux':
        os.system(f"chmod 777 {REPO_DIR}")
###
DAYS_PER_WEEK = 7
SEC_PER_HOUR = 3600


def generate_random_string(size:int) -> str:
    """Return a random string"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(size))


def create_commit_files(repo_name:str, workers:int) -> Dict[int, str]:
    """Create a target file inside the local repo"""
    print(" [+] Creating target file ... ", end="")
    commit_files = {}
    for i in range(1, workers+1):
        filename = generate_random_string(16)
        commit_file = os.path.join(REPO_DIR, f"{repo_name}/{filename}.txt")
        with open(commit_file, 'w') as file:
            file.close()
        if os.path.exists(commit_file):
            commit_files[i] = commit_file
    print("ok")
    return commit_files


def extract_username(repo_url:str) -> str:
    """Extract username from repo URL"""
    return ((repo_url.replace("https://github.com/", "")).split("/")[0]).strip()


def create_push_url(repo_url:str, pat:str) -> str:
    """Build git push url for Linux user"""
    return repo_url.replace("https://", f"https://{extract_username(repo_url)}:{pat}@")


def print_banner():
    print()
    print("┌─────────────────────────────────────────────────────────────────────────────────┐")
    print("│                                                                                 │")
    print("│                      _ __                  __      _ __        __               │")
    print("│                ___ _(_) /_  _______  ___  / /_____(_) /  ___  / /_              │")
    print("│               / _ `/ / __/ / __/ _ \\/ _ \\/ __/ __/ / _ \\/ _ \\/ __/              │")
    print("│               \\_, /_/\\__/  \\__/\\___/_//_/\\__/_/ /_/_.__/\\___/\\__/               │")
    print("│              /___/                                                              │")
    print(f"│                                        Developed by ttran.tech | v{VERSION}         │")
    print("└─────────────────────────────────────────────────────────────────────────────────┘")
    print()


def print_separator():
    print()
    print("───────────────────────────────────────────────────────────────────────────────────")
    print()


def supported_os() -> bool:
    if USER_OS == "Windows":
        return True
    print(" ⚠ This tools currently supports Windows only.")
    print()
    sys.exit(1)