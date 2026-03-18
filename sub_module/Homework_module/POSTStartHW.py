import requests
import json
from typing import Optional, Dict

# --- Configuration ---
# The target BASE URL with a placeholder for the ID (e.g., {})
BASE_API_URL = "https://api-elb.onluyen.vn/api/school-online/assignment/start/{}"

# The body data, which is an empty JSON object "{}"
REQUEST_DATA = {}

# Mandatory Headers (required for HTTP/Request Library functionality)
MANDATORY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, zstd",
}

# Optional/Application-Specific Headers (Custom context for the target API)
OPTIONAL_HEADERS = {
    "authority": "api-elb.onluyen.vn",
    "accept-language": "vi,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,nl;q=0.6",
    "cache-control": "no-cache",
    "code-app": "SCHOOL",
    "origin": "https://app.onluyen.vn",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://app.onluyen.vn/",
    #"school-id": "1716",
    #"school-year": "2025",
    "sec-ch-ua": '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
}

def print_response_summary(response: requests.Response):
    """
    Parses the response JSON and prints a concise summary of the request outcome,
    handling Vietnamese characters correctly.
    """
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("\n--- Summary: Failed to Decode JSON ---")
        print(f"HTTP Status Code: {response.status_code}")
        print("Response content was not valid JSON.")
        return

    is_success = data.get("success", False)
    # The message should print correctly due to ensure_ascii=False in the overall logic.
    message = data.get("message", "No message provided")
    
    status_icon = "✅ SUCCESS" if is_success else "❌ FAILED"
    
    print("\n" + "="*60)
    print(" " * 18 + "API RESPONSE SUMMARY" + " " * 18)
    print("="*60)
    print(f"Overall Status: {status_icon}")
    print(f"HTTP Status Code: {response.status_code}")
    print(f"API Message: {message}")
    
    # Print specific details only available on success
    if is_success and data.get("data"):
        assignment_data = data["data"]
        print("-" * 60)
        print("Assignment Details:")
        print(f"  Assignment ID: {assignment_data.get('assignId')}")
        print(f"  Question ID: {assignment_data.get('questionId')}")
        print(f"  Time Spent (s): {assignment_data.get('timeDoing')} seconds")
        print(f"  Response Time (Server): {data.get('timeResp')}")
    elif not is_success:
        print(f"Response Time (Server): {data.get('timeResp')}")
        
    print("="*60)


def start_assignment_request(assignment_id: str, token: str, debug_flag: bool = False) -> Optional[requests.Response]:
    """
    Performs the HTTP POST request to the API endpoint with dynamic token, assignment ID, and debug control.

    :param assignment_id: The unique ID for the assignment to be started.
    :param token: The raw JWT token (without the "Bearer " prefix).
    :param debug_flag: If True, prints detailed request and response information.
    :return: The requests.Response object if successful, otherwise None.
    """
    
    # 1. Construct the final API URL using the passed assignment_id
    api_url = BASE_API_URL.format(assignment_id)
    
    # 2. Combine all headers and add Authorization
    headers = MANDATORY_HEADERS.copy()
    headers.update(OPTIONAL_HEADERS)
    
    # Hard-code the "Bearer " prefix when setting the Authorization header
    headers["Authorization"] = f"Bearer {token}"

    if debug_flag:
        print("\n--- DEBUG: Request Details ---")
        print(f"URL: {api_url}")
        # Use ensure_ascii=False here to show Vietnamese characters in debug headers
        print(f"Headers: {json.dumps(headers, indent=4, ensure_ascii=False)}")
        print(f"Request Body: {REQUEST_DATA}")
    
    try:
        # requests.post is used for the POST -Method
        # json=REQUEST_DATA handles the -Body "{}" and ensures Content-Type is application/json
        response = requests.post(api_url, headers=headers, json=REQUEST_DATA)

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        if debug_flag:
            print("\n--- DEBUG: Successful Response ---")
            print(f"Status Code: {response.status_code}")
            
            # Check if the response has JSON content
            if response.text and 'application/json' in response.headers.get('Content-Type', ''):
                # Print the JSON response prettily, ensuring non-ASCII characters are displayed correctly
                try:
                    print("Response JSON:")
                    print(json.dumps(response.json(), indent=4, ensure_ascii=False))
                except json.JSONDecodeError:
                    print("Response text (not valid JSON):")
                    print(response.text[:500] + '...' if len(response.text) > 500 else response.text)
            else:
                print("Response Text:")
                print(response.text)
        
        return response

    except requests.exceptions.HTTPError as errh:
        if debug_flag:
            # Print detailed error response in debug mode
            print(f"\n--- DEBUG: HTTP Error ---")
            print(f"Status Code: {response.status_code}")
            print(f"Error Response: {response.text}")
        
        # We return the response even on HTTP errors to allow summarization of the API error body
        return response 
    except requests.exceptions.ConnectionError as errc:
        print(f"\n--- Connection Error ---")
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(f"\n--- Timeout Error ---")
        print(errt)
    except requests.exceptions.RequestException as err:
        print(f"\n--- An Unknown Error Occurred ---")
        print(err)
        
    return None

if __name__ == "__main__":
    # Ensure you have the 'requests' library installed: pip install requests
    
    # The assignment ID to be passed to the function
    SAMPLE_ASSIGNMENT_ID = "6913d551cc53ac706116c66a" 
    
    # Use the token extracted from the original script (WITHOUT "Bearer ")
    SAMPLE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5NzhlM2Q2ZWE0ZGZkZTFjZmEiLCJ1c2VyTmFtZSI6ImFuaG52MTNAYzNsdGsuaGFuYW0uZWR1LnZuIiwiaXNWZXJpZmllZCI6ZmFsc2UsIkdyYWRlSWQiOiJDMTIiLCJEaXNwbGF5TmFtZSI6Ik5ndXnhu4VuIFZp4buHdCBBbmgiLCJQcm92aW5jZUlkIjozNywiRGlzdHJpY3RJZCI6MTMzODQsIlNjaG9vbFllYXIiOjIwMjUsImNvZGVBcHAiOiJTQ0hPT0wiLCJwYXJ0bmVyIjoiT05MVVlFTiIsIlJvbGUiOiJTVFVERU5UIiwiQ3JlYXRlQnlTY2hvb2wiOjE3MTYsInByZW1pdW0iOmZhbHNlLCJjYW5DaGFuZ2VQYXNzd29yZCI6dHJ1ZSwibmVlZENoYW5nZVBhc3N3b3JkIjp0cnVlLCJFblNETG9naW4iOmZhbHNlLCJrZXlUb2tlbiI6Ijc5ODhmODRhZjZiNDE2NWFiMDVjZTkwNmVjNWIzMzkzIiwicGFja2FnZXMiOlsiSUVMVFMtc2Nob29sIiwiUFJFTUlVTS1TQ0hPT0wiXSwianRpIjoiMTRlYjQ3YWItY2NjMS00MzFkLTllZmItYWE0OWY4MDMzYTQ2IiwiaWF0IjoxNzYzMjE2NTk2LCJuYmYiOjE3NjMyMTY1OTYsImV4cCI6MTc2NTgwODU5NiwiaXNzIjoiRURNSUNSTyIsImF1ZCI6Ik9OTFVZRU4uVk4ifQ.H3Epa8WtFcRaY4cdYMDl9c9DUfOLAt478irv5xuacl0"

    print("--- Running API Request Example (Debug ON) ---")
    response = start_assignment_request(
        assignment_id=SAMPLE_ASSIGNMENT_ID,  # Pass the ID here
        token=SAMPLE_TOKEN,
        debug_flag=True # Set to True to see all request/response details
    )
    
    # Only try to summarize if a response object was returned (even if the HTTP status was bad)
    if response is not None:
        try:
            # Check if the response body is available and parseable
            response.json()
            print_response_summary(response)
        except json.JSONDecodeError:
            print("\nRequest failed. Could not parse API response body for summary.")
    else:
        print("\nRequest failed (no response object returned due to connection/timeout error).")