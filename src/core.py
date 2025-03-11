"""
This file handles the core logic and concurrency.
"""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from itertools import filterfalse
from queue import Queue

from .common import *
from .exceptions import FormatError
from .commit_messages import commit_messages

import re
import random
import traceback
import subprocess
import threading
import concurrent.futures


git_lock = threading.Lock()

commit_completed = 0
commit_total = 0

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


def calculate_commit_total(commit_dates:Dict) -> int:
    commit_total = 0
    for _, value in commit_dates.items():
        commit_total += len(value)
    return commit_total


def make_commit(local_repo_path:str, commit_dates:Dict, commit_file:str, worker_id:int) -> None:
    """Make commit to git repo"""
    global commit_completed
    for date in commit_dates.keys():
        commit_hours = commit_dates[date]
        for hour in commit_hours:
            file_data = generate_random_string(16)
            with open(commit_file, 'w') as file:
                file.write(file_data)
                file.close()
            try:
                commit_date = f"{date} {hour}"
                commit_message = random.choice(commit_messages)
                print()
                print(f" [#] Worker {worker_id}: processing commit")
                print(f"   → Commit Date: {commit_date}")
                print(f"   → File Data: {file_data}")
                print(f"   → Commit Message: {commit_message}")

                with  git_lock: # Lock Git operations to avoid conflicts
                    subprocess.run(['git', 'add', commit_file], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True) # Git add
                    subprocess.run(['git', 'commit', '--date', commit_date, '-m', commit_message], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True) # Git commit
                    print(f"\n [#] Worker {worker_id}: finished commits.")
                    commit_completed+=1
            except subprocess.CalledProcessError:
                print(" => Failed")
                traceback.print_exc()
                return None
        with git_lock:
            # Push everything after commits are done
            print(f"\n [#] Worker {worker_id}: push to remote repository ... ", end="")
            subprocess.run(["git", "push", "origin", "main"], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print("OK")


def make_commit_concurrent(user_config:Dict, workers=5) -> None:
    """Run multiple workers to commit concurrently."""
    repo_name = user_config['repo-name']
    local_repo_path = user_config['local-repo-path']
    start_date = user_config['start-date']
    end_date = user_config['end-date']
    min_active_day_per_week = int(user_config['min-active-days'])
    max_active_day_per_week = int(user_config['max-active-days'])
    start_hour = int(user_config['start-hour'])
    end_hour = int(user_config['end-hour'])
    min_commit_per_day = int(user_config['min-commits'])
    max_commit_per_day = int(user_config['max-commits'])

    
    commit_dates = generate_commit_dates(start_date, end_date, min_active_day_per_week, max_active_day_per_week, start_hour, end_hour, min_commit_per_day, max_commit_per_day)
    commit_files = create_commit_files(repo_name, workers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(make_commit, local_repo_path, commit_dates, commit_file, worker_id) for worker_id, commit_file in commit_files.items()]
        for future in concurrent.futures.as_completed(futures):
            future.result()


# The version below is in developing and testing
def make_commit_v2(local_repo_path:str, commit_queue:Queue[Tuple[str,str]], commit_file:str, worker_id:int, push_url:str, batch_size:int=5) -> None:
    """Update remote repository"""
    global commit_completed
    commit_count = 0

    # WHILE commit_queue is NOT empty
    while not commit_queue.empty():
        # Retrieve (date, hour) from commit_queue.
        date, hour = commit_queue.get()

        # Generate random commit file content.
        file_data = generate_random_string(16)
        with open(commit_file, 'w') as file:
            file.write(file_data)
            file.close()

        try:
            commit_date = f"{date} {hour}"
            commit_message = random.choice(commit_messages)
            print()
            print(f" [#] Worker {worker_id}: Executing 'git commit'")
            print(f"   → Commit Date: {commit_date}")
            print(f"   → File Data: {file_data}")
            print(f"   → Commit Message: {commit_message}")

            with git_lock: # Lock Git operations to avoid conflicts
                subprocess.run(['git', 'add', commit_file], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True) # git add
                subprocess.run(['git', 'commit', '--date', commit_date, '-m', commit_message], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True) # git commit
                
                commit_completed+=1
                commit_count+=1
                
                print(f"\n [#] Worker {worker_id}: Commit done. Completed {commit_completed} / {commit_total} commits.")

                if commit_count == batch_size:
                    print(f"\n [#] Worker {worker_id}: Executing 'git push' ... ", end="")
                    subprocess.run(["git", "push", push_url, "main"], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True) # git push
                    commit_count = 0 # reset commit_count
                    print("OK")
        except subprocess.CalledProcessError:
            print(" => Failed")
            traceback.print_exc()
        commit_queue.task_done()
        print(f"\n [#] Worker {worker_id}: Completed all commits")
    # Finalize - push all remain commits to remote repo
    # if commit_count > 0 and commit_completed < commit_total:
    #     print(f"\n [#] Worker {worker_id}: Finalizing... ", end="")
    #     subprocess.run(["git", "push", push_url, "main"], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    #     print("OK")


def make_commit_concurrent_v2(user_config:Dict, workers=5) -> None:
    """Run multiple workers to commit concurrently"""
    global commit_total

    # Extract necessary data from user_config
    repo_name = user_config['repo-name']
    push_url = user_config['push-url']
    local_repo_path = user_config['local-repo-path']
    start_date = user_config['start-date']
    end_date = user_config['end-date']
    min_active_day_per_week = int(user_config['min-active-days'])
    max_active_day_per_week = int(user_config['max-active-days'])
    start_hour = int(user_config['start-hour'])
    end_hour = int(user_config['end-hour'])
    min_commit_per_day = int(user_config['min-commits'])
    max_commit_per_day = int(user_config['max-commits'])

    # Generate commit_dates dictionary using generate_commit_dates()
    commit_dates = generate_commit_dates(start_date, end_date, min_active_day_per_week, max_active_day_per_week, start_hour, end_hour, min_commit_per_day, max_commit_per_day)
    
    # Create a Queue object to store individual commit tasks
    commit_queue = Queue()
    
    # Populate the Queue
    for date in commit_dates:
        for hour in commit_dates[date]:
            commit_queue.put((date, hour))
    commit_total = commit_queue.qsize()

    # Create commit_files mapping (one per worker)
    commit_files = create_commit_files(repo_name, workers)

    # Start ThreadPoolExecutor with 'workers' number of workers:
    #     - Submit make_commit(worker_id) for each worker.
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(make_commit_v2, local_repo_path, commit_queue, commit_file, worker_id, push_url) for worker_id, commit_file in commit_files.items()]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    # Let the main thread handle the last push
    if commit_completed < commit_total:
        print(f"\n [#] Main Thread: Finalizing... ", end="")
        subprocess.run(["git", "push", push_url, "main"], cwd=local_repo_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("OK")