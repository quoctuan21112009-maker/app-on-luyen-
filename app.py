from flask import Flask, render_template, request, jsonify, Response
import csv
import os
import subprocess
import sys
import json
import hashlib
from datetime import datetime, timedelta
from config import CSV_FILE_PATH
from sub_module.utils import remove_accents

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ─── KEY SYSTEM ───────────────────────────────────────────────────────────────
KEYS_FILE = 'keys.json'
SECRET_SALT = 'DNS_BATCH_SALT_2025_SECURE'
ADMIN_USERNAME = 'quoctuan'
ADMIN_PASSWORD = '21112009'
DEFAULT_KEY_DAYS = 1


def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_keys(keys):
    with open(KEYS_FILE, 'w', encoding='utf-8') as f:
        json.dump(keys, f, indent=2, ensure_ascii=False)


def generate_key_from_ip(ip: str) -> str:
    return hashlib.sha256((ip + SECRET_SALT).encode('utf-8')).hexdigest()[:20].upper()


def get_client_ip():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


def check_admin_auth():
    return request.headers.get('X-Admin-Auth', '') == f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}"


# ─── KEY ROUTES ───────────────────────────────────────────────────────────────
@app.route('/get-key', methods=['GET'])
def get_key():
    ip = get_client_ip()
    key = generate_key_from_ip(ip)
    keys = load_keys()
    now = datetime.now()
    if key not in keys:
        expiry = (now + timedelta(days=DEFAULT_KEY_DAYS)).isoformat()
        keys[key] = {'ip': ip, 'created': now.isoformat(), 'expiry': expiry, 'note': ''}
        save_keys(keys)
    kd = keys[key]
    expiry_dt = datetime.fromisoformat(kd['expiry'])
    is_valid = expiry_dt > now
    return jsonify({
        'success': True, 'key': key, 'ip': ip,
        'expiry': kd['expiry'], 'is_valid': is_valid,
        'seconds_remaining': max(0, int((expiry_dt - now).total_seconds())),
        'note': kd.get('note', '')
    })


@app.route('/verify-key', methods=['POST'])
def verify_key():
    data = request.json
    key = data.get('key', '').strip().upper()
    keys = load_keys()
    if key not in keys:
        return jsonify({'success': False, 'message': 'Key không tồn tại trong hệ thống'}), 400
    expiry_dt = datetime.fromisoformat(keys[key]['expiry'])
    now = datetime.now()
    if expiry_dt < now:
        return jsonify({'success': False, 'message': 'Key đã hết hạn. Liên hệ admin để gia hạn'}), 400
    return jsonify({
        'success': True, 'message': 'Xác thực thành công',
        'expiry': keys[key]['expiry'],
        'seconds_remaining': max(0, int((expiry_dt - now).total_seconds())),
        'ip': keys[key]['ip']
    })


@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('username') == ADMIN_USERNAME and data.get('password') == ADMIN_PASSWORD:
        return jsonify({'success': True, 'token': f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}"})
    return jsonify({'success': False, 'message': 'Sai tài khoản hoặc mật khẩu'}), 401


@app.route('/admin/keys', methods=['GET'])
def admin_get_keys():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    keys = load_keys()
    now = datetime.now()
    result = []
    for key, kd in keys.items():
        exp_dt = datetime.fromisoformat(kd['expiry'])
        result.append({
            'key': key, 'ip': kd.get('ip', ''),
            'expiry': kd['expiry'], 'is_valid': exp_dt > now,
            'created': kd.get('created', ''), 'note': kd.get('note', '')
        })
    result.sort(key=lambda x: x['created'], reverse=True)
    return jsonify({'success': True, 'keys': result})


@app.route('/admin/extend-key', methods=['POST'])
def admin_extend_key():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.json
    key = data.get('key', '').strip().upper()
    days = int(data.get('days', 7))
    note = data.get('note', '')
    keys = load_keys()
    if key not in keys:
        return jsonify({'success': False, 'message': 'Key không tồn tại'}), 400
    now = datetime.now()
    base = max(now, datetime.fromisoformat(keys[key]['expiry']))
    new_expiry = base + timedelta(days=days)
    keys[key]['expiry'] = new_expiry.isoformat()
    if note:
        keys[key]['note'] = note
    save_keys(keys)
    return jsonify({'success': True, 'message': f'Đã gia hạn {days} ngày', 'new_expiry': new_expiry.isoformat()})


@app.route('/admin/delete-key', methods=['POST'])
def admin_delete_key():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    key = request.json.get('key', '').strip().upper()
    keys = load_keys()
    if key not in keys:
        return jsonify({'success': False, 'message': 'Key không tồn tại'}), 400
    del keys[key]
    save_keys(keys)
    return jsonify({'success': True, 'message': 'Đã xóa key'})


# ─── CSV HELPERS ──────────────────────────────────────────────────────────────
def ensure_csv_exists():
    try:
        if not os.path.exists(CSV_FILE_PATH):
            print(f"[INFO] Creating new CSV at {CSV_FILE_PATH}")
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['STT', 'Mã học sinh', 'Họ và tên', 'Lớp', 'Tài khoản', 'Mật khẩu', 'Mã đăng nhập cho PH', 'isWrongPass', ''])
        else:
            with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
                first_line = f.readline().rstrip('\n')
                if '; ' in first_line or ' ;' in first_line:
                    f.seek(0)
                    lines = f.readlines()
                    fixed_header = first_line.replace('; ', ';').replace(' ;', ';')
                    with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as fw:
                        fw.write(fixed_header + '\n')
                        fw.writelines(lines[1:])
    except Exception as e:
        print(f"[ERROR] ensure_csv_exists: {e}")


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
        print(f"Error: {e}")
    return max_stt + 1


def _clean_row(row):
    cleaned = {}
    for k, v in row.items():
        ck = (k.strip() if k else '')
        cv = (v[0].strip() if isinstance(v, list) and v else (v.strip() if v else ''))
        cleaned[ck] = cv
    return cleaned


def get_account_from_csv(taikhoan):
    try:
        ensure_csv_exists()
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                rc = _clean_row(row)
                email = (rc.get('Tài khoản') or '').strip()
                if email.lower() == taikhoan.lower():
                    return {
                        'name': (rc.get('Họ và tên') or '').strip(),
                        'email': email,
                        'password': (rc.get('Mật khẩu') or '').strip(),
                        'class': (rc.get('Lớp') or '').strip()
                    }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


# ─── MAIN ROUTES ──────────────────────────────────────────────────────────────
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        ten = remove_accents(data.get('ten', '').strip())
        lop = data.get('lop', '').strip()
        taikhoan = data.get('taikhoan', '').strip()
        matkhau = data.get('matkhau', '').strip()
        if not all([ten, lop, taikhoan, matkhau]):
            return jsonify({'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin'}), 400
        ensure_csv_exists()
        next_stt = get_next_stt()
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([next_stt, '', ten, lop, taikhoan, matkhau, '', '', ''])
        return jsonify({'success': True, 'message': f'Đăng ký thành công cho {ten}', 'stt': next_stt}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500


@app.route('/homework')
def homework():
    return render_template('homework.html')


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
                rc = _clean_row(row)
                email = rc.get('Tài khoản', '')
                if email:
                    accounts.append({'name': rc.get('Họ và tên', ''), 'email': email})
        return jsonify({'success': True, 'accounts': accounts}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500


@app.route('/run', methods=['POST'])
def run_main():
    try:
        data = request.json
        logid = data.get('logid', '').strip()
        taikhoan = data.get('taikhoan', '').strip()
        if not logid:
            return jsonify({'success': False, 'message': 'Vui lòng nhập ID bài'}), 400
        if not taikhoan:
            return jsonify({'success': False, 'message': 'Vui lòng chọn tài khoản'}), 400
        account_info = get_account_from_csv(taikhoan)
        if not account_info:
            return jsonify({'success': False, 'message': f'Tài khoản {taikhoan} không tồn tại'}), 400

        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        process = subprocess.Popen(
            [sys.executable, 'main.py', '--logid', logid, '--account', taikhoan],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=False, env=env,
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
            except:
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
        return jsonify({'success': False, 'message': 'Timeout: Chương trình chạy quá lâu (>10 phút)'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500


if __name__ == '__main__':
    ensure_csv_exists()
    print("=" * 50)
    print("DNS Batch Flask App: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
