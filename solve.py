import json
import re
import sys
import time
from typing import Dict, Any, List, Union
from sub_module.TIMESTAMPGen import generate_timestamp_sequence
from sub_module.utils import clean_content
from config import *

ANSWER_FILE = "Nguyễn Việt Anh-69513503cc19939a44efdd48-ANSWER.json"
QUESTION_FILE = "debug_solve_output.txt"

def debug_print(message: str, debug_mode: bool):
    if debug_mode:
        print(f"[DEBUG] {message}")

def solve_assignment(answer_data_str: str, question_data_str: str, debug_mode: bool = False) -> Dict[str, Union[List[Dict[str, Any]], str, int]]:
    debug_print(f"Debug mode is {'ON' if debug_mode else 'OFF'}.", debug_mode)
    if debug_mode:
        with open("debugwrite.txt","w",encoding = "utf8") as f:
            f.write(question_data_str)
    try:
        answer_data = json.loads(answer_data_str)
        question_data = json.loads(question_data_str)
    except json.JSONDecodeError:
        return {"listAnswer": [], "preSignedUrlAnswer": "ERROR", "timeServer": "ERROR"}

    top_level_data = question_data.get('data', {})
    pre_signed_url = top_level_data.get('preSignedUrlAnswer', 'N/A')
    time_server = top_level_data.get('timeServer', 'N/A')
    
    # 1. Build TWO maps: ID-based and Content-based
    answer_id_map = {}
    answer_content_map = {} 
    
    for item in answer_data.get('data', []):
        q_id = item.get('numberQuestion')
        type_answer = item.get('typeAnswer')
        content_list = item.get('content', [])
        
        # Clean the Question Text (data source)
        q_text_raw = item.get('content-dataStandard', '')
        q_text_cleaned = clean_content(q_text_raw)
        
        # Clean the Answer Option Content
        raw_answer = content_list[0] if content_list and type_answer != 1 else ''
        cleaned_answer = clean_content(raw_answer)
        
        data_payload = {
            'content': content_list,
            'cleaned_content': cleaned_answer,
            'type': type_answer,
            'original_id': q_id
        }
        
        if q_id is not None:
            answer_id_map[q_id] = data_payload
        if q_text_cleaned:
            answer_content_map[q_text_cleaned] = data_payload

    # 2. Match Questions
    submission_answers = []
    question_list = top_level_data.get('data', [])
    num_questions = len(question_list)
    
    timestamp_sequence = generate_timestamp_sequence(
        start=int(time_server) + 10 if str(time_server).isdigit() else int(time.time()),
        step=7, random_range=3, count=num_questions
    )
    ts_iter = iter(timestamp_sequence)

    option_match_misses = 0
    use_content_fallback = False

    for item in question_list:
        data_standard = item.get('dataStandard') or {}
        if not data_standard:
            data_material = item.get('dataMaterial', {})
            data_content = data_material.get('data', [])
            if data_content: data_standard = data_content[0]

        q_id = data_standard.get('numberQuestion')
        step_id = data_standard.get('stepId')
        q_text_cleaned = clean_content(data_standard.get('content', ''))

        # --- SELECTION LOGIC ---
        correct_answer_data = None
        
        # Try ID matching first unless fallback triggered
        if not use_content_fallback:
            correct_answer_data = answer_id_map.get(q_id)
        
        # Fallback to Content Map if ID-based match results in NO option match found later
        # OR if we have already triggered the global fallback flag
        if use_content_fallback or not correct_answer_data:
            correct_answer_data = answer_content_map.get(q_text_cleaned)

        if not correct_answer_data:
            continue
        #----
        flagidopt = True
        # --- OPTION MATCHING ---
        type_answer = correct_answer_data.get('type')
        submission_content = []
        submission_key = 'optionText'
        match_found = False
        debug_print(">"*5 + q_text_cleaned + ">"*5 ,debug_mode)
        
        if type_answer == 0:
            target_opt = correct_answer_data.get('cleaned_content')
            options = data_standard.get('options', [])
            optioniter = 0
            for opt in options:
                
                debug_print(f"Comparing ID:{int(opt.get('idOption'))}{clean_content(opt.get('content'))} to {target_opt}",debug_mode)
                if clean_content(opt.get('content')) == target_opt:
                    if flagidopt:
                        submission_content.append(optioniter)
                    else:
                        submission_content.append(int(opt.get('idOption')))
                    submission_key = 'optionId'
                    match_found = True
                    break
                optioniter += 1
    
            # CRITICAL FIX: If ID matched but NO OPTION matched, increment miss counter
            if not match_found and not use_content_fallback:
                option_match_misses += 1
                debug_print(f"QID {q_id} found but Option mismatch #{option_match_misses}. Looking for: {target_opt}", debug_mode)
                
                # Attempt immediate re-match via Content Map for this specific question
                correct_answer_data = answer_content_map.get(q_text_cleaned)
                if correct_answer_data:
                    target_opt = correct_answer_data.get('cleaned_content')
                    optioniter = 0
                    for opt in options:
                        debug_print(f"Comparingv2 {clean_content(opt.get('content'))} to {target_opt}",debug_mode)
                        if clean_content(opt.get('content')) == target_opt:
                            if flagidopt:
                                submission_content.append(optioniter)
                            else:
                                submission_content.append(int(opt.get('idOption')))
                            submission_key = 'optionId'
                            match_found = True
                            break
                        optioniter += 1

                if option_match_misses >= 3:
                    print("!!! 3 Option mismatches detected. Forcing Content-Based Matching for rest of session. !!!")
                    use_content_fallback = True

        elif type_answer == 1:
            submission_content = correct_answer_data.get('content')
            match_found = True
        elif type_answer == 5:
            submission_content = [correct_answer_data.get('content')[0]]
            match_found = True

        if match_found:
            submission_answers.append({
                submission_key: submission_content,
                'id': step_id,
                'isSkip': False,
                'studentDoRight': None,
                'timeUpdate': next(ts_iter, int(time.time()))
            })
        
        debug_print("<"*5,debug_mode)
            
    print("-------------------------------------------------------")
    print("Processing complete.")
    
    # 4. Return the final payload structure
    final_payload = {
        'listAnswer': submission_answers,
        'preSignedUrlAnswer': pre_signed_url,
        'timeServer': time_server
    }
    
    debug_print(f"\nFinal Submission Payload Structure: {json.dumps(final_payload, indent=2)}", debug_mode)
    
    return final_payload

if __name__ == "__main__":
    is_debug = '--debug' in sys.argv
    try:
        with open(ANSWER_FILE, 'r', encoding='utf-8') as f:
            answer_data_string = f.read()
            
        with open(QUESTION_FILE, 'r', encoding='utf-8') as f:
            question_data_string = f.read()
            
        result_payload = solve_assignment(answer_data_string, question_data_string, debug_mode=is_debug)
        
        if result_payload and result_payload.get('listAnswer'):
            print("\n--- Summary of Prepared Answers (Submission Format) ---")
            print(json.dumps(result_payload['listAnswer'], indent=2))
        elif result_payload:
            print("\n--- No answers were matched successfully. ---")
            
    except FileNotFoundError as e:
        print(f"Error: Could not find required file: {e.filename} to run standalone.")
    except Exception as e:
        print(f"An unexpected error occurred during standalone execution: {e}")
