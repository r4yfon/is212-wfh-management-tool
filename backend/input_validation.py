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