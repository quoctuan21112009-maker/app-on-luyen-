
# Configuration for ONLUYEN-BATCH

# Data Paths
CSV_FILE_PATH = 'Acc-onluyen.csv'
ANSWER_FILE_PATTERN = '{student_name}-{logid}-ANSWER.json'
OUTPUT_JSON_PATTERN = '{student_name}-{logid}.json'

# Performance
DEFAULT_THREAD_COUNT = 5
DEBUG_MODE = False

# API Config
API_LOGIN_URL = "https://oauth.onluyen.vn/api/account/login"
API_HOMEWORK_LIST = "https://app.onluyen.vn/api/homework/list"
# Add other API endpoints as needed
