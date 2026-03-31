from flask import Flask, render_template, request, jsonify
import csv, os, subprocess, sys, hashlib
from datetime import datetime, timedelta
from config import CSV_FILE_PATH
from sub_module.utils import remove_accents

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SECRET_SALT      = 'DNS_BATCH_SALT_2025_SECURE'
ADMIN_USERNAME   = 'quoctuan'
ADMIN_PASSWORD   = '21112009'
DEFAULT_KEY_DAYS = 1

# ─── RAM STORAGE (tránh lỗi ghi disk trên Render) ────────────────────────────
_KEYS: dict = {}

def load_keys() -> dict:
    return _KEYS

def save_keys(keys: dict):
    _KEYS.clear()
    _KEYS.update(keys)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def generate_key_from_ip(ip: str) -> str:
    return hashlib.sha256((ip + SECRET_SALT).encode()).hexdigest()[:20].upper()

def get_client_ip() -> str:
    fwd = request.headers.get('X-Forwarded-For', '')
    return fwd.split(',')[0].strip() if fwd else (request.remote_addr or '127.0.0.1')

def check_admin_auth() -> bool:
    return request.headers.get('X-Admin-Auth', '') == f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}"


# ─── KEY ROUTES ───────────────────────────────────────────────────────────────

@app.route('/get-key')
def get_key():
    """
    Trả về key của IP hiện tại.
    Nếu chưa có → TỰ ĐỘNG TẠO với thời hạn DEFAULT_KEY_DAYS.
    Nếu đã có   → chỉ trả về, KHÔNG tạo lại.
    """
    ip   = get_client_ip()
    key  = generate_key_from_ip(ip)
    keys = load_keys()
    now  = datetime.now()

    if key not in keys:
        expiry = (now + timedelta(days=DEFAULT_KEY_DAYS)).isoformat()
        keys[key] = {
            'ip':      ip,
            'created': now.isoformat(),
            'expiry':  expiry,
            'note':    '',
            'active':  True,
        }
        save_keys(keys)

    kd       = keys[key]
    exp_dt   = datetime.fromisoformat(kd['expiry'])
    is_valid = kd.get('active', True) and exp_dt > now

    return jsonify({
        'success':           True,
        'key':               key,
        'ip':                ip,
        'expiry':            kd['expiry'],
        'is_valid':          is_valid,
        'seconds_remaining': max(0, int((exp_dt - now).total_seconds())),
        'note':              kd.get('note', ''),
        'created':           kd.get('created', ''),
    })


@app.route('/verify-key', methods=['POST'])
def verify_key():
    """Xác thực key (dùng trên trang homework trước khi cho chạy tool)."""
    data = request.json or {}
    key  = data.get('key', '').strip().replace('-', '').upper()
    keys = load_keys()

    if key not in keys:
        return jsonify({'success': False, 'message': 'Key không tồn tại trong hệ thống'}), 400

    kd     = keys[key]
    exp_dt = datetime.fromisoformat(kd['expiry'])
    now    = datetime.now()

    if not kd.get('active', True):
        return jsonify({'success': False, 'message': 'Key đã bị vô hiệu hoá'}), 400
    if exp_dt < now:
        return jsonify({'success': False, 'message': 'Key đã hết hạn. Liên hệ admin để gia hạn'}), 400

    return jsonify({
        'success':           True,
        'message':           'Xác thực thành công',
        'expiry':            kd['expiry'],
        'seconds_remaining': max(0, int((exp_dt - now).total_seconds())),
        'ip':                kd['ip'],
    })


@app.route('/verify-key-by-ip')
def verify_key_by_ip():
    """Kiểm tra key của IP hiện tại (dùng khi load homework.html)."""
    ip   = get_client_ip()
    key  = generate_key_from_ip(ip)
    keys = load_keys()
    now  = datetime.now()

    if key not in keys:
        return jsonify({
            'success': False,
            'message': 'Bạn chưa có key. Vui lòng lấy key tại trang chủ.',
            'key': key, 'ip': ip
        })

    kd     = keys[key]
    exp_dt = datetime.fromisoformat(kd['expiry'])

    if not kd.get('active', True):
        return jsonify({
            'success': False,
            'message': 'Key của bạn đã bị vô hiệu hoá. Liên hệ admin.',
            'key': key, 'ip': ip
        })
    if exp_dt < now:
        return jsonify({
            'success': False,
            'message': 'Key đã hết hạn. Liên hệ admin để gia hạn.',
            'key': key, 'ip': ip, 'expiry': kd['expiry']
        })

    return jsonify({
        'success':           True,
        'key':               key,
        'ip':                ip,
        'expiry':            kd['expiry'],
        'seconds_remaining': max(0, int((exp_dt - now).total_seconds())),
    })


# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    if data.get('username') == ADMIN_USERNAME and data.get('password') == ADMIN_PASSWORD:
        return jsonify({'success': True, 'token': f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}"})
    return jsonify({'success': False, 'message': 'Sai tài khoản hoặc mật khẩu'}), 401


@app.route('/admin/keys')
def admin_get_keys():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    keys   = load_keys()
    now    = datetime.now()
    result = []
    for key, kd in keys.items():
        exp_dt = datetime.fromisoformat(kd['expiry'])
        result.append({
            'key':      key,
            'ip':       kd.get('ip', ''),
            'expiry':   kd['expiry'],
            'is_valid': kd.get('active', True) and exp_dt > now,
            'active':   kd.get('active', True),
            'created':  kd.get('created', ''),
            'note':     kd.get('note', ''),
        })
    result.sort(key=lambda x: x['created'], reverse=True)
    return jsonify({'success': True, 'keys': result})


@app.route('/admin/set-expiry', methods=['POST'])
def admin_set_expiry():
    """Admin đặt ngày giờ hết hạn chính xác cho key (chỉ key đã tồn tại)."""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data       = request.json or {}
    key        = data.get('key', '').strip().replace('-', '').upper()
    expiry_str = data.get('expiry', '').strip().replace(' ', 'T')
    note       = data.get('note', '')
    keys       = load_keys()

    if key not in keys:
        return jsonify({'success': False, 'message': 'Key không tồn tại'}), 400
    try:
        new_expiry = datetime.fromisoformat(expiry_str)
    except ValueError:
        return jsonify({'success': False,
                        'message': 'Định dạng ngày giờ không hợp lệ'}), 400

    keys[key]['expiry'] = new_expiry.isoformat()
    if note:
        keys[key]['note'] = note
    save_keys(keys)
    return jsonify({'success': True, 'message': 'Đã cập nhật hạn key',
                    'new_expiry': new_expiry.isoformat()})


@app.route('/admin/extend-key', methods=['POST'])
def admin_extend_key():
    """Admin gia hạn thêm N ngày (chỉ key đã tồn tại, KHÔNG tạo mới)."""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    data = request.json or {}
    key  = data.get('key', '').strip().replace('-', '').upper()
    days = int(data.get('days', 7))
    note = data.get('note', '')
    keys = load_keys()

    if key not in keys:
        return jsonify({'success': False, 'message': 'Key không tồn tại. Admin không thể tạo key mới.'}), 400

    now   = datetime.now()
    base  = max(now, datetime.fromisoformat(keys[key]['expiry']))
    new_e = base + timedelta(days=days)
    keys[key]['expiry'] = new_e.isoformat()
    keys[key]['active'] = True
    if note:
        keys[key]['note'] = note
    save_keys(keys)
    return jsonify({'success': True, 'message': f'Đã gia hạn {days} ngày',
                    'new_expiry': new_e.isoformat()})


@app.route('/admin/toggle-key', methods=['POST'])
def admin_toggle_key():
    """Bật / tắt key."""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    key  = (request.json or {}).get('key', '').strip().upper()
    keys = load_keys()
    if key not in keys:
        return jsonify({'success': False, 'message': 'Key không tồn tại'}), 400
    keys[key]['active'] = not keys[key].get('active', True)
    save_keys(keys)
    state = 'kích hoạt' if keys[key]['active'] else 'vô hiệu hoá'
    return jsonify({'success': True, 'message': f'Đã {state} key',
                    'active': keys[key]['active']})


@app.route('/admin/delete-key', methods=['POST'])
def admin_delete_key():
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    key  = (request.json or {}).get('key', '').strip().upper()
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
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f, delimiter=';').writerow(
                    ['STT', 'Mã học sinh', 'Họ và tên', 'Lớp',
                     'Tài khoản', 'Mật khẩu', 'Mã đăng nhập cho PH', 'isWrongPass', ''])
        else:
            with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
                first = f.readline().rstrip('\n')
            if '; ' in first or ' ;' in first:
                with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8') as f:
                    lines = f.readlines()
                with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                    f.write(first.replace('; ', ';').replace(' ;', ';') + '\n')
                    f.writelines(lines[1:])
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
    return {
        (k.strip() if k else ''): (
            v[0].strip() if isinstance(v, list) and v else (v.strip() if v else '')
        )
        for k, v in row.items()
    }


def get_account_from_csv(taikhoan):
    try:
        ensure_csv_exists()
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f, delimiter=';'):
                rc = _clean_row(row)
                if rc.get('Tài khoản', '').lower() == taikhoan.lower():
                    return {
                        'name':     rc.get('Họ và tên', ''),
                        'email':    rc.get('Tài khoản', ''),
                        'password': rc.get('Mật khẩu', ''),
                        'class':    rc.get('Lớp', ''),
                    }
    except Exception as e:
        print(f"Error: {e}")
    return None


# ─── MAIN ROUTES ──────────────────────────────────────────────────────────────

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/homework')
def homework():
    return render_template('homework.html')


@app.route('/get-accounts')
def get_accounts():
    try:
        ensure_csv_exists()
        accounts = []
        with open(CSV_FILE_PATH, 'r', newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f, delimiter=';'):
                rc = _clean_row(row)
                if rc.get('Tài khoản'):
                    accounts.append({'name': rc.get('Họ và tên', ''), 'email': rc['Tài khoản']})
        return jsonify({'success': True, 'accounts': accounts})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json or {}
        ten  = remove_accents(data.get('ten', '').strip())
        lop  = data.get('lop', '').strip()
        tk   = data.get('taikhoan', '').strip()
        mk   = data.get('matkhau', '').strip()
        if not all([ten, lop, tk, mk]):
            return jsonify({'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin'}), 400
        ensure_csv_exists()
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f, delimiter=';').writerow([get_next_stt(), '', ten, lop, tk, mk, '', '', ''])
        return jsonify({'success': True, 'message': f'Đăng ký thành công cho {ten}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/run', methods=['POST'])
def run_main():
    try:
        data     = request.json or {}
        logid    = data.get('logid', '').strip()
        taikhoan = data.get('taikhoan', '').strip()
        if not logid:
            return jsonify({'success': False, 'message': 'Vui lòng nhập ID bài'}), 400
        if not taikhoan:
            return jsonify({'success': False, 'message': 'Vui lòng chọn tài khoản'}), 400
        if not get_account_from_csv(taikhoan):
            return jsonify({'success': False,
                            'message': f'Tài khoản {taikhoan} không tồn tại'}), 400

        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        proc = subprocess.Popen(
            [sys.executable, 'main.py', '--logid', logid, '--account', taikhoan],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=False, env=env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        out_bytes, _ = proc.communicate(timeout=600)

        output = ''
        for enc in ['utf-8', 'cp1252', 'latin-1']:
            try:
                output = out_bytes.decode(enc)
                break
            except (UnicodeDecodeError, AttributeError):
                continue
        if not output:
            output = out_bytes.decode('utf-8', errors='replace')

        log_content = ''
        if os.path.exists('latest.log'):
            try:
                with open('latest.log', 'r', encoding='utf-8', errors='replace') as f:
                    log_content = f.read()
            except:
                pass

        success = proc.returncode == 0
        return jsonify({
            'success':   success,
            'status':    '✓ Thành công' if success else '✗ Lỗi',
            'message':   output,
            'log_file':  log_content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
    except subprocess.TimeoutExpired:
        proc.kill()
        return jsonify({'success': False, 'message': 'Timeout: chương trình chạy quá 10 phút'}), 500
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    ensure_csv_exists()
    print("=" * 50)
    print("DNS Batch Flask App: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
