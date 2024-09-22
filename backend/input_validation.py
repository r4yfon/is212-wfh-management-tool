from datetime import datetime
from dateutil.relativedelta import relativedelta

def string_length_valid(input_string, min_length=0, max_length=None):
    """
    Validates if the input string length is within the specified range.

    Parameters:
        input_string (str): The input string to be validated.
        min_length (int): The minimum length of the input string. Defaults to 0.
        max_length (int): The maximum length of the input string. Defaults to None.

    Returns:
        bool: True if the input string length is within the specified range, False otherwise.
    """
    input_string_len = len(input_string)
    if max_length is None:
        max_length = input_string_len
    if min_length <= input_string_len <= max_length:
        return True
    else:
        return False

def has_existing_request(employee_requests, employee_id, request_date):
    """
    Checks if the employee already has an existing request for the given date.

    Parameters:
        employee_requests (list): A list of dictionaries containing employee requests.
        employee_id (int): The ID of the employee member.
        request_date (str): The date of the request in 'YYYY-MM-DD' format.

    Returns:
        bool: True if there is an existing request for the given date, False otherwise.
    """
    for request in employee_requests:
        if request['employee_id'] == employee_id and request['request_date'] == request_date:
            return True
    return False

def check_date_valid(request_start_date, request_end_date):
    """
    Checks if the request start date is within 2 months before the current date 
    and if the request end date is within 3 months after the current date.

    Args:
        request_start_date (str): The start date of the request in 'YYYY-MM-DD' format.
        request_end_date (str): The end date of the request in 'YYYY-MM-DD' format.

    Returns:
        bool: True if the input dates fulfill the check criteria, False otherwise.
    """
    current_date = datetime.now().date()  # Correct usage to get the current date
    two_months_before = current_date - relativedelta(months=2)
    three_months_after = current_date + relativedelta(months=3)

    # Convert input strings to date objects
    request_start_date = datetime.strptime(request_start_date, "%Y-%m-%d").date()
    request_end_date = datetime.strptime(request_end_date, "%Y-%m-%d").date()

    # Check if start date is within 2 months before and end date within 3 months after
    if (two_months_before <= request_start_date <= three_months_after) and (two_months_before <= request_end_date <= three_months_after):
        return True
    else:
        return False