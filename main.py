from datetime import datetime, timedelta
from itertools import filterfalse
from typing import Dict, List
from messages import commit_messages
import os, re, traceback, random, json, subprocess, secrets, string

# Brief:        This file contains the main source code for git-contribot project
#
# Repository:   https://github.com/ttran-tech/git-contribot.git
# Author:       ttran.tech
# Email:        duy@ttran.tech
# Github:       https://github.com/ttran-tech
# 

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


class FormatError(Exception):
    pass


def generate_commit_dates(start_date:str, end_date:str, min_active_days_per_week:int, max_active_days_per_week:int, start_hour:int, end_hour:int, min_commit_per_day:int, max_commit_per_day:int) -> Dict[str, List[str]]:
    """Generate a commit dates dictionary and pair each entry with a list commit hours."""
    
    def _generate_active_dates(start_date:str, end_date:str, min_active_days_per_week:int, max_active_days_per_week:int) -> List[str]:
        """Generate a list of active dates"""
        DATE_REGEX_PATTERN = r'^(\d{4})-(\d{2})-(\d{2})$'
        if not bool(re.match(DATE_REGEX_PATTERN, start_date)) or not bool(re.match(DATE_REGEX_PATTERN, end_date)):
            raise FormatError('Invalid date format. Date format must match "YYYY-MM-DD". Example: 2025-01-01')
        
        if start_date == end_date:
            raise FormatError('Invalid date range: The start date and end date cannot be the same')

        DATE_FORMAT = '%Y-%m-%d'
        start_date = datetime.strptime(f"{start_date}", DATE_FORMAT)
        end_date = datetime.strptime(f"{end_date}", DATE_FORMAT)
        week_total = ((end_date - start_date).days) // DAYS_PER_WEEK  # get the number of weeks between the start and end date

        # active_date = []
        active_dates = set()
        next_start_date = start_date
        for i in range(week_total):
            active_date_per_week = random.randint(min_active_days_per_week, max_active_days_per_week)
            next_end_date = next_start_date + timedelta(days=DAYS_PER_WEEK)
            dates = [(next_start_date + timedelta(days=n)) for n in range((next_end_date - next_start_date).days + 1)]
            for j in range(active_date_per_week):
                # Use filterfalse to eliminate the elements already in active_dates, 
                # and create a list of available dates
                available_dates = list(filterfalse(active_dates.__contains__, dates))
                if available_dates:
                    date = random.choice(available_dates).strftime(DATE_FORMAT)
                    active_dates.add(date)
            next_start_date = next_end_date
        active_dates = sorted(active_dates)
        return active_dates

    def _generate_commit_hours(active_dates:List[datetime], start_hour:int, end_hour:int, min_commit_per_day:int, max_commit_per_day:int) -> Dict[str,List[str]]:
        """Generate commit hours per date"""
        commit_dates = {}
        for active_date in active_dates:
            commit_hours = []
            commit_per_day = random.randint(min_commit_per_day, max_commit_per_day-1) # exlude the last hour
            for i in range(commit_per_day):
                hour = random.randint(start_hour, end_hour)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                commit_hours.append(f"{hour:02d}:{minute:02d}:{second:02d}")
            commit_hours.sort()
            commit_dates[active_date] = commit_hours
        return commit_dates
    
    try:
        active_dates = _generate_active_dates(start_date, end_date, min_active_days_per_week, max_active_days_per_week)
        commit_dates = _generate_commit_hours(active_dates, start_hour, end_hour, min_commit_per_day, max_commit_per_day)
        return commit_dates
    except FormatError as e:
        traceback.print_exc()
        return None


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


def is_REPO_DIR_exist(repo_name:str) -> bool:
    """Check if local repo exists"""
    return os.path.exists(os.path.join(REPO_DIR, repo_name))


def extract_repo_name(repo_url:str) -> str:
    """Extract the repo name from repo URL"""
    print(" [+] Extracting repository name ... ", end="")
    try:
        repo_name = re.search(r'/[\w-]+\.git$', repo_url).group(0)
        repo_name = repo_name.replace('/', '').split('.')[0]
        print("ok")
        print(f"   => Repository Name: {repo_name}")
        return repo_name
    except AttributeError:
        print("failed")
        traceback.print_exc()
        return None


def clone_repo(repo_url:str, repo_name:str) -> bool:
    """Clone a repo to from the remote repo"""
    if not is_REPO_DIR_exist(repo_name):
        print(" [+] Cloning repository ... ", end="")
        try:
            os.chdir(REPO_DIR) # change current working directory to "repo", the next line clones a remote repo in "repo" folder
            subprocess.run(['git', 'clone', repo_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if is_REPO_DIR_exist(repo_name):
                print("ok")
                return True 
        except AttributeError:
            print("failed")
            traceback.print_exc()
            return False


def create_target_file(repo_name:str) -> bool:
    """Create a target file inside the local repo"""
    global TARGET_FILE
    print(" [+] Creating target file ... ", end="")
    TARGET_FILE = os.path.join(REPO_DIR, f"{repo_name}/target.txt")
    if not os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, 'w') as file:
            file.close()
        if os.path.exists(TARGET_FILE):
            print("ok")
            return True
        print("failed")
        raise FileNotFoundError


def generate_random_string(size:int) -> str:
    """Return a random string"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(size))


def make_commit(repo_name:str) -> None:
    start_date = '2017-01-01'
    end_date = '2017-05-31'
    min_active_day_per_week = 4
    max_active_day_per_week = 7
    start_hour = 8
    end_hour = 17
    min_commit_per_day = 2
    max_commit_per_day = 8

    commit_dates = generate_commit_dates(start_date, end_date, min_active_day_per_week, max_active_day_per_week, start_hour, end_hour, min_commit_per_day, max_commit_per_day)

    local_repo_path = os.path.join(REPO_DIR, repo_name)
    for date in commit_dates.keys():
        commit_hours = commit_dates[date]
        for hour in commit_hours:
            file_data = generate_random_string(32)
            with open(TARGET_FILE, 'w') as target_file:
                target_file.write(file_data)
                target_file.close()
            try:
                commit_date = f"{date} {hour}"
                commit_message = random.choice(commit_messages)
                print()
                print(" [+] Processing commit:")
                print(f"   - Commit Date: {commit_date}")
                print(f"   - File Data: {file_data}")
                print(f"   - Commit Message: {commit_message}")

                # Git add
                subprocess.run(['git', 'add', TARGET_FILE], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

                # Git commit
                subprocess.run(['git', 'commit', '--date', commit_date, '-m', commit_message], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            except subprocess.CalledProcessError:
                print(" => Failed")
                traceback.print_exc()
                return None
        # Batch commit - only push after the hours already commited to reduce execution time
        print(" [+] Push to remote repo ... ", end="")
        subprocess.run(['git', 'push'], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("OK")


def make_commit_concurrency():
    pass


def print_banner():
    pass


def user_input() -> Dict[str, str]:
    pass


def main():
    if is_remote_repo_exist(TEST_REPO_URL):
        repo_name = extract_repo_name(TEST_REPO_URL)
        clone_repo(TEST_REPO_URL, repo_name)
        create_target_file(repo_name)
        make_commit(repo_name)

        print("\n => COMPLETED.")


if __name__ == '__main__':
    main()
    # commit_dates = generate_commit_dates('2023-01-01', '2023-03-01', 2, 5, 8, 17, 1, 8)
    
    # if commit_dates:
    #     commit_dates_json = json.dumps(commit_dates, indent=2)
    #     print(commit_dates_json)
    