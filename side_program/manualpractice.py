import json
from sub_module.Practice_module.GETStartPractice import get_step_id
from sub_module.Practice_module.GETPracticeSpecificInfo    import get_practice_info
from sub_module.Practice_module.GETPracticeQuestDetails import get_question_details
from sub_module.Practice_module.POSTAnswer import send_answer
from solve import clean_content

def run_manual_practice(practice_id, bearer_token):
    # 1. Start session
    current_step_id = get_step_id(practice_id, bearer_token)
    #current_step_id = get_practice_info(practice_id, bearer_token).get("stepId")
    if not current_step_id or "Error" in current_step_id:
        print("Failed to initialize practice session.")
        return

    while current_step_id:
        # A. Fetch question details
        q_num, q_type, options, q_content = get_question_details(practice_id, current_step_id, bearer_token)
        
        print("\n" + "="*50)
        print(f"QUESTION: {q_content};")
        # print("="*50)
        
        # Display Options and create index mapping
        option_map = {}
        for idx, opt in enumerate(options): # type: ignore
            label = chr(65 + idx) # A, B, C, D...
            option_map[label] = opt['id']
            option_map[str(idx)] = opt['id']
            
            print(f"[{label}] {clean_content(opt['name'])}")
        print("ANSWER ONLY")
        # B. Get User Answer
        user_choice = input("\nEnter your answer (A, B, C, D or 0, 1, 2, 3): ").strip().upper()

        if user_choice not in option_map:
            print("Invalid input. Exiting...")
            break

        # C. Build payload
        payload = {
            "stepId": current_step_id,
            "problemId": practice_id,
            "isSkip": False,
            "textAnswer": "",
            "dataOptionId": [option_map[user_choice]]
        }

        # D. Submit Answer
        print("Submitting answer...")
        status, next_id, result_details = send_answer(bearer_token, payload)
        
        if status:
            print("Correct!")
            current_step_id = next_id
            # print(json.dumps(result_details, indent=4, ensure_ascii=False))
        else:
            print("Error submitting answer.")

    print("\nSession finished.")

if __name__ == "__main__":
    PRACTICE_ID = "668760f51645fe7784a47794"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5NThlM2Q2ZWE0ZGZkZTFjZTYiLCJ1c2VyTmFtZSI6InRhbW50OTZAYzNsdGsuaGFuYW0uZWR1LnZuIiwiaXNWZXJpZmllZCI6ZmFsc2UsIkdyYWRlSWQiOiJDMTIiLCJEaXNwbGF5TmFtZSI6Ik5ndXnhu4VuIFRyw60gVMOibSIsIlByb3ZpbmNlSWQiOjM3LCJEaXN0cmljdElkIjoxMzM4NCwiU2Nob29sWWVhciI6MjAyNSwiY29kZUFwcCI6IlNDSE9PTCIsInBhcnRuZXIiOiJPTkxVWUVOIiwiUm9sZSI6IlNUVURFTlQiLCJDcmVhdGVCeVNjaG9vbCI6MTcxNiwicHJlbWl1bSI6ZmFsc2UsImNhbkNoYW5nZVBhc3N3b3JkIjp0cnVlLCJuZWVkQ2hhbmdlUGFzc3dvcmQiOnRydWUsIkVuU0RMb2dpbiI6ZmFsc2UsInBhY2thZ2VzIjpbIklFTFRTLXNjaG9vbCIsIlBSRU1JVU0tU0NIT09MIl0sImp0aSI6ImY2MzM5ZjcyLTgxNjAtNDU3ZS1hMTcxLTk5MWJhMmNkMWI1YiIsImlhdCI6MTc2NTExNjg4NywibmJmIjoxNzY1MTE2ODg3LCJleHAiOjE3Njc3MDg4ODcsImlzcyI6IkVETUlDUk8iLCJhdWQiOiJPTkxVWUVOLlZOIn0.hSytAQggEZWaKxUsXdXjL8M00piUqr8QYqy89tjX5Ow"
    run_manual_practice(PRACTICE_ID, TOKEN)