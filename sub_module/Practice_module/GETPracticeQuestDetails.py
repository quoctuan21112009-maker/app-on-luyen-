import requests

def get_question_details(problem_id, question_id, bearer_token):
    """
    Fetches details and parses specific fields: questionNumber, typeAnswer, and options.
    """
    url = f"https://api-elb.onluyen.vn/api/practice/questions/detail/{problem_id}/{question_id}"
    
    session = requests.Session()
    headers = {
        "authority": "api-elb.onluyen.vn",
        "authorization": f"Bearer {bearer_token}",
        "code-app": "SCHOOL",
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        full_json = response.json()

        # Parsing the specific structure provided
        data = full_json.get("dataStandard", {})
        
        q_number = data.get("questionNumber")
        q_type = data.get("typeAnswer")
        q_options = data.get("options", [])
        q_content= data.get("question", "")

        return q_number, q_type, q_options, q_content

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None, None, None, None

if __name__ == "__main__":
    # Test Data
    PID = "668760f51645fe7784a47794"
    QID = "69350b03e44d2e73f537685f"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5ODhlM2Q2ZWE0ZGZkZTFkMDgiLCJ1c2VyTmFtZSI6ImRhbmduZGg0MkBjM2x0ay5oYW5hbS5lZHUudm4iLCJpc1ZlcmlmaWVkIjpmYWxzZSwiR3JhZGVJZCI6IkMxMiIsIkRpc3BsYXlOYW1lIjoiTmd1eeG7hW4gRHV5IEjhuqNpIMSQxINuZyIsIlByb3ZpbmNlSWQiOjM3LCJEaXN0cmljdElkIjoxMzM4NCwiU2Nob29sWWVhciI6MjAyNSwiY29kZUFwcCI6IlNDSE9PTCIsInBhcnRuZXIiOiJPTkxVWUVOIiwiUm9sZSI6IlNUVURFTlQiLCJDcmVhdGVCeVNjaG9vbCI6MTcxNiwicHJlbWl1bSI6ZmFsc2UsImNhbkNoYW5nZVBhc3N3b3JkIjp0cnVlLCJuZWVkQ2hhbmdlUGFzc3dvcmQiOnRydWUsIkVuU0RMb2dpbiI6ZmFsc2UsInBhY2thZ2VzIjpbIlBSRU1JVU0tU0NIT09MIiwiSUVMVFMtc2Nob29sIl0sImp0aSI6IjdkNzZkZjIzLWU5NTctNGZhMy04NTE3LTUyZGEyMWM5YjgyOCIsImlhdCI6MTc2NTA4ODMxNywibmJmIjoxNzY1MDg4MzE3LCJleHAiOjE3Njc2ODAzMTcsImlzcyI6IkVETUlDUk8iLCJhdWQiOiJPTkxVWUVOLlZOIn0.3pHPaAo-P4m6rQ-CsRKYGUN4qvWxRDQvL6Tyrqsgqbg" # Use your actual full token here

    q_num, q_type, options, q_name = get_question_details(PID, QID, TOKEN)

    if q_num is not None:
        print(f"--- Question Data ---")
        print(f"Question Number: {q_num}")
        print(f"Type Answer:     {q_type}")
        print(f"Options Count:   {len(options)}") # type: ignore
        print("\nOptions Detail:")
        for opt in options: # type: ignore
            # Cleaning simple HTML tags for cleaner terminal output
            clean_name = opt['name'].replace("<p>", "").replace("</p>", "")
            is_correct = "[CORRECT]" if opt['isAnswer'] else ""
            print(f" - ID {opt['id']}: {clean_name} {is_correct}")
    else:
        print("Failed to retrieve or parse data.")