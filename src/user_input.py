"""
This file handles user inputs and validation.
"""
from datetime import datetime
import re


def get_valid_input(prompt, validation_fn, error_message):
    """Generic function to get valid input from the user."""
    while True:
        user_input = input(prompt).strip()
        if validation_fn(user_input):
            return user_input
        print(f" [x] {error_message}\n")


# Validation functions
def is_valid_date(date_str):
    """Check if the date follows YYYY-MM-DD format and is a valid date."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_int(value, min_val=None, max_val=None):
    """Check if the input is a valid integer within an optional range."""
    if not value.isdigit():
        return False
    value = int(value)
    if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
        return False
    return True


def is_valid_repo_url(url):
    """Check if the given URL follows a valid GitHub repo format."""
    git_url_pattern = re.compile(r"^(https:\/\/github\.com\/[\w.-]+\/[\w.-]+\.git)$")
    return bool(git_url_pattern.match(url))

# Collect user input with validation
repo_url = get_valid_input(" => Enter your GitHub repository URL (e.g., https://github.com/user/repo.git): ",
                           is_valid_repo_url, "Invalid GitHub repository URL! Format: https://github.com/user/repo.git")

start_date = get_valid_input(" => Enter the starting date (YYYY-MM-DD): ", 
                             is_valid_date, "Invalid date format! Please use YYYY-MM-DD.")

end_date = get_valid_input(" => Enter the last date to make a commit (YYYY-MM-DD): ", 
                           is_valid_date, "Invalid date format! Please use YYYY-MM-DD.")

min_active_days = get_valid_input(" => Enter the minimum active days per week (1-7): ", 
                                  lambda x: is_valid_int(x, 1, 7), "Invalid number! Must be between 1 and 7.")

max_active_days = get_valid_input(" => Enter the maximum active days per week (1-7): ", 
                                  lambda x: is_valid_int(x, 1, 7), "Invalid number! Must be between 1 and 7.")

start_hour = get_valid_input(" => Enter the starting hour for commits per day (0-23): ", 
                             lambda x: is_valid_int(x, 0, 23), "Invalid hour! Must be between 0 and 23.")

end_hour = get_valid_input(" => Enter the ending hour for commits per day (0-23): ", 
                           lambda x: is_valid_int(x, 0, 23), "Invalid hour! Must be between 0 and 23.")

min_commits = get_valid_input(" => Enter the minimum number of commits per day: ", 
                              lambda x: is_valid_int(x, 1), "Invalid number! Must be a positive integer.")

max_commits = get_valid_input(" => Enter the maximum number of commits per day: ", 
                              lambda x: is_valid_int(x, 1), "Invalid number! Must be a positive integer.")