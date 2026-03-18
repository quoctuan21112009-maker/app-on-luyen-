import requests
import json
import os

def get_assignment_data(token: str, assignment_id: str, write_to_file: str = None) -> dict: # type: ignore
    """
    Fetches assignment data from the onluyen.vn API using a Bearer token.

    The function recreates the headers from the original PowerShell request,
    removes the unnecessary 'user-id' and 'user-name' headers, and handles
    the Bearer token authentication.

    Args:
        token: The raw JWT token string (e.g., 'eyJhbGciOi...').
               The 'Bearer ' prefix is added automatically.
        assignment_id: The ID of the assignment to fetch (e.g., '6913d551cc53ac706116c66a').

    Returns:
        A dictionary containing the parsed JSON response from the API,
        or an error dictionary if the request fails.
    """
    # Use the assignment_id argument to construct the URL
    url = f"https://api-elb.onluyen.vn/api/school-online/assignment/doing/{assignment_id}"

    # Minimal necessary headers derived from the original request
    headers = {
        # Dynamically set Authorization header with hardcoded 'Bearer ' prefix
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "authority": "api-elb.onluyen.vn",
        "cache-control": "no-cache",
        "code-app": "SCHOOL",
        "origin": "https://app.onluyen.vn",
        "referer": "https://app.onluyen.vn/",
        "school-id": "1716",
        "school-year": "2025",
        # Note: 'user-id' and 'user-name' headers have been removed as requested.
    }

    try:
        # Perform the GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        datautf = json.dumps(response.json(), indent=4, ensure_ascii= False)
        if write_to_file != None:
            with open(f'{write_to_file}.json', "w", encoding="utf8") as f:
                f.write(datautf)
        # Return the parsed JSON content
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        # Return structured error information
        return {"error": "Request failed", "details": str(e), "status_code": getattr(response, 'status_code', 'N/A')}
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return {"error": "JSON Decode Error", "response_text": response.text}


# --- Example Usage ---
if __name__ == "__main__":
    # WARNING: This token is public and should be replaced with a secure method
    # or loaded from an environment variable in a real application.
    # The example token is included for demonstration purposes only.
    example_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5NThlM2Q2ZWE0ZGZkZTFjZGUiLCJ1c2VyTmFtZSI6Im5oaW55M0BjM2x0ay5oYW5hbS5lZHUudm4iLCJpc1ZlcmlmaWVkIjpmYWxzZSwiR3JhZGVJZCI6IkMxMiIsIkRpc3BsYXlOYW1lIjoiTmd1eeG7hW4gWeG6v24gTmhpIiwiUHJvdmluY2VJZCI6MzcsIkRpc3RyaWN0SWQiOjEzMzg0LCJTY2hvb2xZZWFyIjoyMDI1LCJjb2RlQXBwIjoiU0NIT09MIiwicGFydG5lciI6Ik9OTFVZRU4iLCJSb2xlIjoiU1RVREVOVCIsIkNyZWF0ZUJ5U2Nob29sIjoxNzE2LCJwcmVtaXVtIjpmYWxzZSwiY2FuQ2hhbmdlUGFzc3dvcmQiOnRydWUsIm5lZWRDaGFuZ2VQYXNzd29yZCI6dHJ1ZSwiRW5TRExvZ2luIjpmYWxzZSwicGFja2FnZXMiOlsiUFJFTUlVTS1TQ0hPT0wiLCJJRUxUUy1zY2hvb2wiXSwianRpIjoiY2U4ZmZiNzAtOGViNC00ZTQ4LWIxZTItOGFhNWMyM2VhZDYzIiwiaWF0IjoxNzY0MzUyNDk1LCJuYmYiOjE3NjQzNTI0OTUsImV4cCI6MTc2Njk0NDQ5NSwiaXNzIjoiRURNSUNSTyIsImF1ZCI6Ik9OTFVZRU4uVk4ifQ.WhMDZNt5GSyC2G0oUTmdoj6_BLtIKpiRZ44wOrmD0Ks"
    
    # Define the assignment ID here for the example
    assignment_id = "6925175257021d562da69e90"

    print("--- Running Assignment Data Fetcher ---")

    # Call the function with the token and the ID
    data = get_assignment_data(example_token, assignment_id)
    datautf = json.dumps(data, indent=4, ensure_ascii= False)
    if "error" in data:
        print("\n--- ERROR ---")
        print(f"Status Code: {data.get('status_code', 'N/A')}")
        print(f"Details: {data.get('details', 'N/A')}")
    else:
        print("\n--- Success: Received Data ---")
        # Print a concise summary of the response
        print(f"Response Keys: {list(data.keys())}")
        print(f"First 200 characters of data (for preview): {str(datautf)[:200]}...")
        # Optional: Save to a file for review
        with open("assignment_response.json", "w", encoding="utf8") as f:
            f.write(datautf)
        print("\nFull response saved to assignment_response.json")