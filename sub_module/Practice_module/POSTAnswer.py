import requests
import json

def send_answer(token, payload):
    """
    Sends a practice answer and returns parsed status and specific data points.
    """
    url = "https://api-elb.onluyen.vn/api/practice/questions/sendanswer"
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
        "authorization": f"Bearer {token}" if not token.startswith("Bearer") else token,
        "content-type": "application/json",
        "code-app": "SCHOOL",
        "school-id": "1716"
    }

    try:
        response = session.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        # --- Integrated Parsing Logic ---
        
        # 1. Top-level status and next ID
        is_answer = data.get('isAnswer', False)
        next_step_id = data.get('nextStepId', '')

        # 2. Find content of the correct option
        correct_content = next(
            (opt.get('content') for opt in data.get('options', []) if opt.get('isAnswer')), 
            "No correct answer found"
        )

        # 3. Build the custom results dictionary
        parsed_dict = {
            "stepId": data.get('stepId'),
            "nextStepId": next_step_id,
            "content-dataStandard": data.get('content'),
            "numberID": data.get('numberId'),
            "typeAnswer": data.get('typeAnswer'),
            "correctOptionContent": correct_content
        }

        return is_answer, next_step_id, parsed_dict

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None, None, {}

# --- Self-Test Mode ---
if __name__ == "__main__":
    # Input parameters
    my_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5ODhlM2Q2ZWE0ZGZkZTFkMGEiLCJ1c2VyTmFtZSI6ImdpYW5nbGgxOEBjM2x0ay5oYW5hbS5lZHUudm4iLCJpc1ZlcmlmaWVkIjpmYWxzZSwiR3JhZGVJZCI6IkMxMiIsIkRpc3BsYXlOYW1lIjoiTMOqIEjGsMahbmcgR2lhbmciLCJQcm92aW5jZUlkIjozNywiRGlzdHJpY3RJZCI6MTMzODQsIlNjaG9vbFllYXIiOjIwMjUsImNvZGVBcHAiOiJTQ0hPT0wiLCJwYXJ0bmVyIjoiT05MVVlFTiIsIlJvbGUiOiJTVFVERU5UIiwiQ3JlYXRlQnlTY2hvb2wiOjE3MTYsInByZW1pdW0iOmZhbHNlLCJjYW5DaGFuZ2VQYXNzd29yZCI6dHJ1ZSwibmVlZENoYW5nZVBhc3N3b3JkIjp0cnVlLCJFblNETG9naW4iOmZhbHNlLCJwYWNrYWdlcyI6WyJJRUxUUy1zY2hvb2wiLCJQUkVNSVVNLVNDSE9PTCJdLCJqdGkiOiI2ZTZjYzVkMS1kNzY5LTQ5MmMtYTY2My02Y2IyYTIwY2ZjNzciLCJpYXQiOjE3NjUwODE4NjAsIm5iZiI6MTc2NTA4MTg2MCwiZXhwIjoxNzY3NjczODYwLCJpc3MiOiJFRE1JQ1JPIiwiYXVkIjoiT05MVVlFTi5WTiJ9.ewsADwzmJeCavThoSx7sT-ZI_FRPRvL9LhFi8sdePHM" # Replace with full token
    my_payload = {
        "stepId": "69350b03e44d2e73f537685f",
        "problemId": "668760f51645fe7784a47794",
        "dataOptionId": [1],
        "textAnswer": "",
        "isSkip": False
    }

    print("Sending answer and parsing result...\n")
    status, next_id, details = send_answer(my_token, my_payload)

    if status is not None:
        print(f"Is Answer Correct: {status}")
        print(f"Next Step to follow: {next_id}")
        print("-" * 30)
        print("Parsed Data Dictionary:")
        print(json.dumps(details, indent=4, ensure_ascii=False))