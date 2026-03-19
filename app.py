from flask import Flask, render_template, request, jsonify, Response
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

# Ensure CSV file exists with headers
def ensure_csv_exists():
    try:
        if not os.path.exists(CSV_FILE_PATH):
            print(f"[INFO] Creating new CSV at {CSV_FILE_PATH}")
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['STT', 'Mã học sinh', 'Họ và tên', 'Lớp', 'Tài khoản', 'Mật khẩu', 'Mã đăng nhập cho PH', 'isWrongPass', ''])
        else:
            # Fix headers if they have spaces after delimiter
            try:
                with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
                    first_line = f.readline().rstrip('\n')
                    # Check if header has spaces
                    if '; ' in first_line or ' ;' in first_line:
                        # Read all content
                        f.seek(0)
                        lines = f.readlines()
                        
                        # Fix header - remove spaces around delimiter
                        fixed_header = first_line.replace('; ', ';').replace(' ;', ';')
                        
                        # Write back
                        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as fw:
                            fw.write(fixed_header + '\n')
                            fw.writelines(lines[1:])
                        print("[INFO] Fixed CSV header format")
            except Exception as e:
                print(f"[WARNING] Could not fix CSV header: {e}")
    except Exception as e:
        print(f"[ERROR] ensure_csv_exists failed: {e}")

# Get the next STT number
def get_next_stt():
    ensure_csv_exists()
    max_stt = 0
    try:
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # Skip header
            for row in reader:
                if row and row[0].strip().isdigit():
                    max_stt = max(max_stt, int(row[0].strip()))
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return max_stt + 1

@app.route('/')
def login():
    """Trang đăng nhập - nhập tên, lớp, tài khoản, mật khẩu"""
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    """Lưu thông tin vào Acc-onluyen.csv"""
    try:
        data = request.json
        ten = data.get('ten', '').strip()
        lop = data.get('lop', '').strip()
        taikhoan = data.get('taikhoan', '').strip()
        matkhau = data.get('matkhau', '').strip()

        if not all([ten, lop, taikhoan, matkhau]):
            return jsonify({'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin'}), 400

        # Remove Vietnamese accents from name
        ten = remove_accents(ten)

        ensure_csv_exists()
        next_stt = get_next_stt()

        # Append new row to CSV
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                next_stt,           # STT
                '',                 # Mã học sinh (để trống)
                ten,                # Họ và tên
                lop,                # Lớp
                taikhoan,           # Tài khoản
                matkhau,            # Mật khẩu
                '',                 # Mã đăng nhập cho PH
                '',                 # isWrongPass
                ''                  # Cột cuối
            ])

        return jsonify({
            'success': True, 
            'message': f'Đăng ký thành công cho {ten}',
            'stt': next_stt
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/homework')
def homework():
    """Trang nhập ID bài"""
    return render_template('homework.html')

@app.route('/get-accounts', methods=['GET'])
def get_accounts():
    """Lấy danh sách các tài khoản đã đăng ký"""
    try:
        ensure_csv_exists()
        accounts = []
        
        print(f"[DEBUG] Reading CSV from: {CSV_FILE_PATH}")
        print(f"[DEBUG] CSV file exists: {os.path.exists(CSV_FILE_PATH)}")
        
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8-sig') as f:  # utf-8-sig removes BOM
            first_line = f.readline()
            print(f"[DEBUG] CSV header: {repr(first_line)}")
            
            f.seek(0)  # Reset to beginning
            reader = csv.DictReader(f, delimiter=';')
            
            if not reader.fieldnames:
                print("[ERROR] CSV fieldnames is empty!")
                return jsonify({'success': False, 'message': 'CSV không có header'}), 500
            
            print(f"[DEBUG] CSV fieldnames: {reader.fieldnames}")
            
            row_count = 0
            for row in reader:
                if not row:
                    print(f"[DEBUG] Skipping empty row")
                    continue
                    
                row_count += 1
                try:
                    # Safe key cleanup - handle None keys and list values
                    row_cleaned = {}
                    for k, v in row.items():
                        clean_key = (k.strip() if k else '')
                        # Handle case where value is list or None
                        if isinstance(v, list):
                            clean_val = (v[0].strip() if v and v[0] else '')
                        else:
                            clean_val = (v.strip() if v else '')
                        row_cleaned[clean_key] = clean_val
                    
                    print(f"[DEBUG] Row {row_count}: {row_cleaned}")
                    
                    # Get email safely
                    email = row_cleaned.get('Tài khoản', '')
                    if email and email.strip():
                        name = row_cleaned.get('Họ và tên', '')
                        accounts.append({
                            'name': name,
                            'email': email
                        })
                        print(f"[DEBUG] Added account: {name} ({email})")
                except Exception as row_error:
                    print(f"[WARNING] Error processing row {row_count}: {row_error}")
                    continue
        
        print(f"[DEBUG] Total accounts loaded: {len(accounts)}")
        return jsonify({'success': True, 'accounts': accounts}), 200
        
    except Exception as e:
        print(f"[ERROR] get_accounts exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

def get_account_from_csv(taikhoan):
    """Lấy thông tin tài khoản từ CSV"""
    try:
        ensure_csv_exists()
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8-sig') as f:  # Remove BOM
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Strip spaces from keys and handle list/None values
                row_cleaned = {}
                for k, v in row.items():
                    clean_key = (k.strip() if k else '')
                    # Handle case where value is list or None
                    if isinstance(v, list):
                        clean_val = (v[0].strip() if v and v[0] else '')
                    else:
                        clean_val = (v.strip() if v else '')
                    row_cleaned[clean_key] = clean_val
                
                email_in_csv = (row_cleaned.get('Tài khoản') or '').strip()
                if email_in_csv.lower() == taikhoan.lower():
                    return {
                        'name': (row_cleaned.get('Họ và tên') or '').strip(),
                        'email': email_in_csv,
                        'password': (row_cleaned.get('Mật khẩu') or '').strip(),
                        'class': (row_cleaned.get('Lớp') or '').strip()
                    }
        return None
    except Exception as e:
        print(f"Error reading account from CSV: {e}")
        return None

@app.route('/run', methods=['POST'])
def run_main():
    """Chạy main.py với logid và taikhoan để giải bài cho một tài khoản cụ thể"""
    try:
        data = request.json
        logid = data.get('logid', '').strip()
        taikhoan = data.get('taikhoan', '').strip()

        if not logid:
            return jsonify({'success': False, 'message': 'Vui lòng nhập ID bài'}), 400
        
        if not taikhoan:
            return jsonify({'success': False, 'message': 'Vui lòng chọn tài khoản'}), 400

        # Check xem tài khoản có tồn tại trong CSV không
        account_info = get_account_from_csv(taikhoan)
        if not account_info:
            return jsonify({'success': False, 'message': f'Tài khoản {taikhoan} không tồn tại trong danh sách'}), 400
        
        print(f"[LOG] Chạy bài cho: {account_info['name']} ({taikhoan}) - Lớp {account_info['class']}")

        # Chạy main.py với --logid và --account
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'  # Force UTF-8 encoding
        
        process = subprocess.Popen(
            [sys.executable, 'main.py', '--logid', logid, '--account', taikhoan],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=False,  # Read as bytes, not text
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        # Lấy output - handle encoding issues
        output_bytes, _ = process.communicate(timeout=600)  # Timeout 10 phút
        returncode = process.returncode
        
        # Try decode with multiple encodings
        output = ''
        for encoding in ['utf-8', 'cp1252', 'latin-1']:
            try:
                output = output_bytes.decode(encoding)
                print(f"[DEBUG] Successfully decoded output with {encoding}")
                break
            except (UnicodeDecodeError, AttributeError):
                continue
        
        # If all encodings fail, use replace mode
        if not output:
            output = output_bytes.decode('utf-8', errors='replace')

        # Đọc log file nếu có
        log_content = ''
        if os.path.exists('latest.log'):
            try:
                with open('latest.log', 'r', encoding='utf-8', errors='replace') as f:
                    log_content = f.read()
            except:
                pass

        success = returncode == 0
        status = '✓ Thành công' if success else '✗ Lỗi'

        return jsonify({
            'success': success,
            'status': status,
            'message': output,
            'log_file': log_content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 200

    except subprocess.TimeoutExpired:
        process.kill()
        return jsonify({'success': False, 'message': 'Timeout: Chương trình chạy quá lâu'}), 500
    except Exception as e:
        print(f"[ERROR] run_main exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/stream', methods=['POST'])
def stream_main():
    """Stream output từ main.py real-time"""
    try:
        data = request.json
        logid = data.get('logid', '').strip()

        if not logid:
            return jsonify({'success': False, 'message': 'Vui lòng nhập ID bài'}), 400

        input_data = logid + '\n' + 'Y\n'

        def generate():
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'  # Force UTF-8 encoding
            
            process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                bufsize=1,
                universal_newlines=True,
                env=env,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )

            # Ghi input
            process.stdin.write(input_data)
            process.stdin.flush()
            process.stdin.close()

            # Stream output
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield f"data: {json.dumps({'line': line.rstrip()})}\n\n"

            process.wait()
            yield f"data: {json.dumps({'completed': True})}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

if __name__ == '__main__':
    ensure_csv_exists()
    print("=" * 50)
    print("Flask App đang chạy tại http://localhost:5000")
    print("Đăng nhập tài khoản: http://localhost:5000/")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
