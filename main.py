from datetime import datetime, timedelta
from itertools import filterfalse
from messages import commit_messages
import os, re, traceback, random, json, subprocess, shutil

# Brief:        This file contains the main source code for git-contribot project
#
# Repository:   https://github.com/ttran-tech/git-contribot.git
# Author:       ttran.tech
# Email:        duy@ttran.tech
# Github:       https://github.com/ttran-tech
# 

# Initial setup
BASE_DIR = os.path.dirname(__file__)
LOCAL_REPO = os.path.join(BASE_DIR, 'repo')
if not os.path.isdir(LOCAL_REPO):
    os.mkdir(LOCAL_REPO, 777)
###

TARGET_FILE = None
DAYS_PER_WEEK = 7
SEC_PER_HOUR = 3600
TEST_REPO_URL = 'https://github.com/ttran-tech/git-contribot-test.git'
DUMMY_REPO_URL = 'https://github.com/ttran-tech/git-contribot-test1.git'


class FormatError(Exception):
    pass


def generate_commit_dates(start_date:str, end_date:str, min_active_days_per_week:int, max_active_days_per_week:int, start_hour:int, end_hour:int, min_commit_per_day:int, max_commit_per_day:int) -> dict[str, list[str]]:
    """Generate a commit dates dictionary and pair each entry with a list commit hours."""
    
    def _generate_active_dates(start_date:str, end_date:str, min_active_days_per_week:int, max_active_days_per_week:int) -> list[str]:
        """Generate a list of active dates"""
        DATE_REGEX_PATTERN = r'^(\d{4})-(\d{2})-(\d{2})$'
        if not bool(re.match(DATE_REGEX_PATTERN, start_date)) or not bool(re.match(DATE_REGEX_PATTERN, end_date)):
            raise FormatError('Invalid date format. Date format must match "YYYY-MM-DD". Example: 2025-01-01')
        
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

    def _generate_commit_hours(active_dates:list[datetime], start_hour:int, end_hour:int, min_commit_per_day:int, max_commit_per_day:int) -> dict[str,list[str]]:
        """Generate commit hours per date"""
        commit_dates = {}
        for active_date in active_dates:
            commit_hours = []
            commit_per_day = random.randint(min_commit_per_day, max_commit_per_day-1) # exlude the last hour
            for i in range(commit_per_day):
                hour = random.randint(start_hour, end_hour)
                minute = random.randint(1, 60)
                second = random.randint(1, 60)
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


def is_local_repo_exist(repo_name:str) -> bool:
    """Check if local repo exists"""
    return os.path.exists(os.path.join(LOCAL_REPO, repo_name))


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
    print(" [+] Cloning repository ... ", end="")
    try:
        os.chdir(LOCAL_REPO) # change current working directory to "repo", the next line clones a remote repo in "repo" folder
        subprocess.run(['git', 'clone', repo_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if is_local_repo_exist(repo_name):
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
    TARGET_FILE = os.path.join(LOCAL_REPO, f"{repo_name}/target.txt")
    with open(TARGET_FILE, 'w') as file:
        file.close()

    if not os.path.exists(TARGET_FILE):
        print("failed")
        raise FileNotFoundError
    print("ok")
    return True


def print_banner():
    pass


def main():
    if is_remote_repo_exist(TEST_REPO_URL):
        repo_name = extract_repo_name(TEST_REPO_URL)
        if not is_local_repo_exist(repo_name):
            clone_repo(TEST_REPO_URL, repo_name)
        create_target_file(repo_name)




if __name__ == '__main__':
    main()
    # commit_dates = generate_commit_dates('2023-01-01', '2023-03-01', 2, 5, 8, 17, 1, 8)
    
    # if commit_dates:
    #     commit_dates_json = json.dumps(commit_dates, indent=2)
    #     print(commit_dates_json)
    