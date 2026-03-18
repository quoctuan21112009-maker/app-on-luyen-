import csv
import os
from typing import Optional, Tuple, Dict


class StudentDatabase:
    """
    Robust CSV-backed student database.
    - Auto-detect delimiter (; or ,)
    - Handles UTF-8 BOM
    - Compatible with old calls (debug param supported)
    """

    REQUIRED_COLUMNS = ['STT', 'Họ và tên', 'Tài khoản', 'Mật khẩu']

    def __init__(self, csv_filepath: str, debug: bool = False):
        self.csv_filepath = os.path.abspath(csv_filepath)
        self.debug = debug
        self.students: Dict[int, dict] = {}
        self.last_stt: int = 0
        self._load_data()

    # ===============================
    # LOAD DATA
    # ===============================
    def _load_data(self):

        if not os.path.exists(self.csv_filepath):
            raise FileNotFoundError(
                f"CSV file not found at: {self.csv_filepath}"
            )

        if self.debug:
            print(f"[DEBUG] Loading CSV from: {self.csv_filepath}")

        with open(self.csv_filepath, 'r', encoding='utf-8-sig') as f:
            sample = f.read(2048)
            f.seek(0)

            # Detect delimiter
            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(sample, delimiters=";,")
                delimiter = dialect.delimiter
            except csv.Error:
                delimiter = ';'

            if self.debug:
                print(f"[DEBUG] Detected delimiter: '{delimiter}'")

            reader = csv.DictReader(f, delimiter=delimiter)

            # Clean header
            if reader.fieldnames:
                reader.fieldnames = [h.strip() for h in reader.fieldnames]

            self._validate_columns(reader.fieldnames)

            for row in reader:
                try:
                    stt = int(row.get('STT', 0))
                    if stt <= 0:
                        continue

                    self.students[stt] = row
                    self.last_stt = max(self.last_stt, stt)

                except ValueError:
                    continue

        if not self.students:
            raise ValueError("CSV loaded but contains no valid student entries.")

        if self.debug:
            print(f"[DEBUG] Loaded {len(self.students)} students.")
            print(f"[DEBUG] Last STT: {self.last_stt}")

    # ===============================
    # VALIDATE HEADERS
    # ===============================
    def _validate_columns(self, headers):

        if not headers:
            raise ValueError("CSV file has no headers.")

        missing = [col for col in self.REQUIRED_COLUMNS if col not in headers]
        if missing:
            raise ValueError(
                f"CSV missing required columns: {missing}\n"
                f"Found columns: {headers}"
            )

    # ===============================
    # PUBLIC METHODS
    # ===============================
    def get_last_stt(self) -> int:
        return self.last_stt

    def get_credentials(
        self,
        stt_count: int,
        debug: bool = False   # ✅ FIX: tương thích với code cũ
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:

        student = self.students.get(stt_count)
        if not student:
            if debug:
                print(f"[DEBUG] STT {stt_count} not found.")
            return (None, None, None)

        student_name = student.get('Họ và tên', '').strip()
        username = student.get('Tài khoản', '').strip()
        password = student.get('Mật khẩu', '').strip()

        is_wrong_pass = student.get('isWrongPass', 'FALSE').strip().upper()
        if is_wrong_pass == 'TRUE':
            if debug:
                print(f"[DEBUG] STT {stt_count} marked wrong password.")
            return (None, None, None)

        if not username or not password:
            if debug:
                print(f"[DEBUG] STT {stt_count} missing credentials.")
            return (None, None, None)

        if debug:
            print(f"[DEBUG] STT {stt_count} valid account found.")

        return (student_name, username, password)


# ==================================
# TEST BLOCK
# ==================================
if __name__ == "__main__":
    try:
        db = StudentDatabase('Acc-onluyen.csv', debug=True)

        print("-" * 40)
        print(f"Last STT: {db.get_last_stt()}")
        print(f"STT 1: {db.get_credentials(1, debug=True)}")
        print("-" * 40)

    except Exception as e:
        print(f"[FATAL ERROR] {e}")
