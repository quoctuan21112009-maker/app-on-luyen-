from studentdatabase import StudentDatabase
from sub_module.POSTLogin import *
from sub_module.Homework_module.GETHWListAll import *
from sub_module.Homework_module.GETHWQuestDoing import *
from sub_module.utils import *
from config import DEFAULT_THREAD_COUNT
import concurrent.futures
from typing import Optional, List, Tuple, Dict, Any

# Shared state for the full log ID discovery
discovered_full_logid: Optional[str] = None

def find_full_logid(all_assignments: List[Dict[str, Any]], partial_logid: str) -> Optional[str]:
    normalized_partial = partial_logid.lower()
    for assignment in all_assignments:
        log_id = assignment.get('logid')
        if log_id and normalized_partial in log_id.lower():
            return log_id
    return None

def check_single_student(stt: int, db: StudentDatabase, partial_logid: str, debug: bool) -> Tuple[int, str, Optional[str], Optional[str], bool]:
    """
    Checks a single student.
    Returns: (stt, name, token, status_code, is_done)
    status_code: 'DONE', 'NOT_DONE', 'LOGIN_FAILED', 'FETCH_FAILED', 'ID_NOT_FOUND', 'SKIP'
    """
    global discovered_full_logid
    
    name, username, password = db.get_credentials(stt, debug=debug)
    
    if not name or not username or not password:
        return (stt, "Unknown", None, 'SKIP', False)

    # 1. Login
    response = make_login_request(username, password, debug=debug)
    if not response:
        return (stt, name, None, 'LOGIN_FAILED', False)

    current_token = response.get('access_token')
    if not current_token:
         return (stt, name, None, 'LOGIN_FAILED', False)

    # 2. Fetch HW
    hw_list = fetch_homework_data(current_token)
    if not hw_list:
        return (stt, name, current_token, 'FETCH_FAILED', False)

    # 3. Check Status
    if hw_list.get('success') is True and isinstance(hw_list.get('data'), list):
        all_assignments = extract_detailed_summary(hw_list)
        
        # Try to discover full logid if not yet found
        local_full_logid = discovered_full_logid
        if not local_full_logid:
            found = find_full_logid(all_assignments, partial_logid)
            if found:
                discovered_full_logid = found
                local_full_logid = found
                print(f"[{stt}] DISCOVERED FULL LOGID: {local_full_logid}")
        
        target_logid = local_full_logid if local_full_logid else partial_logid
        
        # If we still rely on partial matching and haven't confirmed full ID, we might risk false negatives
        # But for now we proceed.
        
        if check_assignment_availability(all_assignments, target_logid, "Done"):
            return (stt, name, current_token, 'DONE', True)
        else:
             return (stt, name, current_token, 'NOT_DONE', False)

    return (stt, name, current_token, 'FETCH_FAILED', False)


def check_if_anyone_did_hw(db: StudentDatabase, partial_logid: str, debug: bool = False) -> Tuple[str, List[Tuple[str, str]], List[Tuple[str, Optional[str]]]]:
    global discovered_full_logid
    discovered_full_logid = None # Reset for new run
    
    students_done: List[Tuple[str, str]] = []
    students_not_done: List[Tuple[str, Optional[str]]] = []
    
    last_stt = db.get_last_stt()
    if last_stt == 0:
        return (partial_logid, [], [])

    print(f"Starting check for {last_stt} students with {DEFAULT_THREAD_COUNT} threads...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=DEFAULT_THREAD_COUNT) as executor:
        # Create futures
        futures = {executor.submit(check_single_student, stt, db, partial_logid, debug): stt for stt in range(1, last_stt + 1)}
        
        for future in concurrent.futures.as_completed(futures):
            stt = futures[future]
            try:
                result_stt, name, token, status, is_done = future.result()
                
                if status == 'SKIP':
                    continue
                
                if is_done:
                    print(f"[STT {stt}] {name}: DONE")
                    students_done.append((name, token)) # type: ignore
                else:
                    if status == 'NOT_DONE':
                         print(f"[STT {stt}] {name}: NOT DONE")
                    else:
                         print(f"[STT {stt}] {name}: {status}")
                    students_not_done.append((name, token))

            except Exception as e:
                print(f"Exception checking STT {stt}: {e}")

    final_logid = discovered_full_logid if discovered_full_logid else partial_logid
    
    # Sort results by name for consistency, or keep them random. 
    # Usually user might want them sorted by STT, but we lost that order.
    # We can try to sort if we kept STT in the list, but the return signature only asks for name/token.
    
    return (final_logid, students_done, students_not_done)