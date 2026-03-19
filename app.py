from flask import Flask, render_template, request, jsonify, Response, redirect
import csv
import os
import subprocess
import sys
import json
from datetime import datetime
from config import CSV_FILE_PATH
from sub_module.utils import remove_accents

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


# ─── redirect gốc thẳng vào homework ──────────────────────────────────────────
@app.route('/')
def index():
    return redirect('/homework')


@app.route('/homework')
def homework():
    return render_template('homework.html')


# ─── CSV helpers (giữ nguyên để /get-accounts còn hoạt động) ──────────────────
def ensure_csv_exists():
    try:
        if not os.path.exists(CSV_FILE_PATH):
            print(f"[INFO] Creating new CSV at {CSV_FILE_PATH}")
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['STT', 'Mã học sinh', 'Họ và tên', 'Lớp', 'Tài khoản', 'Mật khẩu', 'Mã đăng nhập cho PH', 'isWrongPass', ''])
        else:
            try:
                with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
                    first_line = f.readline().rstrip('\n')
                    if '; ' in first_line or ' ;' in first_line:
                        f.seek(0)
                        lines = f.readlines()
                        fixed_header = first_line.replace('; ', ';').replace(' ;', ';')
                        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as fw:
                            fw.write(fixed_header + '\n')
                            fw.writelines(lines[1:])
                        print("[INFO] Fixed CSV header format")
            except Exception as e:
                print(f"[WARNING] Could not fix CSV header: {e}")
    except Exception as e:
        print(f"[ERROR] ensure_csv_exists failed: {e}")


def get_next_stt():
    ensure_csv_exists()
    max_stt = 0
    try:
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)
            for row in reader:
                if row and row[0].strip().isdigit():
                    max_stt = max(max_stt, int(row[0].strip()))
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return max_stt + 1


def _clean_row(row):
    """Strip keys/values, handle list values from DictReader."""
    cleaned = {}
    for k, v in row.items():
        key = k.strip() if k else ''
        if isinstance(v, list):
            val = v[0].strip() if v and v[0] else ''
        else:
            val = v.strip() if v else ''
        cleaned[key] = val
    return cleaned


# ─── API: lấy danh sách tài khoản cho <select> ────────────────────────────────
@app.route('/get-accounts', methods=['GET'])
def get_accounts():
    try:
        ensure_csv_exists()
        accounts = []
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if not row:
                    continue
                r = _clean_row(row)
                email = r.get('Tài khoản', '')
                if email:
                    accounts.append({'name': r.get('Họ và tên', ''), 'email': email})
        return jsonify({'success': True, 'accounts': accounts}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500


# ─── API: chạy main.py ────────────────────────────────────────────────────────
@app.route('/run', methods=['POST'])
def run_main():
    try:
        data     = request.json
        logid    = data.get('logid', '').strip()
        taikhoan = data.get('taikhoan', '').strip()

        if not logid:
            return jsonify({'success': False, 'message': 'Vui lòng nhập ID bài'}), 400
        if not taikhoan:
            return jsonify({'success': False, 'message': 'Vui lòng chọn tài khoản'}), 400

        print(f"[LOG] Chạy bài cho: {taikhoan} | logid: {logid}")

        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        process = subprocess.Popen(
            [sys.executable, 'main.py', '--logid', logid, '--account', taikhoan],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=False,
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        output_bytes, _ = process.communicate(timeout=600)
        returncode = process.returncode

        output = ''
        for enc in ['utf-8', 'cp1252', 'latin-1']:
            try:
                output = output_bytes.decode(enc)
                break
            except (UnicodeDecodeError, AttributeError):
                continue
        if not output:
            output = output_bytes.decode('utf-8', errors='replace')

        log_content = ''
        if os.path.exists('latest.log'):
            try:
                with open('latest.log', 'r', encoding='utf-8', errors='replace') as f:
                    log_content = f.read()
            except Exception:
                pass

        success = returncode == 0
        return jsonify({
            'success': success,
            'status': '✓ Thành công' if success else '✗ Lỗi',
            'message': output,
            'log_file': log_content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200

    except subprocess.TimeoutExpired:
        process.kill()
        return jsonify({'success': False, 'message': 'Timeout: Chương trình chạy quá lâu'}), 500
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500


if __name__ == '__main__':
    ensure_csv_exists()
    print("=" * 50)
    print("Flask App đang chạy tại http://localhost:5000/homework")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
