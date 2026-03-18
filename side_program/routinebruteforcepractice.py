from studentdatabase import *
from sub_module.POSTLogin import *
from sub_module.Practice_module.MakeAnsDOC import *
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

    print(f"STT {stt}: Login successful. BruteForce practice...")
    token = respone['access_token'] # type: ignore
    P_ID1 = "668760ef1645fe7784a47792"
    P_ID2 = "668760f51645fe7784a47794"
    
    run_sync_practice(token, P_ID1)
    run_sync_practice(token, P_ID1)
    run_sync_practice(token, P_ID2)
    run_sync_practice(token, P_ID2)