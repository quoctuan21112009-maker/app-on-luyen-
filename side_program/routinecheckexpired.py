from studentdatabase import *
from sub_module.POSTLogin import *
from sub_module.Homework_module.GETHWListAll import *
from sub_module.Homework_module.GETHWQuestDoing import *
debug = True
FILE_PATH = 'Acc-onluyen.csv'

laststudent= get_last_stt(FILE_PATH)
if laststudent == None:
    raise ValueError("Could not determine the last student STT.")
for stt in range(1, laststudent +1):
    name, username, password = get_credentials(FILE_PATH, stt)
    if name == None or username == None or password == None:
        print(f"STT {stt}: Skipping due to invalid account or not found.\n")
        continue

    print(f"STT {stt}: Attempting login for user '{username}'...")
    respone = make_login_request(username, password, debug=debug)
    if respone is None:
        print(f"STT {stt}: Login failed for user '{username}'.\n")
        continue

    print(f"STT {stt}: Login successful. Fetching homework list...")
    hw_list = fetch_mission_data(respone['access_token']) # type: ignore
    if hw_list is None:
        print(f"STT {stt}: Failed to fetch homework list.\n")
        continue

    if hw_list and hw_list.get('success') is True and isinstance(hw_list.get('data'), list):
        
        # 1. Extract all assignments
        all_assignments = extract_detailed_summary(hw_list)
        
        # 2. Define the target status for filtering
    # 0: "Waiting",
    # 1: "Doing",
    # 2: "Grading",
    # 3: "Done",
    # 7: "Expired"
        target_status = "Doing"
        print(f"Filtering assignments for status: '{target_status}'")
        
        # 3. Filter the assignments
        filtered_assignments = filter_assignments_by_status(all_assignments, target_status)
        
        # 4. Print the filtered table
        print_assignment_table(filtered_assignments)

    # print(f"STT {stt}: Homework list fetched. Processing assignments...")
    # for assignment in hw_list.get('data', []):
    #     assignment_id = assignment.get('id')
    #     if assignment_id:
    #         print(f"STT {stt}: Fetching details for assignment ID '{assignment_id}'...")
    #         assignment_data = get_assignment_data(token, assignment_id) # type: ignore
    #         if assignment_data:
    #             print(f"STT {stt}: Successfully fetched data for assignment ID '{assignment_id}'.\n")
    #         else:
    #             print(f"STT {stt}: Failed to fetch data for assignment ID '{assignment_id}'.\n")
    #     else:
    #         print(f"STT {stt}: Assignment ID not found in the homework list.\n")