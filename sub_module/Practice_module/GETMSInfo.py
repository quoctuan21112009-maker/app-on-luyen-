import requests
import json
import datetime

BASE_URL = "https://api-elb.onluyen.vn/api/school-online/mission/missiondetail"

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://app.onluyen.vn/",
}

def _format_timestamp(timestamp: int) -> str:
    if timestamp == 0 or timestamp is None:
        return "N/A"
    try:
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%H:%M:%S - %d/%m/%y")
    except Exception:
        return "Invalid Time"

def fetch_data_and_parse(mission_id: str, token: str, write_to_file: bool = False, debug: bool = False, output_filename: str = None): # type: ignore
    url = f"{BASE_URL}/{mission_id}"
    request_headers = BASE_HEADERS.copy()
    request_headers["Authorization"] = f"Bearer {token}"
    
    if debug:
        print(f"-> Attempting to fetch data for ID '{mission_id}' from: {url}")
    
    try:
        response = requests.get(url, headers=request_headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        beautifed = json.dumps(data, indent=4, ensure_ascii=False)

        if debug:
            print("\n--- Successful API Response ---")
            print(beautifed[:1500] + "..." if len(beautifed) > 1500 else beautifed)

        # Checking root level for missionId based on your provided JSON structure
        if "missionId" in data:
            print(f"\nAPI Call Status: SUCCESS")
            print(f"MISSION TITLE: {data.get('title', 'N/A')}")
            
            # Extract root fields
            mission_id_val = data.get("missionId")
            total_progress = data.get("progress", 0.0)
            start_time_ts = data.get("startTime", 0)
            end_time_ts = data.get("endTime", 0)
            subject = data.get("classSubjectName", "N/A")

            STATUS_MAPPING = {1: "In Progress", 3: "Completed", 7: "Expired"}
            status_desc = STATUS_MAPPING.get(data.get("statusMission"), f"Unknown ({data.get('statusMission')})")

            # Print Summary Table
            KEY_WIDTH = 25
            SEP = "-" * 65
            print("\n--- Mission Summary ---")
            print(SEP)
            print(f"{'Mission ID:':<{KEY_WIDTH}} {mission_id_val}")
            print(f"{'Subject:':<{KEY_WIDTH}} {subject}")
            print(f"{'Status:':<{KEY_WIDTH}} {status_desc}")
            print(f"{'Total Progress:':<{KEY_WIDTH}} {total_progress}%")
            print(SEP)
            print(f"{'Start Time:':<{KEY_WIDTH}} {_format_timestamp(start_time_ts)}")
            print(f"{'End Time:':<{KEY_WIDTH}} {_format_timestamp(end_time_ts)}")
            print(SEP)

            # Parsing individual tasks from listProblem
            problems = data.get("listProblem", [])
            if problems:
                print("\n--- Task Breakdown ---")
                for idx, prob in enumerate(problems, 1):
                    p_name = prob.get("problemName", "Unnamed Task")
                    p_id = prob.get("problemId", "N/A") # Extracted problemID
                    p_prog = prob.get("process", 0.0)
                    is_done = "Done" if prob.get("isPass") else "Incomplete"
                    
                    print(f"{idx}. {p_name}")
                    print(f"   ID:       {p_id}") # Printing problemID
                    print(f"   Progress: {p_prog}% | Status: {is_done}")
                    print("-" * 30)

            if write_to_file:
                filename = output_filename if output_filename else f"mission_{mission_id_val}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(beautifed)
                print(f"\n[FILE WRITE] Raw JSON data written to {filename}")

            return beautifed
        else:
            print(f"API Call Status: FAILURE - Expected fields not found in root.")

    except Exception as e:
        print(f"\n--- ERROR ---")
        print(f"Details: {e}")
        
if __name__ == "__main__":
    ASSIGNMENT_ID = "6933d637951c8c3f7fb949d8"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5ODhlM2Q2ZWE0ZGZkZTFkMGEiLCJ1c2VyTmFtZSI6ImdpYW5nbGgxOEBjM2x0ay5oYW5hbS5lZHUudm4iLCJpc1ZlcmlmaWVkIjpmYWxzZSwiR3JhZGVJZCI6IkMxMiIsIkRpc3BsYXlOYW1lIjoiTMOqIEjGsMahbmcgR2lhbmciLCJQcm92aW5jZUlkIjozNywiRGlzdHJpY3RJZCI6MTMzODQsIlNjaG9vbFllYXIiOjIwMjUsImNvZGVBcHAiOiJTQ0hPT0wiLCJwYXJ0bmVyIjoiT05MVVlFTiIsIlJvbGUiOiJTVFVERU5UIiwiQ3JlYXRlQnlTY2hvb2wiOjE3MTYsInByZW1pdW0iOmZhbHNlLCJjYW5DaGFuZ2VQYXNzd29yZCI6dHJ1ZSwibmVlZENoYW5nZVBhc3N3b3JkIjp0cnVlLCJFblNETG9naW4iOmZhbHNlLCJwYWNrYWdlcyI6WyJJRUxUUy1zY2hvb2wiLCJQUkVNSVVNLVNDSE9PTCJdLCJqdGkiOiI2ZTZjYzVkMS1kNzY5LTQ5MmMtYTY2My02Y2IyYTIwY2ZjNzciLCJpYXQiOjE3NjUwODE4NjAsIm5iZiI6MTc2NTA4MTg2MCwiZXhwIjoxNzY3NjczODYwLCJpc3MiOiJFRE1JQ1JPIiwiYXVkIjoiT05MVVlFTi5WTiJ9.ewsADwzmJeCavThoSx7sT-ZI_FRPRvL9LhFi8sdePHM" # Use the valid token here
    fetch_data_and_parse(ASSIGNMENT_ID, TOKEN, debug=False)