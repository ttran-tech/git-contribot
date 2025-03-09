from typing import Dict, List
from datetime import datetime, timedelta
from itertools import filterfalse

from common import *
from exceptions import FormatError
from commit_messages import commit_messages

import os
import re
import random
import traceback
import subprocess


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


def make_commit(repo_name:str) -> None:
    """Make commit to git repo"""
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
            file_data = generate_random_string(16)
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