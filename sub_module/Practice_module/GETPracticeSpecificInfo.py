import requests

def get_practice_info(practice_id, token):
    """
    Fetches practice information and returns specific parsed fields.
    """
    url = f"https://api-elb.onluyen.vn/api/practice/info/{practice_id}"
    
    headers = {
        "authority": "api-elb.onluyen.vn",
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "code-app": "SCHOOL",
        "origin": "https://app.onluyen.vn",
        "referer": "https://app.onluyen.vn/",
        "school-id": "1716",
        "school-year": "2025",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Extract specific fields
        parsed_data = {
            "title": data.get("title", "N/A"),
            "knowledgeId": data.get("knowledgeId", "N/A"),
            "stepId": data.get("stepIdNow", "N/A")
        }
        
        return parsed_data
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    TEST_ID = "668760ef1645fe7784a47792"
    TEST_TOKEN = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5ODhl"
        "M2Q2ZWE0ZGZkZTFkMGEiLCJ1c2VyTmFtZSI6ImdpYW5nbGgxOEBjM2x0ay5oYW5hbS5lZHUudm4iLCJpc1Zlcmlm"
        "aWVkIjpmYWxzZSwiR3JhZGVJZCI6IkMxMiIsIkRpc3BsYXlOYW1lIjoiTMOqIEjGsMahbmcgR2lhbmciLCJQcm92"
        "aW5jZUlkIjozNywiRGlzdHJpY3RJZCI6MTMzODQsIlNjaG9vbFllYXIiOjIwMjUsImNvZGVBcHAiOiJTQ0hPT0wi"
        "LCJwYXJ0bmVyIjoiT05MVVlFTiIsIlJvbGUiOiJTVFVERU5UIiwiQ3JlYXRlQnlTY2hvb2wiOjE3MTYsInByZW1p"
        "dW0iOmZhbHNlLCJjYW5DaGFuZ2VQYXNzd29yZCI6dHJ1ZSwibmVlZENoYW5nZVBhc3N3b3JkIjp0cnVlLCJFblNE"
        "TG9naW4iOmZhbHNlLCJwYWNrYWdlcyI6WyJJRUxUUy1zY2hvb2wiLCJQUkVNSVVNLVNDSE9PTCJdLCJqdGkiOiI2"
        "ZTZjYzVkMS1kNzY5LTQ5MmMtYTY2My02Y2IyYTIwY2ZjNzciLCJpYXQiOjE3NjUwODE4NjAsIm5iZiI6MTc2NTA4"
        "MTg2MCwiZXhwIjoxNzY3NjczODYwLCJpc3MiOiJFRE1JQ1JPIiwiYXVkIjoiT05MVVlFTi5WTiJ9.ewsADwzmJeCa"
        "vThoSx7sT-ZI_FRPRvL9LhFi8sdePHM"
    )

    print(f"Requesting data for ID: {TEST_ID}...")
    result = get_practice_info(TEST_ID, TEST_TOKEN)
    
    if "error" in result:
        print(f"Request failed: {result['error']}")
    else:
        print("--- Parsed Response ---")
        print(f"Title: {result['title']}")
        print(f"Knowledge ID: {result['knowledgeId']}")