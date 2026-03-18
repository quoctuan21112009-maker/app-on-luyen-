import requests
import json
import datetime
from typing import Optional, Dict, Any

# --- Configuration ---

# The API endpoint URL
API_URL = "https://api-elb.onluyen.vn/api/school-online/assignment/assign-student-suggest?pageIndex=1&pageSize=15"

# Map numerical status codes to human-readable strings
STATUS_MAP = {
    0: "waiting",
    1: "doing",
    2: "grading",
    3: "done"
}

# The base set of headers required for the request (excluding dynamic or unnecessary fields)
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
    "Content-Type": "application/json",
    "authority": "api-elb.onluyen.vn",
    "method": "GET",
    "path": "/api/school-online/assignment/assign-student-suggest?pageIndex=1&pageSize=15",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "vi,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,nl;q=0.6",
    "cache-control": "no-cache",
    "code-app": "SCHOOL",
    "origin": "https://app.onluyen.vn",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://app.onluyen.vn/",
    #"school-id": "1716",
    #"school-year": "2025",
    "sec-ch-ua": "\"Chromium\";v=\"142\", \"Microsoft Edge\";v=\"142\", \"Not_A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    # Removed "user-id" and "user-name" as requested.
}

def _print_assignment_summary(data: Dict[str, Any]):
    """Prints a human-readable summary of the assignments from the API response."""
    assignments = data.get('data', [])
    total_count = data.get('totalCount', 0)
    current_count = data.get('currentCount', 0)
    page_index = data.get('pageIndex', 1)
    
    print("\n" + "="*50)
    print("         HUMAN-READABLE ASSIGNMENT SUMMARY")
    print("="*50)
    print(f"Total Records Found: {total_count}")
    print(f"Records on Current Page: {current_count}")
    print(f"Page Index: {page_index}")
    print("-" * 50)
    
    if not assignments:
        print("No assignments found on this page.")
        return

    for i, assignment in enumerate(assignments):
        # Retrieve and format timeCreate timestamp
        time_create = assignment.get('timeCreate')
        try:
            # Convert Unix timestamp (seconds) to readable format
            timestamp = datetime.datetime.fromtimestamp(time_create)
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except (TypeError, ValueError):
            time_str = "N/A"

        # status is already converted to string (unconditionally)
        status_str = assignment.get('status', 'N/A')

        print(f"[{i+1:02d}] Assignment: {assignment.get('name', 'N/A')}")
        print(f"      Class: {assignment.get('className', 'N/A')}")
        print(f"      Status: {status_str.upper()}")
        print(f"      Created On: {time_str}")
        print("-" * 50)


def fetch_assignments(raw_token: str, debug: bool = False) -> Optional[Dict[str, Any]]:
    """
    Performs a GET request to the assignment API using the provided raw JWT token.
    The response data is always processed to convert numerical status codes to 
    descriptive strings, and a human-readable summary is printed upon success.

    Args:
        raw_token: The raw JWT token string (e.g., "eyJhbGciOi..."). 
                   The "Bearer " prefix is automatically added internally.
        debug: If True, prints status updates and error details to the console.

    Returns:
        The parsed JSON dictionary (with converted status strings) if the 
        request is successful and returns 200, otherwise returns None.

    Example of accessing the returned data:
        response_data = fetch_assignments(my_token, debug=False)
        if response_data:
            # 1. Get a top-level value (e.g., total number of records)
            total_count = response_data.get('totalCount')
            print(f"Total Assignments: {total_count}")

            # 2. Access the list of assignments and get a nested value 
            #    (The status is guaranteed to be a descriptive string)
            assignments = response_data.get('data')
            if assignments and len(assignments) > 0:
                first_assignment = assignments[0]
                print(f"First Assignment Name: {first_assignment.get('name')}")
                print(f"First Assignment Status: {first_assignment.get('status')}")
    """
    headers = BASE_HEADERS.copy()
    
    # Hard-code the "Bearer " prefix as requested
    headers["authorization"] = f"Bearer {raw_token}"

    if debug:
        print(f"Attempting GET request to: {API_URL}")
        # Print first 50 chars of token for debug, replacing with ... for security
        auth_display = headers.get('authorization', 'N/A')
        print(f"Using Authorization: {auth_display[:50]}...")

    try:
        # Use requests.get for the GET method
        response = requests.get(API_URL, headers=headers, timeout=10)

        # Raise an HTTPError for bad responses (4xx or 5xx status codes)
        response.raise_for_status()

        # Try to parse the response as JSON
        if 'application/json' in response.headers.get('Content-Type', '').lower():
            data = response.json()
            
            # --- Status Conversion Logic (UNCONDITIONAL) ---
            if 'data' in data and isinstance(data['data'], list):
                if debug:
                    print(f"Converting {len(data['data'])} assignment statuses to human-readable format...")
                
                for assignment in data['data']:
                    current_status = assignment.get('status')
                    if isinstance(current_status, int) and current_status in STATUS_MAP:
                        # Modify the status field to the string value
                        assignment['status'] = STATUS_MAP[current_status]
            # --- End Status Conversion Logic ---

            if debug:
                print("\n--- Request Successful (Debug Information) ---")
                print(f"Status Code: {response.status_code}")
                
            
            # Print the summary (UNCONDITIONAL)
            _print_assignment_summary(data)

            # NOTE: Raw JSON printing is removed to comply with the request to always print the summary.

            return data
        else:
            if debug:
                print("\n--- Request Successful (Non-JSON Response) ---")
                print(f"Status Code: {response.status_code}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
            return None # Expected application/json, but got something else

    except requests.exceptions.HTTPError as errh:
        if debug:
            print(f"\nHTTP Error occurred: {errh}")
            print(f"Response Content: {response.text[:500]}...")
        return None
    except requests.exceptions.RequestException as err:
        # Catches ConnectionError, Timeout, and other general request exceptions
        if debug:
            print(f"\nAn unexpected Error occurred: {err}")
        return None
    except json.JSONDecodeError:
        if debug:
            print("\nError: Could not decode response as JSON.")
            print(f"Raw response text: {response.text[:500]}...")
        return None


if __name__ == "__main__":
    # NOTE: This is the raw JWT, without the "Bearer " prefix. 
    # You must replace this with a fresh, valid token for the request to succeed.
    TEST_RAW_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5NzhlM2Q2ZWE0ZGZkZTFjZmEiLCJ1c2VyTmFtZSI6ImFuaG52MTNAYzNsdGsuaGFuYW0uZWR1LnZuIiwiaXNWZXJpZmllZCI6ZmFsc2UsIkdyYWRlSWQiOiJDMTIiLCJEaXNwbGF5TmFtZSI6Ik5ndXnhu4VuIFZp4buHdCBBbmgiLCJQcm92aW5jZUlkIjozNywiRGlzdHJpY3RJZCI6MTMzODQsIlNjaG9vbFllYXIiOjIwMjUsImNvZGVBcHAiOiJTQ0hPT0wiLCJwYXJ0bmVyIjoiT05MVVlFTiIsIlJvbGUiOiJTVFVERU5UIiwiQ3JlYXRlQnlTY2hvb2wiOjE3MTYsInByZW1pdW0iOmZhbHNlLCJjYW5DaGFuZ2VQYXNzd29yZCI6dHJ1ZSwibmVlZENoYW5nZVBhc3N3b3JkIjp0cnVlLCJFblNETG9naW4iOmZhbHNlLCJrZXlUb2tlbiI6Ijc5ODhmODRhZjZiNDE2NWFiMDVjZTkwNmVjNWIzMzkzIiwicGFja2FnZXMiOlsiSUVMVFMtc2Nob29sIiwiUFJFTUlVTS1TQ0hPT0wiXSwianRpIjoiMTRlYjQ3YWItY2NjMS00MzFkLTllZmItYWE0OWY4MDMzYTQ2IiwiaWF0IjoxNzYzMjE2NTk2LCJuYmYiOjE3NjMyMTY1OTYsImV4cCI6MTc2NTgwODU5NiwiaXNzIjoiRURNSUNSTyIsImF1ZCI6Ik9OTFVZRU4uVk4ifQ.H3Epa8WtFcRaY4cdYMDl9c9DUfOLAt478irv5xuacl0"

    # Example 1: Debug ON (Prints debug info + SUMMARY)
    print("--- Running Request 1: Debug ON (Prints debug info + SUMMARY) ---")
    fetch_assignments(TEST_RAW_TOKEN, debug=True)
    
    # Example 2: Debug OFF (Prints ONLY SUMMARY)
    print("\n" + "="*50)
    print("--- Running Request 2: Debug OFF (Prints ONLY SUMMARY) ---")
    
    # Executes silently but prints the summary upon success
    data_silent = fetch_assignments(TEST_RAW_TOKEN, debug=False)
    
    if data_silent and data_silent.get('data'):
        # Now you can use the returned data, knowing the status is already a string
        first_assignment = data_silent['data'][0]
        print("\n--- Example of accessing the returned data after the silent request ---")
        print(f"First Assignment Name: {first_assignment.get('name')}")
        print(f"Status from returned data: {first_assignment.get('status').upper()}")
    else:
        print("\nFailed to retrieve data. Check token validity or try debug=True.")