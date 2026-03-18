import json
import time
from GETPracticeSpecificInfo import get_practice_info
from GETStartPractice import get_step_id
from POSTAnswer import send_answer

def run_sync_practice(token, practice_id, output_file=None):
    """
    Combines info retrieval, initialization, and answer crawling into one JSON result.
    """
    # 1. Fetch Practice Title and Metadata
    info = get_practice_info(practice_id, token)
    title = info.get("title", "Untitled Collection")
    knowledge_id = info.get("knowledgeId", practice_id)

    results_data = []
    
    # 2. Get the starting step ID
    current_step = get_step_id(practice_id, token)
    
    step_idx = 0
    while current_step and isinstance(current_step, str) and "Error" not in current_step:
        # Dummy payload picking index 0 to force the server to reveal the correct answer
        payload = {
            "stepId": current_step,
            "problemId": practice_id,
            "dataOptionId": [0],
            "textAnswer": "",
            "isSkip": False
        }

        # 3. Send dummy answer and parse the correct result
        _, next_id, details = send_answer(token, payload)
        
        if details:
            # Reconstruct the entry structure from your example ANSWER.json
            results_data.append({
                "stepIndex": step_idx,
                "content-dataStandard": details.get("content-dataStandard"),
                "numberQuestion": details.get("numberID"),
                "typeAnswer": details.get("typeAnswer"),
                "content": [details.get("correctOptionContent")]
            })
        
        current_step = next_id
        step_idx += 1
        time.sleep(0.3)  # Anti-throttle delay

    # 4. Final Data Assembly matching the requested structure
    final_dict = {
        "assignId": knowledge_id,
        "name": title,
        "data": results_data
    }

    json_str = json.dumps(final_dict, ensure_ascii=False, indent=4)

    # 5. Write to file only if path provided
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(json_str)
    
    return json_str

# --- Example of calling the function ---
if __name__ == "__main__":
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5NThlM2Q2ZWE0ZGZkZTFjZTYiLCJ1c2VyTmFtZSI6InRhbW50OTZAYzNsdGsuaGFuYW0uZWR1LnZuIiwiaXNWZXJpZmllZCI6ZmFsc2UsIkdyYWRlSWQiOiJDMTIiLCJEaXNwbGF5TmFtZSI6Ik5ndXnhu4VuIFRyw60gVMOibSIsIlByb3ZpbmNlSWQiOjM3LCJEaXN0cmljdElkIjoxMzM4NCwiU2Nob29sWWVhciI6MjAyNSwiY29kZUFwcCI6IlNDSE9PTCIsInBhcnRuZXIiOiJPTkxVWUVOIiwiUm9sZSI6IlNUVURFTlQiLCJDcmVhdGVCeVNjaG9vbCI6MTcxNiwicHJlbWl1bSI6ZmFsc2UsImNhbkNoYW5nZVBhc3N3b3JkIjp0cnVlLCJuZWVkQ2hhbmdlUGFzc3dvcmQiOnRydWUsIkVuU0RMb2dpbiI6ZmFsc2UsInBhY2thZ2VzIjpbIklFTFRTLXNjaG9vbCIsIlBSRU1JVU0tU0NIT09MIl0sImp0aSI6ImY2MzM5ZjcyLTgxNjAtNDU3ZS1hMTcxLTk5MWJhMmNkMWI1YiIsImlhdCI6MTc2NTExNjg4NywibmJmIjoxNzY1MTE2ODg3LCJleHAiOjE3Njc3MDg4ODcsImlzcyI6IkVETUlDUk8iLCJhdWQiOiJPTkxVWUVOLlZOIn0.hSytAQggEZWaKxUsXdXjL8M00piUqr8QYqy89tjX5Ow"
    P_ID1 = "668760ef1645fe7784a47792"
    P_ID2 = "668760f51645fe7784a47794"
    
    run_sync_practice(TOKEN, P_ID1)
    run_sync_practice(TOKEN, P_ID1)
    run_sync_practice(TOKEN, P_ID2)
    run_sync_practice(TOKEN, P_ID2)
    print("done")