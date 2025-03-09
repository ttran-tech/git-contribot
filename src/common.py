"""
This file contains common constants and functions used in other modules.
"""
import os
import string
import secrets

VERSION = "0.1.0"

# Initial setup
BASE_DIR = os.path.dirname(__file__)
REPO_DIR = os.path.join(BASE_DIR, 'repo')
if not os.path.isdir(REPO_DIR):
    os.mkdir(REPO_DIR, 777)
###
WORKERS = 5 # for concurrent
TARGET_FILE = None
DAYS_PER_WEEK = 7
SEC_PER_HOUR = 3600
TEST_REPO_URL = 'https://github.com/ttran-tech/git-contribot-test.git'
DUMMY_REPO_URL = 'https://github.com/ttran-tech/git-contribot-test1.git'


def generate_random_string(size:int) -> str:
    """Return a random string"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(size))


def create_target_file(repo_name:str) -> str:
    """Create a target file inside the local repo"""
    print(" [+] Creating target file ... ", end="")
    target_file = os.path.join(REPO_DIR, f"{repo_name}/target.txt")
    with open(target_file, 'w') as file:
        file.close()
    if os.path.exists(target_file):
        print("ok")
        return target_file
    print("failed")
    raise FileNotFoundError
    

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