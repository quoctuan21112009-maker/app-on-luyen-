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
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['STT', 'Mã học sinh', 'Họ và tên', 'Lớp', 'Tài khoản', 'Mật khẩu', 'Mã đăng nhập cho PH', 'isWrongPass', ''])

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
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row.get('Tài khoản', '').strip():
                    accounts.append({
                        'name': row.get('Họ và tên', '').strip(),
                        'email': row.get('Tài khoản', '').strip()
                    })
        
        return jsonify({'success': True, 'accounts': accounts}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

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

        # Chạy main.py với --logid và --account
        process = subprocess.Popen(
            [sys.executable, 'main.py', '--logid', logid, '--account', taikhoan],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        # Lấy output
        output, _ = process.communicate(timeout=600)  # Timeout 10 phút
        returncode = process.returncode

        # Đọc log file nếu có
        log_content = ''
        if os.path.exists('latest.log'):
            try:
                with open('latest.log', 'r', encoding='utf-8') as f:
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
            process = subprocess.Popen(
                [sys.executable, 'main.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                bufsize=1,
                universal_newlines=True,
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
