import requests
import json
#import os
import datetime

# 1. Define the BASE_URL template (ID removed, will be added dynamically)
BASE_URL = "https://api-elb.onluyen.vn/api/school-online/assignment/info"

# 2. Define Base Headers (Contextual headers removed, Authorization handled by function argument)
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json", # Specified in the original PowerShell command
    "Referer": "https://app.onluyen.vn/",
}

def _format_timestamp(timestamp: int) -> str:
    """Converts a Unix timestamp (seconds) to a human-readable string in HH:MM:SS - DD/MM/YY format."""
    if timestamp == 0 or timestamp is None:
        return "N/A"
    try:
        # Convert seconds to datetime object
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        # Format the time as HH:MM:SS - DD/MM/YY
        return dt_object.strftime("%H:%M:%S - %d/%m/%y")
    except Exception:
        return "Invalid Time"


def fetch_data_and_parse(assign_id: str, token: str, write_to_file: bool = False, debug: bool = False, output_filename: str = None): # type: ignore
    """
    Fetches assignment data from the API, parses the JSON response,
    and conditionally prints debug information or writes data to a file.

    Args:
        assign_id (str): The ID of the assignment to fetch.
        token (str): The Bearer authentication token.
        write_to_file (bool): If True, writes the raw JSON response to a text file.
        debug (bool): If True, prints the full raw JSON response to the console.
        output_filename (str, optional): Custom filename to save the JSON data to.
                                         Defaults to "assignment_response_{id}.txt".
    """
    
    # Construct the full URL dynamically using the base URL and assignment ID
    url = f"{BASE_URL}/{assign_id}"
    
    # Dynamically set the Authorization header using the provided token
    request_headers = BASE_HEADERS.copy()
    request_headers["Authorization"] = f"Bearer {token}"
    if debug:
        print(f"-> Attempting to fetch data for ID '{assign_id}' from: {url}")
    
    try:
        # Use requests.get to make the API call
        response = requests.get(url, headers=request_headers, timeout=10)

        # Check for HTTP errors (like 404, 500)
        response.raise_for_status()

        # Parse the JSON content
        data = response.json()
        beautifed = json.dumps(data, indent=4, ensure_ascii=False)
        # ----------------------------------------------------
        # 3. Conditional Debug Printing
        # ----------------------------------------------------
        if debug:
            print("\n--- Successful API Response (FULL JSON Data) ---")
            
            # Use json.dumps for raw string output, preserving non-ASCII characters (Vietnamese text)
            output = beautifed
            
            # Print the data, truncated for brevity
            print("Response Data (RAW JSON):\n")
            print(output[:1500] + "..." if len(output) > 1500 else output)
        
        # ----------------------------------------------------
        # 4. Parsing the data - Extracted key fields
        # ----------------------------------------------------
        print("\n--- Extracted Key Data Points ---")

        # Define the status mapping
        STATUS_MAPPING = {
            0: "waiting",
            1: "doing",
            2: "grading",
            3: "done",
            7: "expired"
        }

        # Check if the API request was successful based on the 'success' field
        if data.get("success"):
            print(f"API Call Status: SUCCESS")
            print(f"Message: {data.get('message', 'N/A')}")
            
            # Navigate to the main data object
            assignment_info = data.get("data", {})
            
            # Extract specific fields from the 'data' object
            assign_id_from_data = assignment_info.get("assignId", "unknown")
            assignment_name = assignment_info.get("name", "Name not found")
            total_questions = assignment_info.get("totalQuestion", 0)
            status_code = assignment_info.get("status", "N/A")
            max_score = assignment_info.get("maxScore", 0.0)

            # Extract fields for the summary table
            accuracy = assignment_info.get("accuracy", 0.0)
            percent_complete = assignment_info.get("percentComplete", 0)
            start_time_assign_ts = assignment_info.get("startTimeAssign", 0)
            start_time_ts = assignment_info.get("startTime", 0)
            submit_time_ts = assignment_info.get("submitTime", 0)
            end_time_assign_ts = assignment_info.get("endTimeAssign", 0)

            # Get the status description using the mapping
            status_description = STATUS_MAPPING.get(status_code, f"Unknown Status ({status_code})")
            
            # Convert timestamps to human-readable format
            start_time_assign_hr = _format_timestamp(start_time_assign_ts)
            start_time_hr = _format_timestamp(start_time_ts)
            submit_time_hr = _format_timestamp(submit_time_ts)
            end_time_assign_hr = _format_timestamp(end_time_assign_ts)
            
            # Print basic extracted data
            print(f"Assignment ID: {assign_id_from_data}")
            print(f"Total Questions: {total_questions}")
            print(f"Max Score: {max_score}")
            
            # --- SUMMARY TABLE PRINT ---
            print("\n--- Assignment Summary Table ---")
            
            # Define padding width for keys
            KEY_WIDTH = 25
            SEPARATOR = "-" * 50
            
            print(SEPARATOR)
            print(f"{'Name:':<{KEY_WIDTH}} {assignment_name}")
            print(f"{'Status:':<{KEY_WIDTH}} {status_description}")
            print(f"{'Accuracy:':<{KEY_WIDTH}} {accuracy:.2f}%")
            print(f"{'Percent Complete:':<{KEY_WIDTH}} {percent_complete}%")
            print(SEPARATOR)
            print(f"{'Scheduled Start Time:':<{KEY_WIDTH}} {start_time_assign_hr}")
            print(f"{'Actual Start Time:':<{KEY_WIDTH}} {start_time_hr}")
            print(f"{'Submit Time:':<{KEY_WIDTH}} {submit_time_hr}")
            print(f"{'Scheduled End Time:':<{KEY_WIDTH}} {end_time_assign_hr}")
            print(SEPARATOR)
            # --- END SUMMARY TABLE PRINT ---
            
            # ----------------------------------------------------
            # 5. Conditional Write to File
            # ----------------------------------------------------
            if write_to_file:
                # Determine the filename: use custom name if provided, otherwise use default
                if output_filename:
                    filename = output_filename
                else:
                    # Use the ID retrieved from the data object for the default filename
                    filename = f"assignment_response_{assign_id_from_data}.txt" 

                with open(filename, 'w', encoding='utf-8') as f:
                    # Write the raw JSON string (pretty-printed for readability in the file)
                    f.write(json.dumps(data, indent=4, ensure_ascii=False))
                print(f"\n[FILE WRITE] Raw JSON data successfully written to {filename}")
            return beautifed
        else:
            print(f"API Call Status: FAILURE")
            print(f"Error Message: {data.get('message', 'Unknown error')}")

    except requests.exceptions.RequestException as e:
        print(f"\n--- ERROR: Failed to make the request ---")
        print(f"Details: {e}")
    except json.JSONDecodeError:
        print("\n--- ERROR: Failed to decode JSON response ---")
        if 'response' in locals():
            print(f"Response text (first 200 chars): {response.text[:200]}...")
        else:
            print("No response object available.")

if __name__ == "__main__":
    # The assignment ID from your original request
    ASSIGNMENT_ID = "68f0b711f56366aff9c9938e"
    
    # WARNING: Replace this placeholder with a current, valid Bearer token for a successful call.
    PLACEHOLDER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5NDhlM2Q2ZWE0ZGZkZTFjZDIiLCJ1c2VyTmFtZSI6Im1pbmhudDY1QGMzbHRrLmhhbmFtLmVkdS52biIsImlzVmVyaWZpZWQiOmZhbHNlLCJHcmFkZUlkIjoiQzEyIiwiRGlzcGxheU5hbWUiOiJOZ3V54buFbiBUdeG6pW4gTWluaCIsIlByb3ZpbmNlSWQiOjM3LCJEaXN0cmljdElkIjoxMzM4NCwiU2Nob29sWWVhciI6MjAyNSwiY29kZUFwcCI6IlNDSE9PTCIsInBhcnRuZXIiOiJPTkxVWUVOIiwiUm9sZSI6IlNUVURFTlQiLCJDcmVhdGVCeVNjaG9vbCI6MTcxNiwicHJlbWl1bSI6ZmFsc2UsImNhbkNoYW5nZVBhc3N3b3JkIjp0cnVlLCJuZWVkQ2hhbmdlUGFzc3dvcmQiOnRydWUsIkVuU0RMb2dpbiI6ZmFsc2UsImtleVRva2VuIjoiNzk4OGY4NGFmNmI0MTY1YWIwNWNlOTA2ZWM1YjMzOTMiLCJwYWNrYWdlcyI6WyJJRUxUUy1zY2hvb2wiLCJQUkVNSVVNLVNDSE9PTCJdLCJqdGkiOiIyNGMyMDJiNy02ZDUyLTRhYjktYTc1OS1lZjBhN2NkNDYxY2EiLCJpYXQiOjE3NjMyODU2NzEsIm5iZiI6MTc2MzI4NTY3MSwiZXhwIjoxNzY1ODc3NjcxLCJpc3MiOiJFRE1JQ1JPIiwiYXVkIjoiT05MVVlFTi5WTiJ9.lHV0n7E7DT3kvYsO5lcpva1-yquiOXstbcUuUYEaZ9M"

    # Example 1: Basic call - No debug, no file write (default)
    print("--- Running Example 1 (Basic Parse) ---")
    fetch_data_and_parse(ASSIGNMENT_ID, PLACEHOLDER_TOKEN)

    # Example 2: Debug enabled
    print("\n--- Running Example 2 (Debug Mode: Full JSON Printed) ---")
    fetch_data_and_parse(ASSIGNMENT_ID, PLACEHOLDER_TOKEN, debug=True)

    # Example 3: Default file write enabled
    print("\n--- Running Example 3 (Default File Write Mode: JSON saved to file) ---")
    fetch_data_and_parse(ASSIGNMENT_ID, PLACEHOLDER_TOKEN, write_to_file=True)
    
    # Example 4: Custom filename enabled
    CUSTOM_FILENAME = "my_custom_assignment_data.json"
    print(f"\n--- Running Example 4 (Custom File Write Mode: JSON saved to {CUSTOM_FILENAME}) ---")
    fetch_data_and_parse(ASSIGNMENT_ID, PLACEHOLDER_TOKEN, write_to_file=True, output_filename=CUSTOM_FILENAME)