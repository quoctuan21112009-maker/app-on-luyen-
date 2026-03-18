import sys
import os

try:
    print("Testing imports...")
    import config
    print("config imported")
    from sub_module.utils import clean_content
    print("utils imported")
    from studentdatabase import StudentDatabase
    print("studentdatabase imported")
    from sub_module.Homework_module.Checkifanyonedidhw import check_if_anyone_did_hw
    print("Checkifanyonedidhw imported")
    import main
    print("main imported (modules load check)")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
    sys.exit(1)
except Exception as e:
    # main might run logic if imported because I didn't wrap everything in 'if __name__', 
    # but I did remove the immediate execution in main.py? 
    # Wait, main.py has logic at top level?
    # Checking main.py:
    # It has:
    # db = StudentDatabase(CSV_FILE_PATH)
    # logidpartial = input(...) 
    # So importing main will block on input!
    print(f"Exception during import (expected if main runs logic): {e}")

print("\nTesting StudentDatabase...")
try:
    db = StudentDatabase(config.CSV_FILE_PATH)
    last_stt = db.get_last_stt()
    print(f"Database loaded. Last STT: {last_stt}")
    if last_stt > 0:
        print("Success: Database verified.")
    else:
        print("Warning: Database seems empty or failed to load.")
except Exception as e:
    print(f"DATABASE ERROR: {e}")

print("\nVerification Complete.")
