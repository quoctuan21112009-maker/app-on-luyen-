import requests
import json
import sys
from typing import Optional, Dict, Any

# Note: The 'brotli' package is no longer strictly necessary since 'br' 
# has been removed from the Accept-Encoding header, but it's good practice
# to keep it installed if you expect other requests to use it.

def make_login_request(username: str, userpass: str, debug: bool = False) -> Optional[Dict[str, Any]]:
    """
    Executes a POST request to the onluyen.vn login API with specific headers and user credentials.

    Args:
        username (str): The user's identification (phone number or email) which is used 
                        for both the "phoneNumber" and "userName" fields in the payload.
        userpass (str): The user's password.
        debug (bool, optional): If True, prints detailed information about the request 
                                (status code, URL, and response body). Defaults to False.
                             
    Returns:
        Optional[Dict[str, Any]]: The parsed JSON dictionary from the successful 
                                  response body if the status code is 200 and the content is valid JSON.
                                  The dictionary typically includes the following keys on success:
                                  - "access_token" (str): The JWT token used for subsequent authorized API calls.
                                  - "refresh_token" (str): The token used to generate new access tokens.
                                  - "userId" (str): The unique identifier for the authenticated user.
                                  - "display_name" (str): The user's display name.
                                  - "expires_in" (int): The access token's lifespan in seconds.
                                  - "expires_at" (str): The expiration time in ISO format.
                                  Returns None on failure (non-200 status, network error, or invalid JSON).
    """
    # --- 1. Define the URL ---
    url = "https://oauth.onluyen.vn/api/account/login"
    
    # --- 2. Construct the Data Payload ---
    # This dictionary is constructed dynamically using the function arguments.
    data_payload = {
        "phoneNumber": username,
        "password": userpass,
        "rememberMe": True,
        "userName": username,
        "socialType": "Email"
    }
    
    # --- 3. Define the Request Headers ---
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
        "authority": "oauth.onluyen.vn",
        "method": "POST",
        "path": "/api/account/login",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, zstd", 
        "accept-language": "vi,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,nl;q=0.6",
        "access-control-allow-origin": "*",
        "cache-control": "no-cache",
        "origin": "https://app.onluyen.vn",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://app.onluyen.vn/",
        "sec-ch-ua": "\"Chromium\";v=\"142\", \"Microsoft Edge\";v=\"142\", \"Not_A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "Content-Type": "application/json"
    }

    # --- 4. Execute the POST Request ---
    try:
        if debug:
            print(f"Attempting POST request to: {url}")
            print(f"Payload: {data_payload}")
            
        # Execute the request, using the constructed data_payload
        response = requests.post(url, headers=headers, json=data_payload, timeout=10)

        # --- 5. Process the Response ---
        
        if debug:
            print("\n--- Response Status and Headers ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response URL: {response.url}")

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            if debug:
                print("\n--- Successful Response Body ---")
            try:
                parsed_json = response.json()
                if debug:
                    # Attempt to parse as JSON and print prettily
                    print("Response Format: JSON")
                    print(json.dumps(parsed_json, indent=4, ensure_ascii=True))
                if 'status' in parsed_json and parsed_json['status'] == -1:
                    raise ValueError(f"Login failed, invalid credentials for {username} or other error.")
                # Return the parsed JSON response
                return parsed_json
            
            except requests.exceptions.JSONDecodeError:
                # If JSON decoding fails, print the raw text content
                if debug:
                    print("Response Format: Plain Text (Could not decode as JSON)")
                    text_content = response.text
                    print("Text Content:", text_content[:500] + ("..." if len(text_content) > 500 else ""))
                return None # Return None if successful status but unparsable body
        else:
            # Handle non-200 status codes
            if debug:
                print(f"\nRequest failed with status code {response.status_code}.")
                text_content = response.text
                print("Response Text:", text_content[:500] + ("..." if len(text_content) > 500 else ""))
            return None # Return None on unsuccessful status

    except requests.exceptions.RequestException as e:
        # This catches network errors, connection timeouts, and other general request issues
        print(f"\nAn error occurred during the request (Connection/Timeout): {e}", file=sys.stderr)
        return None # Return None on network error


if __name__ == "__main__":
    # Example usage when running the script directly
    example_username = "anhnv13@c3ltk.hanam.edu.vn"
    example_password = "929313"
    
    print("--- Running make_login_request with debug=True ---")
    
    # Call the function using the new username and userpass arguments
    response_data = make_login_request(example_username, example_password, debug=True) 
    
    if response_data:
        print("\n*** Function returned data successfully ***")
        # Example of how you would access the data when calling the function
        if 'access_token' in response_data:
            print(f"Access Token retrieved: {response_data['access_token'][:30]}...")
        if 'userId' in response_data:
            print(f"User ID: {response_data['userId']}")
    else:
        print("\n*** Function returned None (request failed or invalid response) ***")