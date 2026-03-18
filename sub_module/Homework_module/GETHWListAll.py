import requests
import json
from typing import Dict, Any, List
from datetime import datetime
import textwrap

# Mapping for assignment status codes
STATUS_MAP = {
    0: "Waiting",
    1: "Doing",
    2: "Grading",
    3: "Done",
    7: "Expired"
}

def fetch_homework_data(auth_token: str) -> Dict[str, Any] | None:
    """
    Makes a GET request to the onluyen.vn API using the provided Bearer token
    and custom headers, converting the original PowerShell script logic.

    Args:
        auth_token: The JWT (JSON Web Token) to be used in the Authorization header.

    Returns:
        The parsed JSON response data as a dictionary, or None if the request failed.
    """
    url = "https://api-elb.onluyen.vn/api/student/data-mission-assignment-elearning"

    # Define the headers, adapting from the original PowerShell script.
    headers = {
        # Customizations based on request:
        "Authorization": f"Bearer {auth_token}",
        "Accept-Encoding": "gzip, deflate, zstd",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",

        # Remaining headers from the original script:
        "Accept": "application/json, text/plain, */*",
        "authority": "api-elb.onluyen.vn",
        "Accept-Language": "vi,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,nl;q=0.6",
        "Cache-Control": "no-cache",
        "code-app": "SCHOOL",
        "Origin": "https://app.onluyen.vn",
        "Pragma": "no-cache",
        "priority": "u=1, i",
        "Referer": "https://app.onluyen.vn/",
        "school-id": "1716",
        "school-year": "2025",
        "Sec-Ch-Ua": '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    try:
        # Perform the GET request
        response = requests.get(url, headers=headers)

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # Assuming the API returns JSON data
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return None

def format_timestamp(ts: int) -> str:
    """Converts a Unix timestamp (seconds) to a formatted date string (HH:MM:YY - DD/MM/YY)."""
    try:
        return datetime.fromtimestamp(ts).strftime('%H:%M:%y - %d/%m/%y')
    except (ValueError, TypeError):
        return "N/A"

def extract_detailed_summary(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts detailed assignment information from the API response."""
    detailed_list = []
    class_assignments = data.get('data', [])

    for class_item in class_assignments:
        class_name = class_item.get('className', 'Unknown Class')
        data_list = class_item.get('data', [])

        for data_group in data_list:
            # We are interested in assignments where 'type' is 0
            if data_group.get('type') == 0:
                assignments = data_group.get('data', [])
                for assignment in assignments:
                    detailed_list.append({
                        'logid': assignment.get('assignClassLogId', 'N/A'),
                        'name': assignment.get('name', 'N/A'),
                        'subject': class_name,
                        'status': STATUS_MAP.get(assignment.get('status'), 'Unknown'),
                        'time_assign': format_timestamp(assignment.get('timeAssign', 0)),
                        'time_expired': format_timestamp(assignment.get('timeExpired', 0)),
                        'retryable': 'Yes' if assignment.get('retryable', False) else 'No',
                        'content_type': assignment.get('assignmentContentType', 'N/A'),
                    }) # Move to the next class once type 0 is processed
            if data_group.get('type') == 1:
                assignments = data_group.get('data', [])
                for assignment in assignments:
                    detailed_list.append({
                        'logid': assignment.get('id', 'N/A'),
                        'name': assignment.get('name', 'N/A'),
                        'subject': class_name,
                        'status': STATUS_MAP.get(assignment.get('status'), 'Unknown'),
                        'time_assign': format_timestamp(assignment.get('timeAssign', 0)),
                        'time_expired': format_timestamp(assignment.get('timeExpired', 0)),
                        'retryable': 'Yes' if assignment.get('retryable', False) else 'No',
                        'content_type': "Practice",
                    })

    return detailed_list

def filter_assignments_by_status(assignments: List[Dict[str, Any]], target_status: str) -> List[Dict[str, Any]]:
    """
    Filters a list of assignments based on a specified status string (case-insensitive).
    
    Args:
        assignments: The list of assignment dictionaries.
        target_status: The status string to filter by (e.g., 'Done', 'Expired').
        
    Returns:
        A new list containing only the assignments matching the target status.
    """
    if not target_status:
        return assignments # Return all if status is empty
        
    target_status_lower = target_status.lower()
    
    return [
        assignment for assignment in assignments
        if assignment['status'].lower() == target_status_lower
    ]

def filter_assignments_by_logid(assignments: List[Dict[str, Any]], target_logid: str) -> List[Dict[str, Any]]:
    """
    Filters a list of assignments based on whether their Log ID contains the target string
    (case-insensitive partial match).
    
    Args:
        assignments: The list of assignment dictionaries.
        target_logid: The log ID string or substring to filter by.
        
    Returns:
        A new list containing only the assignments whose log ID matches the target.
    """
    if not target_logid:
        return assignments # Return all if ID is empty
        
    target_logid_lower = target_logid.lower()
    
    return [
        assignment for assignment in assignments
        # Check if the lower-case Log ID contains the lower-case target string
        if target_logid_lower in assignment['logid'].lower()
    ]

def check_assignment_availability(assignments: List[Dict[str, Any]], target_logid: str, target_status: str) -> bool:
    """
    Checks if an assignment with the specified Log ID (partial match) and status exists.

    Args:
        assignments: The list of assignment dictionaries.
        target_logid: The log ID string or substring to look for.
        target_status: The status string to look for (e.g., 'Done', 'Expired').

    Returns:
        True if an assignment matching both criteria is found, False otherwise.
    """
    if not target_logid or not target_status:
        # Cannot search if either criterion is empty/missing
        return False

    target_logid_lower = target_logid.lower()
    target_status_lower = target_status.lower()

    for assignment in assignments:
        # 1. Check for Log ID match (partial, case-insensitive)
        logid_match = target_logid_lower in assignment['logid'].lower()
        
        # 2. Check for Status match (exact, case-insensitive)
        status_match = assignment['status'].lower() == target_status_lower

        if logid_match and status_match:
            return True

    return False

def print_assignment_table(assignments: List[Dict[str, Any]]):
    """Prints the detailed list of assignments in a formatted, organized table."""
    total_assignments = len(assignments)

    if total_assignments == 0:
        print("No assignments found in the data to display.")
        return

    print(f"Total Assignments Found: {total_assignments}\n")

    # Define column widths for alignment
    COL_WIDTHS = {
        'Subject': 25,
        'Name': 40,
        'Status': 10,
        'Assigned': 17,
        'Expired': 17,
        'Retry': 7,
        'Log ID': 24, # Displaying the last 24 chars of the log ID
        'Type': 6
    }
    
    # Helper function for text padding and truncation
    def format_cell(text, width):
        return str(text).ljust(width)[:width]

    # Print Header
    header = (
        format_cell('Subject', COL_WIDTHS['Subject']) +
        format_cell('Name', COL_WIDTHS['Name']) +
        format_cell('Status', COL_WIDTHS['Status']) +
        format_cell('Assigned', COL_WIDTHS['Assigned']) +
        format_cell('Expired', COL_WIDTHS['Expired']) +
        format_cell('Retry', COL_WIDTHS['Retry']) +
        format_cell('Type', COL_WIDTHS['Type']) +
        format_cell('Log ID', COL_WIDTHS['Log ID'])
    )
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    # Print Data Rows
    for assignment in assignments:
        row = (
            format_cell(assignment['subject'], COL_WIDTHS['Subject']) +
            format_cell(assignment['name'], COL_WIDTHS['Name']) +
            format_cell(assignment['status'], COL_WIDTHS['Status']) +
            format_cell(assignment['time_assign'], COL_WIDTHS['Assigned']) +
            format_cell(assignment['time_expired'], COL_WIDTHS['Expired']) +
            format_cell(assignment['retryable'], COL_WIDTHS['Retry']) +
            format_cell(assignment['content_type'], COL_WIDTHS['Type']) +
            # Use the last 24 characters of Log ID for space
            format_cell(assignment['logid'][-24:], COL_WIDTHS['Log ID'])
        )
        print(row)
    
    print("-" * len(header))


# --- Example Usage ---

if __name__ == '__main__':
    # NOTE: Replace this placeholder with your actual Bearer token
    example_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5NjhlM2Q2ZWE0ZGZkZTFjZjIiLCJ1c2VyTmFtZSI6InZ5bHA5MEBjM2x0ay5oYW5hbS5lZHUudm4iLCJpc1ZlcmlmaWVkIjpmYWxzZSwiR3JhZGVJZCI6IkMxMiIsIkRpc3BsYXlOYW1lIjoiTMOqIFBoxrDGoW5nIFZ5IiwiUHJvdmluY2VJZCI6MzcsIkRpc3RyaWN0SWQiOjEzMzg0LCJTY2hvb2xZZWFyIjoyMDI1LCJjb2RlQXBwIjoiU0NIT09MIiwicGFydG5lciI6Ik9OTFVZRU4iLCJSb2xlIjoiU1RVREVOVCIsIkNyZWF0ZUJ5U2Nob29sIjoxNzE2LCJwcmVtaXVtIjpmYWxzZSwiY2FuQ2hhbmdlUGFzc3dvcmQiOnRydWUsIm5lZWRDaGFuZ2VQYXNzd29yZCI6ZmFsc2UsIkVuU0RMb2dpbiI6ZmFsc2UsInBhY2thZ2VzIjpbIlBSRU1JVU0tU0NIT09MIiwiSUVMVFMtc2Nob29sIl0sImp0aSI6ImFlYmE2ZDc2LTEwYzgtNGFlOS1iZTYxLTA1YWIwYWI5NDlkNiIsImlhdCI6MTc2NTA2OTk4MCwibmJmIjoxNzY1MDY5OTgwLCJleHAiOjE3Njc2NjE5ODAsImlzcyI6IkVETUlDUk8iLCJhdWQiOiJPTkxVWUVOLlZOIn0.xEj014rb6WzHLXrPDJlplNPhBa6AM5G_q0IWwewpfbo"

    print("Attempting to fetch data...")

    data = fetch_homework_data(example_token)



    # Check if data was successfully retrieved and is in the expected format
    if data and data.get('success') is True and isinstance(data.get('data'), list):
        print("\n--- Request Successful (Using Sample Data for Summary) ---")
        
        # 1. Extract all assignments
        all_assignments = extract_detailed_summary(data)
        print(f"Total assignments extracted: {len(all_assignments)}")
        print_assignment_table(all_assignments)
        # --- Example 1: Filtering by Status (Done) ---
        target_status = "Done"
        print(f"\n[EXAMPLE 1] Filtering assignments for status: '{target_status}'")
        
        filtered_by_status = filter_assignments_by_status(all_assignments, target_status)
        print_assignment_table(filtered_by_status)
        
        # --- Example 2: Filtering by Log ID (Partial Match) ---
        # The sample data has a Log ID: 68eefe56034c1960bb3107f9 (Expired status)
        target_logid = "3107f9"
        print(f"\n[EXAMPLE 2] Filtering assignments for partial Log ID: '...{target_logid}'")
        
        filtered_by_logid = filter_assignments_by_logid(all_assignments, target_logid)
        print_assignment_table(filtered_by_logid)
        
        # --- Example 3: Checking availability (New Function Demonstration) ---
        print("\n[EXAMPLE 3] Checking if specific Log IDs with specific Statuses exist:")
        
        # Test Case 1: Existing ID and Status ('luyện tập' is Expired, Log ID ends in 3107f9)
        id_to_check_1 = "3107f9"
        status_to_check_1 = "Expired"
        is_available_1 = check_assignment_availability(all_assignments, id_to_check_1, status_to_check_1)
        print(f"Is assignment with ID '...{id_to_check_1}' and status '{status_to_check_1}' available? {is_available_1}") # Should be True

        # Test Case 2: Existing ID but Wrong Status (Try finding the 'luyện tập' assignment as Done)
        id_to_check_2 = "3107f9"
        status_to_check_2 = "Done"
        is_available_2 = check_assignment_availability(all_assignments, id_to_check_2, status_to_check_2)
        print(f"Is assignment with ID '...{id_to_check_2}' and status '{status_to_check_2}' available? {is_available_2}") # Should be False

        # Test Case 3: Non-existent ID (Looking for an ID that doesn't exist)
        id_to_check_3 = "ZZZZZ"
        status_to_check_3 = "Done"
        is_available_3 = check_assignment_availability(all_assignments, id_to_check_3, status_to_check_3)
        print(f"Is assignment with ID '...{id_to_check_3}' and status '{status_to_check_3}' available? {is_available_3}") # Should be False
        
    else:
        print("\n--- Request Failed ---")
        print("Could not retrieve data or response format was unexpected. Check the token and network connection.")