import re # regular expressions library will help us check format.

# -INDIVIDUAL VALIDATION CHECKS -

def is_valid_id(id_str):
    "Checks ID: Must be exactly 6 digits."
    # ^ means start of string, $ means end of string
    # r means raw string, so no escape characters needed
    if not re.fullmatch(r'^\d{6}$', id_str):
        return False, "ID must be exactly 6 digits."
    return True, None


def is_valid_email(email_str):
    "Checks Email: Must be in XXXXXXXX@ksu.edu.sa format."
    pattern = r'^[A-Za-z0-9._%-]+@ksu\.edu\.sa$'
    if not re.fullmatch(pattern, email_str):
        return False, "Email must be in the format XXXXXXXX@ksu.edu.sa"
    return True, None


def is_valid_phone(phone_str):
    """
    Checks Phone: Must be in 05XXXXXXXX format (10 digits).
    Fix: Uses re.sub to remove all non-digit characters first.
    """
    # 1. Aggressively clean the string: Remove ALL non-digit characters
    # (This line was missing in your file!)
    cleaned_phone = re.sub(r'\D', '', phone_str)

    # 2. Check the format on the CLEANED string
    # (Added 'r' before the quotes to fix the SyntaxWarning)
    if not re.fullmatch(r'^05\d{8}$', cleaned_phone):
        return False, "Phone number must be exactly 10 digits, starting with 05."

    return True, None

def is_valid_password(password_str):
    # Checks Password: Must be at least 6 characters/digits.

    if len(password_str) < 6:
        return False, "Password must be at least 6 characters/digits."
    return True, None


# - COMPREHENSIVE VALIDATION -

def validate_signup_inputs(data):
    """
    Runs all format validation checks for the Sign Up window.

    Args:
        data (dict): Dictionary containing all sign-up fields.

    Returns:
        dict: A dictionary of errors, where keys are the field names.
    """
    errors = {}

    # Check ID
    valid, msg = is_valid_id(data.get('id', ''))
    if not valid: errors['id'] = msg

    # Check Email
    valid, msg = is_valid_email(data.get('email', ''))
    if not valid: errors['email'] = msg

    # Check Phone
    valid, msg = is_valid_phone(data.get('phone_number', ''))
    if not valid: errors['phone_number'] = msg

    # Check Password
    valid, msg = is_valid_password(data.get('password', ''))
    if not valid: errors['password'] = msg

    # Check User Class selection
    if data.get('user_class') not in ['College', 'Courier', 'Inventory Manager']:
        errors['user_class'] = "A valid User Class must be selected."

    return errors