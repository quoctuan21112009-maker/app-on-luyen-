import sys
from sub_module.Homework_module.Checkifanyonedidhw import *
from sub_module.Homework_module.GETHWSpecificInfo import *
from sub_module.Homework_module.POSTStartHW import *
from sub_module.Homework_module.PUTAnswers import *
from sub_module.Homework_module.convertREFtoANSDOC import *
import json
from solve import *
import time
from config import *
from studentdatabase import StudentDatabase
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

class Logger(object):
    def __init__(self, filename='latest.log'):
        self.terminal = sys.stdout
        self.input_method = input # Store original input
        self.log = open(filename, "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

def process_student_task(student, logid, answer_json, debug_mode):
    """
    Process a single student: start assignment, get data, solve, submit.
    """
    try:
        start_time = time.perf_counter()
        print('*'*10 + f"Solving for {student[0]}" + '*'*10)
        
        start_assignment_request(logid, student[1], debug_mode) 
        exam_data = get_assignment_data(student[1], logid) 
        
        datautf = json.dumps(exam_data, indent=4, ensure_ascii=True)
        
        ready_to_push = solve_assignment(answer_json, datautf, debug_mode)
        
        push_result = submit_assignment(ready_to_push["preSignedUrlAnswer"], ready_to_push["listAnswer"]) 
        
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print("+"*20)
        print(f"Elapsed time solving for {student[0]}: {elapsed_time:.4f} seconds")
        print("-"*20)
        return student[0], elapsed_time
    except Exception as e:
        print(f"Error processing student {student[0]}: {e}")
        return student[0], None

def main():
    # Argument Parser
    parser = argparse.ArgumentParser(description="Run the ONLUYEN-BATCH process.")
    parser.add_argument('--debug', '-d', action='store_true', help="Enable debug mode")
    args = parser.parse_args()
    
    # Override Global DEBUG_MODE with Argument
    current_debug_mode = args.debug if args.debug else DEBUG_MODE

    # Setup Logging
    sys.stdout = Logger()
    # sys.stderr = sys.stdout # Create one stream for both

    try:
        # Initialize Database once
        db = StudentDatabase(CSV_FILE_PATH)

        #START
        #1:GET LOGID + CSV
        try:
            # Since we redirected stdout, the prompt from input() might go to the original stdout 
            # or the new one depending on implementation. 
            # Python's input() writes to sys.stdout.
            logidpartial = input("Please input the logid of the test(the scrambled string in searchbar, partial OK):")
            # Log the input itself
            print(logidpartial) # Echo input to log
        except EOFError:
            print("Input stream closed.")
            return

        #2:check_if_did_hw
        # Pass the db instance instead of file path
        start_time1 = time.perf_counter()
        logid, students_done, students_not_done = check_if_anyone_did_hw(db, logidpartial, current_debug_mode)
        end_time1 = time.perf_counter()
        elapsed = - start_time1 + end_time1
        print(f"Elapsed time for login {elapsed:.4f}")
        #3.1:chose 1 student done
        if not students_done:
            print("NO REF STUDENT CAN BE FOUND")
            
            sys.exit(1)
        if not students_not_done:
            print("ALL STUDENT DID HW")
            sys.exit(0)

        refs_student = students_done[0]

        print(f'REF FOUND:{refs_student[0]}')
        rawresp=fetch_data_and_parse(logid, refs_student[1], True, current_debug_mode, OUTPUT_JSON_PATTERN.format(student_name=refs_student[0], logid=logid))
        print(f"{len(students_done)} student did homework and {len(students_not_done)} didn't")

        if rawresp == None:
            raise ValueError("FETCHING ANSWER FAILED")

        answer_json = convert_assignment_json_to_json(rawresp)

        # Save answer file
        answer_filename = ANSWER_FILE_PATTERN.format(student_name=refs_student[0], logid=logid)
        with open(answer_filename,'w', encoding = 'utf8') as f:
            f.write(str(answer_json))
        end_time12 = time.perf_counter()
        elapsed_time1 = end_time12 - start_time1
        print("-"*20)
        print(f"Elapsed time fetching answer: {elapsed_time1:.4f} seconds")
        print("-"*20)
        print('-'*10 + 'ANSWER JSON MADE' + '-'*10)

        confirm = input("Continue?YN")
        print(confirm) # Echo input
        if confirm.upper() != "Y":
            sys.exit(0)

        print(f"Start copying with {DEFAULT_THREAD_COUNT} threads")
        start_time2 = time.perf_counter()
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=DEFAULT_THREAD_COUNT) as executor:
            # Submit all tasks
            future_to_student = {
                executor.submit(process_student_task, student, logid, answer_json, current_debug_mode): student 
                for student in students_not_done
            }
            
            # Wait for all tasks to complete
            for future in as_completed(future_to_student):
                student_name, elapsed = future.result()
                # Results are already printed in the task function
                
        end_time2 = time.perf_counter()
        elapsed_time2 = end_time2 - start_time2
        print("-"*20)
        print(f"Elapsed time copying: {elapsed_time2:.4f} seconds")
        print("-"*20)
        print("-"*20)
        print(f"Total elapsed time: {elapsed_time2 + elapsed_time1:.4f} seconds")
        print("-"*20)
    finally:
        if isinstance(sys.stdout, Logger):
            sys.stdout.close()

if __name__ == "__main__":
    main()
