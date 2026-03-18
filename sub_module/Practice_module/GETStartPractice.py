import requests

def get_step_id(practice_id: str, bearer_token: str) -> str:
    """
    Sends a request to the OnLuyen API to start a practice session.
    
    Args:
        practice_id (str): The ID found in the URL.
        bearer_token (str): The JWT authorization token.
        
    Returns:
        str: The 'stepIdNow' value parsed from the JSON response.
    """
    url = f"https://api-elb.onluyen.vn/api/practice/start/{practice_id}"
    
    headers = {
        "authority": "api-elb.onluyen.vn",
        "accept": "application/json, text/plain, */*",
        "accept-language": "vi,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,nl;q=0.6",
        "authorization": f"Bearer {bearer_token}",
        "cache-control": "no-cache",
        "code-app": "SCHOOL",
        "origin": "https://app.onluyen.vn",
        "pragma": "no-cache",
        "referer": "https://app.onluyen.vn/",
        "school-id": "1716",
        "school-year": "2025",
        "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        
        data = response.json()
        return data.get("stepIdNow")
    
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# Example Usage:
pid = "668760f51645fe7784a47794"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5ODhlM2Q2ZWE0ZGZkZTFkMGEiLCJ1c2VyTmFtZSI6ImdpYW5nbGgxOEBjM2x0ay5oYW5hbS5lZHUudm4iLCJpc1ZlcmlmaWVkIjpmYWxzZSwiR3JhZGVJZCI6IkMxMiIsIkRpc3BsYXlOYW1lIjoiTMOqIEjGsMahbmcgR2lhbmciLCJQcm92aW5jZUlkIjozNywiRGlzdHJpY3RJZCI6MTMzODQsIlNjaG9vbFllYXIiOjIwMjUsImNvZGVBcHAiOiJTQ0hPT0wiLCJwYXJ0bmVyIjoiT05MVVlFTiIsIlJvbGUiOiJTVFVERU5UIiwiQ3JlYXRlQnlTY2hvb2wiOjE3MTYsInByZW1pdW0iOmZhbHNlLCJjYW5DaGFuZ2VQYXNzd29yZCI6dHJ1ZSwibmVlZENoYW5nZVBhc3N3b3JkIjp0cnVlLCJFblNETG9naW4iOmZhbHNlLCJwYWNrYWdlcyI6WyJJRUxUUy1zY2hvb2wiLCJQUkVNSVVNLVNDSE9PTCJdLCJqdGkiOiI2ZTZjYzVkMS1kNzY5LTQ5MmMtYTY2My02Y2IyYTIwY2ZjNzciLCJpYXQiOjE3NjUwODE4NjAsIm5iZiI6MTc2NTA4MTg2MCwiZXhwIjoxNzY3NjczODYwLCJpc3MiOiJFRE1JQ1JPIiwiYXVkIjoiT05MVVlFTi5WTiJ9.ewsADwzmJeCavThoSx7sT-ZI_FRPRvL9LhFi8sdePHM" # Replace with your full token

result = get_step_id(pid, token)
print(f"Step ID Now: {result}")