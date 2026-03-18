import requests
import json
import time

# --- Configuration ---
# NOTE: The URL and headers are often dynamically generated (especially the signature
# and date/time components). For demonstration, we use the specific ones provided.
# In a real application, the URL/body might be passed as arguments.

API_URL = "https://onluyen-assignment-submission.s3.ap-southeast-1.amazonaws.com/assign/6927baf6b27e6d7781dc126f/66e7d7948e3d6ea4dfde1cd2/69293faa6e3c7680626d77b4.json?X-Amz-Expires=10980&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARNHFJRUSPDX4IUU6%2F20251128%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Date=20251128T062234Z&X-Amz-SignedHeaders=content-type%3Bhost&X-Amz-Signature=3cdddbe0b67cd36293b20b16b5bd6598fc8f9b4db9086ac595b6f34c649d3796"

# The request body data
ASSIGNMENT_DATA = [
    {
        "optionText": ["3"],
        "id": "69293faa6e3c7680626d77b7",
        "isSkip": False,
        "studentDoRight": None,
        "timeUpdate": 1764311039
    },
    {
        "optionText": ["3"],
        "id": "69293faa6e3c7680626d77de",
        "isSkip": False,
        "studentDoRight": None,
        "timeUpdate": 1764311051
    }
]

# The request headers
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "vi,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,nl;q=0.6",
    "Cache-Control": "no-cache",
    "Origin": "https://app.onluyen.vn",
    "Pragma": "no-cache",
    "Referer": "https://app.onluyen.vn/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "sec-ch-ua": "\"Chromium\";v=\"142\", \"Microsoft Edge\";v=\"142\", \"Not_A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Content-Type": "application/json"
}

def submit_assignment(url=API_URL, data=ASSIGNMENT_DATA, headers=REQUEST_HEADERS):
    """
    Performs a PUT request to the specified URL with assignment submission data.

    Args:
        url (str): The pre-signed S3 URL for the PUT request.
        data (list): The list of assignment submission objects (will be serialized to JSON).
        headers (dict): The dictionary of HTTP headers.

    Returns:
        tuple: A tuple containing (success: bool, status_code: int, message: str)
    """
    max_retries = 3
    
    # Retry logic implementation using a simple loop
    for attempt in range(max_retries):
        try:
            # requests.put uses the 'json' parameter to automatically set the
            # Content-Type header and serialize the Python list 'data' to JSON.
            response = requests.put(url, headers=headers, json=data, timeout=10)
            
            # Check for standard HTTP errors (4xx or 5xx)
            response.raise_for_status()

            # Request was successful (e.g., 200, 201, 204)
            return True, response.status_code, "Assignment submitted successfully."

        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors
            error_message = f"HTTP Error {e.response.status_code}: {e.response.reason}"
            print(f"Attempt {attempt + 1} failed: {error_message}")
            if attempt < max_retries - 1 and e.response.status_code in (408, 429, 500, 502, 503, 504):
                # Retry on temporary server errors or timeouts
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                continue
            return False, e.response.status_code, f"Failed to submit assignment. {error_message}"
        
        except requests.exceptions.RequestException as e:
            # Handle non-HTTP errors like connection loss or DNS failure
            error_message = f"Connection Error: {e}"
            print(f"Attempt {attempt + 1} failed: {error_message}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return False, 0, f"Failed to submit assignment. {error_message}"
        
    return False, 0, "Failed to submit assignment after multiple retries."


# This block ensures the script only runs the function if executed directly (not imported)
if __name__ == "__main__":
    print("--- Running API Client Test Directly ---")
    
    # In this context, we demonstrate a direct call of the function.
    success, status, message = submit_assignment()
    
    print(f"\nResult: {'SUCCESS' if success else 'FAILURE'}")
    print(f"Status Code: {status}")
    print(f"Message: {message}")