import re

def validate_string(input_string):
    return [
        bool(re.search(r'[a-zA-Z0-9_]', input_string)), 
        bool(re.search(r'[a-zA-Z]', input_string)), 
        bool (re.search(r'[A-Z]', input_string)), 
        bool(re.search(r'[a-z]', input_string)), 
        bool(re.search(r'[0-9]', input_string)), 
        len(input_string) >= 8
        ]

print(validate_string("xYz8")) # [True, False, False, False, True, True]
    