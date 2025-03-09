"""
This file handles user inputs and validation.
"""
from datetime import datetime
from typing import Dict
from .common import print_separator
import re

DEFAULT_VALUES = {
    'repo-url': '',
    'start-date': '',
    'end-date': '',
    'min-active-days': '2',
    'max-active-days': '6',
    'start-hour': '8',
    'end-hour': '17',
    'min-commits': '5',
    'max-commits': '20',
}

def get_valid_input(prompt:str, validation_fn, error_message:str, default_value=None) -> str:
    """Generic function to get valid input from the user."""
    while True:
        user_input = input(prompt).strip()
        if user_input == '':
            if default_value:
                user_input = default_value
        if validation_fn(user_input):
            return user_input
        print(f"\n [x] {error_message}")


# Validation functions
def is_valid_date(date_str:str) -> bool:
    """Check if the date follows YYYY-MM-DD format and is a valid date."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_int(value, min_val=None, max_val=None) -> bool:
    """Check if the input is a valid integer within an optional range."""
    if not value.isdigit():
        return False
    value = int(value)
    if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
        return False
    return True


def is_valid_repo_url(url) -> bool:
    """Check if the given URL follows a valid GitHub repo format."""
    git_url_pattern = re.compile(r"^(https:\/\/github\.com\/[\w.-]+\/[\w.-]+\.git)$")
    return bool(git_url_pattern.match(url))


def get_prompt_set(user_input=None) -> Dict[str, str]:
    prompt_set = {}
    if user_input is None:
        prompt_set = {
            'repo-url': "\n → Enter your GitHub repository URL (e.g., https://github.com/user/repo.git)\n > ",
            'start-date': "\n → Enter the starting date (YYYY-MM-DD)\n > ",
            'end-date': "\n → Enter the last date to make a commit (YYYY-MM-DD)\n > ",
            'min-active-days': f"\n → Enter the minimum active days per week (1-7) [Default: {DEFAULT_VALUES['min-active-days']}, press Enter]\n > ",
            'max-active-days': f"\n → Enter the maximum active days per week (1-7) [Default: {DEFAULT_VALUES['max-active-days']}, press Enter]\n > ",
            'start-hour': f"\n → Enter the starting hour for commits per day (0-23) [Default: {DEFAULT_VALUES['start-hour']}, press Enter]\n > ",
            'end-hour': f"\n → Enter the ending hour for commits per day (0-23) [Default: {DEFAULT_VALUES['end-hour']}, press Enter]\n > ",
            'min-commits': f"\n → Enter the minimum number of commits per day [Default: {DEFAULT_VALUES['min-commits']}, press Enter]\n > ",
            'max-commits': f"\n → Enter the maximum number of commits per day [Default: {DEFAULT_VALUES['max-commits']}, press Enter]\n > ",
        }
    else:
        prompt_set = {
            'repo-url': f"\n → Enter your GitHub repository URL [Repository URL: {user_input['repo-url']}, Enter to skip]\n > ",
            'start-date': f"\n → Enter the starting date (YYYY-MM-DD) [Starting date: {user_input['start-date']}, Enter to skip]\n > ",
            'end-date': f"\n → Enter the last date to make a commit (YYYY-MM-DD) [Ending date: {user_input['end-date']}, Enter to skip]\n > ",
            'min-active-days': f"\n → Enter the minimum active days per week (1-7) [Min. active days: {user_input['min-active-days']}, Enter to skip]\n > ",
            'max-active-days': f"\n → Enter the maximum active days per week (1-7) [Max. active days: {user_input['max-active-days']}, Enter to skip]\n > ",
            'start-hour': f"\n → Enter the starting hour for commits per day (0-23) [Start hour: {user_input['start-hour']}, Enter to skip]\n > ",
            'end-hour': f"\n → Enter the ending hour for commits per day (0-23) [End hour: {user_input['end-hour']}, Enter to skip]\n > ",
            'min-commits': f"\n → Enter the minimum number of commits per day [Min. commits: {user_input['min-commits']}, Enter to skip]\n > ",
            'max-commits': f"\n → Enter the maximum number of commits per day [Max. commits: {user_input['max-commits']}, Enter to skip]\n > ",
        }
    return prompt_set


def get_user_input() -> Dict:
    user_input = None
    prompt_set = get_prompt_set(user_input)
    local_default_value = DEFAULT_VALUES
    while True:
        repo_url = get_valid_input(prompt_set['repo-url'],
                                is_valid_repo_url, "Invalid GitHub repository URL! Format: https://github.com/user/repo.git", local_default_value['repo-url'])

        start_date = get_valid_input(prompt_set['start-date'], 
                                    is_valid_date, "Invalid date format! Please use YYYY-MM-DD.", local_default_value['start-date'])

        end_date = get_valid_input(prompt_set['end-date'], 
                                is_valid_date, "Invalid date format! Please use YYYY-MM-DD.", local_default_value['end-date'])

        min_active_days = get_valid_input(prompt_set['min-active-days'], 
                                        lambda x: is_valid_int(x, 1, 7), "Invalid number! Must be between 1 and 7.", local_default_value['min-active-days'])

        max_active_days = get_valid_input(prompt_set['max-active-days'], 
                                        lambda x: is_valid_int(x, 1, 7), "Invalid number! Must be between 1 and 7.", local_default_value['max-active-days'])

        start_hour = get_valid_input(prompt_set['start-hour'], 
                                    lambda x: is_valid_int(x, 0, 23), "Invalid hour! Must be between 0 and 23.", local_default_value['start-hour'])

        end_hour = get_valid_input(prompt_set['end-hour'], 
                                lambda x: is_valid_int(x, 0, 23), "Invalid hour! Must be between 0 and 23.", local_default_value['end-hour'])

        min_commits = get_valid_input(prompt_set['min-commits'], 
                                    lambda x: is_valid_int(x, 1), "Invalid number! Must be a positive integer.", local_default_value['min-commits'])

        max_commits = get_valid_input(prompt_set['max-commits'], 
                                    lambda x: is_valid_int(x, 1), "Invalid number! Must be a positive integer.", local_default_value['max-commits'])
        user_input = {
            'repo-url': repo_url,
            'repo-name': '',
            'start-date': start_date,
            'end-date': end_date,
            'min-active-days': min_active_days,
            'max-active-days': max_active_days,
            'start-hour': start_hour,
            'end-hour': end_hour,
            'min-commits': min_commits,
            'max-commits': max_commits
        }

        # Confirmation
        confirm = input("\n → Proceed with these settings? (Y/N): ").strip().lower()
        if confirm == 'y':
            return user_input
        else:
            prompt_set = get_prompt_set(user_input)
            local_default_value = user_input
            print_separator()