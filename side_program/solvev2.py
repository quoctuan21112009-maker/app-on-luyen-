import json
import time
# Import functions from your provided files
from sub_module.Practice_module.GETStartPractice import get_step_id
from sub_module.Practice_module.GETPracticeQuestDetails import get_question_details
from sub_module.Practice_module.POSTAnswer import send_answer
from solve import clean_content

def run_practice_session(practice_id, bearer_token, db_file="final_results.json"):
    # 1. Start session
    current_step_id = get_step_id(practice_id, bearer_token)
    
    if not current_step_id or "Error" in current_step_id:
        return

    # 2. Load database and create mapping for both ID and Text Content
    with open(db_file, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    
    # Map for QID -> Answer
    id_map = {item['numberQuestion']: item for item in db_data['data']}
    
    # NEW: Map for Question Text -> Answer (Fallback)
    content_map = {clean_content(item['content-dataStandard']): item for item in db_data['data']}
    
    while current_step_id:
        # A. Fetch details (returns numberQuestion, typeAnswer, and options)
        q_num, q_type, options = get_question_details(practice_id, current_step_id, bearer_token)
        
        # B. Get standard data from live API (simulated based on details return)
        # Assuming you can access the raw live question text here to compare
        live_question_text = "" # This would come from the full dataStandard response
        
        # 3. MATCHING LOGIC
        target_entry = id_map.get(q_num) # Primary match by ID
        
        if not target_entry:
            # FALLBACK: Match by cleaning and comparing question text
            target_entry = content_map.get(clean_content(live_question_text))
            
        if not target_entry:
            print(f"Match failed for {q_num}. Question content did not match database.")
            break

        target_answer = clean_content(target_entry['content'][0])

        # C. Compare options and build payload
        payload = {
            "stepId": current_step_id,
            "problemId": practice_id,
            "isSkip": False,
            "textAnswer": ""
        }

        if q_type == 0: # Multiple Choice
            for opt in options:
                if clean_content(opt['content']) == target_answer:
                    payload["dataOptionId"] = [opt['idOption']]
                    break
        
        # D. Submit
        status, next_id, result_details = send_answer(bearer_token, payload)
        current_step_id = next_id if status else None

if __name__ == "__main__":
    run_practice_session("668760f51645fe7784a47794", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc0dvZE1vZGUiOmZhbHNlLCJ1c2VySWQiOiI2NmU3ZDc5ODhlM2Q2ZWE0ZGZkZTFkMDgiLCJ1c2VyTmFtZSI6ImRhbmduZGg0MkBjM2x0ay5oYW5hbS5lZHUudm4iLCJpc1ZlcmlmaWVkIjpmYWxzZSwiR3JhZGVJZCI6IkMxMiIsIkRpc3BsYXlOYW1lIjoiTmd1eeG7hW4gRHV5IEjhuqNpIMSQxINuZyIsIlByb3ZpbmNlSWQiOjM3LCJEaXN0cmljdElkIjoxMzM4NCwiU2Nob29sWWVhciI6MjAyNSwiY29kZUFwcCI6IlNDSE9PTCIsInBhcnRuZXIiOiJPTkxVWUVOIiwiUm9sZSI6IlNUVURFTlQiLCJDcmVhdGVCeVNjaG9vbCI6MTcxNiwicHJlbWl1bSI6ZmFsc2UsImNhbkNoYW5nZVBhc3N3b3JkIjp0cnVlLCJuZWVkQ2hhbmdlUGFzc3dvcmQiOnRydWUsIkVuU0RMb2dpbiI6ZmFsc2UsInBhY2thZ2VzIjpbIlBSRU1JVU0tU0NIT09MIiwiSUVMVFMtc2Nob29sIl0sImp0aSI6IjdkNzZkZjIzLWU5NTctNGZhMy04NTE3LTUyZGEyMWM5YjgyOCIsImlhdCI6MTc2NTA4ODMxNywibmJmIjoxNzY1MDg4MzE3LCJleHAiOjE3Njc2ODAzMTcsImlzcyI6IkVETUlDUk8iLCJhdWQiOiJPTkxVWUVOLlZOIn0.3pHPaAo-P4m6rQ-CsRKYGUN4qvWxRDQvL6Tyrqsgqbg")