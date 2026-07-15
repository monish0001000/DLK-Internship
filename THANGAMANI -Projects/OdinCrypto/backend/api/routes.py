"""
OdinCrypto - All Flask Routes (stdlib + cryptography only)
"""
import os, io, json, secrets, base64, hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import (Blueprint, render_template, request, redirect, url_for,
                   session, flash, jsonify, send_file, send_from_directory, abort)
from backend.database.db import get_db
from backend.authentication.auth_service import (log_action, register_user,
    verify_user, change_password, calculate_security_score, hash_password, check_password)
from backend.crypto.crypto_service import CryptoService

main = Blueprint('main', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        if not session.get('is_admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated

def get_user(user_id):
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    db.close()
    return dict(u) if u else None

# ─── AUTH ────────────────────────────────────────────────────────────────────

@main.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email    = request.form.get('email','').strip()
        password = request.form.get('password','')
        confirm  = request.form.get('confirm_password','')
        if not all([username, email, password, confirm]):
            flash('All fields are required.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
        else:
            r = register_user(username, email, password)
            if r['success']:
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('main.login'))
            flash(r['message'], 'error')
    return render_template('auth/register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        r = verify_user(request.form.get('email',''), request.form.get('password',''))
        if r['success']:
            u = r['user']
            session['user_id']  = u['id']
            session['username'] = u['username']
            session['is_admin'] = bool(u['is_admin'])
            session.permanent   = True
            flash(f"Welcome back, {u['username']}!", 'success')
            return redirect(url_for('main.dashboard'))
        flash(r['message'], 'error')
    return render_template('auth/login.html')

@main.route('/logout')
@login_required
def logout():
    log_action(session['user_id'], 'LOGOUT', 'User logged out')
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.login'))

# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@main.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    db  = get_db()
    keys   = db.execute("SELECT COUNT(*) as c FROM key_pairs WHERE user_id=? AND is_revoked=0",(uid,)).fetchone()['c']
    shared = db.execute("SELECT COUNT(*) as c FROM shared_files WHERE user_id=? AND is_active=1",(uid,)).fetchone()['c']
    vault  = db.execute("SELECT COUNT(*) as c FROM password_vault WHERE user_id=?",(uid,)).fetchone()['c']
    notes  = db.execute("SELECT COUNT(*) as c FROM secure_notes WHERE user_id=?",(uid,)).fetchone()['c']
    logs   = [dict(r) for r in db.execute(
        "SELECT * FROM audit_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT 5",(uid,)).fetchall()]
    user   = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    db.close()
    score  = calculate_security_score(uid)
    db2 = get_db(); db2.execute("UPDATE users SET security_score=? WHERE id=?",(score,uid)); db2.commit(); db2.close()
    return render_template('dashboard/dashboard.html',
        user=user, keys=keys, shared=shared, vault=vault, notes=notes, logs=logs, score=score)

# ─── KEYS ────────────────────────────────────────────────────────────────────

@main.route('/keys')
@login_required
def keys():
    uid = session['user_id']
    db  = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    key_list = [dict(r) for r in db.execute(
        "SELECT * FROM key_pairs WHERE user_id=? ORDER BY created_at DESC",(uid,)).fetchall()]
    db.close()
    return render_template('dashboard/keys.html', user=user, keys=key_list)

@main.route('/keys/generate', methods=['POST'])
@login_required
def generate_key():
    uid       = session['user_id']
    key_size  = int(request.form.get('key_size', 2048))
    key_name  = request.form.get('key_name', f'Key-{datetime.now().strftime("%Y%m%d%H%M%S")}')
    password  = request.form.get('key_password','')
    if key_size not in [2048, 4096]:
        flash('Invalid key size.', 'error')
        return redirect(url_for('main.keys'))
    kp  = CryptoService.generate_rsa_keypair(key_size)
    enc = CryptoService.encrypt_private_key_with_password(kp['private_key'], password)
    db  = get_db()
    db.execute("INSERT INTO key_pairs (user_id,key_name,algorithm,public_key,private_key_encrypted) VALUES (?,?,?,?,?)",
               (uid, key_name, f'RSA-{key_size}', kp['public_key'], enc))
    db.commit(); db.close()
    log_action(uid, 'KEY_GENERATE', f'Generated RSA-{key_size}: {key_name}')
    flash(f'RSA-{key_size} key pair "{key_name}" generated!', 'success')
    return redirect(url_for('main.keys'))

@main.route('/keys/<int:kid>/download/public')
@login_required
def download_key(kid):
    uid = session['user_id']
    db  = get_db()
    kp  = db.execute("SELECT * FROM key_pairs WHERE id=? AND user_id=?",(kid,uid)).fetchone()
    db.close()
    if not kp: abort(404)
    log_action(uid, 'KEY_DOWNLOAD', f'Downloaded public key: {kp["key_name"]}')
    return send_file(io.BytesIO(kp['public_key'].encode()), as_attachment=True,
                     download_name=f'{kp["key_name"]}_public.pem', mimetype='application/x-pem-file')

@main.route('/keys/<int:kid>/revoke', methods=['POST'])
@login_required
def revoke_key(kid):
    uid = session['user_id']
    db  = get_db()
    kp  = db.execute("SELECT * FROM key_pairs WHERE id=? AND user_id=?",(kid,uid)).fetchone()
    if kp:
        db.execute("UPDATE key_pairs SET is_revoked=1 WHERE id=?",(kid,))
        db.commit()
        log_action(uid,'KEY_REVOKE',f'Revoked: {kp["key_name"]}')
        flash(f'Key "{kp["key_name"]}" revoked.','warning')
    db.close()
    return redirect(url_for('main.keys'))

@main.route('/keys/<int:kid>/qr')
@login_required
def key_qr(kid):
    uid = session['user_id']
    db  = get_db()
    kp  = db.execute("SELECT * FROM key_pairs WHERE id=? AND user_id=?",(kid,uid)).fetchone()
    db.close()
    if not kp: abort(404)
    img = CryptoService.make_qr(kp['public_key'])
    buf = io.BytesIO(); img.save(buf, format='PNG'); buf.seek(0)
    return send_file(buf, mimetype='image/png', download_name=f'{kp["key_name"]}_qr.png')

# ─── TEXT ENCRYPTION ─────────────────────────────────────────────────────────

@main.route('/encrypt/text', methods=['GET','POST'])
@login_required
def encrypt_text():
    uid  = session['user_id']
    db   = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    key_list = [dict(r) for r in db.execute(
        "SELECT * FROM key_pairs WHERE user_id=? AND is_revoked=0",(uid,)).fetchall()]
    db.close()
    result = None
    if request.method == 'POST':
        action    = request.form.get('action','encrypt')
        algorithm = request.form.get('algorithm','aes')
        text      = request.form.get('text','')
        password  = request.form.get('password','')
        kid       = request.form.get('key_id')
        try:
            if algorithm == 'aes':
                if action == 'encrypt':
                    enc = CryptoService.aes_encrypt(text.encode(), password)
                    result = {'action':'encrypted','data':json.dumps(enc),'algorithm':'AES-256-CBC'}
                    log_action(uid,'TEXT_ENCRYPT','AES-256 text encrypted')
                else:
                    pkg = json.loads(text)
                    dec = CryptoService.aes_decrypt(pkg['ciphertext'],pkg['salt'],pkg['iv'],password)
                    result = {'action':'decrypted','data':dec.decode(),'algorithm':'AES-256-CBC'}
                    log_action(uid,'TEXT_DECRYPT','AES-256 text decrypted')
            elif algorithm in ('rsa','hybrid'):
                if not kid:
                    flash('Select a key.','error')
                else:
                    db2 = get_db()
                    kp  = db2.execute("SELECT * FROM key_pairs WHERE id=? AND user_id=?",(kid,uid)).fetchone()
                    db2.close()
                    if algorithm == 'rsa':
                        if action == 'encrypt':
                            ct = CryptoService.rsa_encrypt(text.encode(), kp['public_key'])
                            result = {'action':'encrypted','data':ct,'algorithm':'RSA-OAEP'}
                            log_action(uid,'TEXT_ENCRYPT','RSA text encrypted')
                        else:
                            priv = CryptoService.decrypt_private_key_with_password(kp['private_key_encrypted'],password)
                            dec  = CryptoService.rsa_decrypt(text, priv)
                            result = {'action':'decrypted','data':dec.decode(),'algorithm':'RSA-OAEP'}
                            log_action(uid,'TEXT_DECRYPT','RSA text decrypted')
                    else:
                        if action == 'encrypt':
                            pkg = CryptoService.hybrid_encrypt(text.encode(), kp['public_key'])
                            result = {'action':'encrypted','data':json.dumps(pkg),'algorithm':'Hybrid AES+RSA'}
                            log_action(uid,'TEXT_ENCRYPT','Hybrid text encrypted')
                        else:
                            priv = CryptoService.decrypt_private_key_with_password(kp['private_key_encrypted'],password)
                            pkg  = json.loads(text)
                            dec  = CryptoService.hybrid_decrypt(pkg, priv)
                            result = {'action':'decrypted','data':dec.decode(),'algorithm':'Hybrid AES+RSA'}
                            log_action(uid,'TEXT_DECRYPT','Hybrid text decrypted')
        except Exception as e:
            flash(f'Operation failed: {e}','error')
    return render_template('dashboard/encrypt_text.html', user=user, result=result, keys=key_list)

# ─── FILE ENCRYPTION ─────────────────────────────────────────────────────────

@main.route('/encrypt/file', methods=['GET','POST'])
@login_required
def encrypt_file():
    from flask import current_app
    uid  = session['user_id']
    db   = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    db.close()
    result = None
    if request.method == 'POST':
        action   = request.form.get('action','encrypt')
        password = request.form.get('password','')
        f = request.files.get('file')
        if not f or f.filename == '':
            flash('No file selected.','error')
            return redirect(request.url)
        data = f.read(); oname = f.filename
        try:
            if action == 'encrypt':
                enc     = CryptoService.aes_encrypt(data, password)
                package = json.dumps({'original_name':oname,'encrypted':enc}).encode()
                outname = oname + '.odenc'
                out     = os.path.join(current_app.config['ENCRYPTED_FOLDER'], outname)
                with open(out,'wb') as fp: fp.write(package)
                log_action(uid,'FILE_ENCRYPT',f'Encrypted: {oname}')
                result  = {'action':'encrypted','filename':outname,'original':oname}
                flash(f'"{oname}" encrypted!','success')
            else:
                try:
                    pkg   = json.loads(data.decode())
                    enc   = pkg['encrypted']; oname = pkg.get('original_name','decrypted_file')
                except Exception:
                    flash('Invalid .odenc file.','error'); return redirect(request.url)
                dec  = CryptoService.aes_decrypt(enc['ciphertext'],enc['salt'],enc['iv'],password)
                out  = os.path.join(current_app.config['DECRYPTED_FOLDER'], oname)
                with open(out,'wb') as fp: fp.write(dec)
                log_action(uid,'FILE_DECRYPT',f'Decrypted: {oname}')
                result = {'action':'decrypted','filename':oname}
                flash('File decrypted!','success')
        except Exception as e:
            flash(f'Error: {e}','error')
    return render_template('dashboard/encrypt_file.html', user=user, result=result)

@main.route('/download/encrypted/<path:filename>')
@login_required
def download_encrypted(filename):
    from flask import current_app
    return send_from_directory(current_app.config['ENCRYPTED_FOLDER'], filename, as_attachment=True)

@main.route('/download/decrypted/<path:filename>')
@login_required
def download_decrypted(filename):
    from flask import current_app
    return send_from_directory(current_app.config['DECRYPTED_FOLDER'], filename, as_attachment=True)

# ─── HASH CENTER ─────────────────────────────────────────────────────────────

@main.route('/hash', methods=['GET','POST'])
@login_required
def hash_center():
    uid  = session['user_id']
    db   = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    db.close()
    result = None
    if request.method == 'POST':
        algo    = request.form.get('algorithm','sha256')
        itype   = request.form.get('input_type','text')
        verify  = request.form.get('verify_hash','').strip()
        try:
            data    = request.form.get('text','').encode() if itype=='text' else request.files['file'].read()
            computed = CryptoService.compute_hash(data, algo)
            is_match = None
            if verify: is_match = secrets.compare_digest(computed.lower(), verify.lower())
            log_action(uid,'HASH_COMPUTE',f'{algo.upper()} hash computed')
            result = {'hash':computed,'algorithm':algo.upper(),'is_match':is_match}
        except Exception as e:
            flash(f'Error: {e}','error')
    return render_template('dashboard/hash.html', user=user, result=result)

# ─── DIGITAL SIGNATURE ───────────────────────────────────────────────────────

@main.route('/signature', methods=['GET','POST'])
@login_required
def digital_signature():
    uid  = session['user_id']
    db   = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    key_list = [dict(r) for r in db.execute(
        "SELECT * FROM key_pairs WHERE user_id=? AND is_revoked=0",(uid,)).fetchall()]
    db.close()
    result = None
    if request.method == 'POST':
        action   = request.form.get('action','sign')
        kid      = request.form.get('key_id')
        kpwd     = request.form.get('key_password','')
        itype    = request.form.get('input_type','text')
        try:
            data = request.form.get('text','').encode() if itype=='text' else request.files['file'].read()
            db2  = get_db()
            kp   = db2.execute("SELECT * FROM key_pairs WHERE id=? AND user_id=?",(kid,uid)).fetchone()
            db2.close()
            if not kp: flash('Key not found.','error')
            elif action == 'sign':
                priv = CryptoService.decrypt_private_key_with_password(kp['private_key_encrypted'],kpwd)
                sig  = CryptoService.sign_data(data, priv)
                result = {'action':'signed','signature':sig,'key':kp['key_name']}
                log_action(uid,'SIGN',f'Signed with: {kp["key_name"]}')
            else:
                sig   = request.form.get('signature','').strip()
                valid = CryptoService.verify_signature(data, sig, kp['public_key'])
                result = {'action':'verified','valid':valid,'key':kp['key_name']}
                log_action(uid,'VERIFY',f'Signature verified: {valid}')
        except Exception as e:
            flash(f'Error: {e}','error')
    return render_template('dashboard/signature.html', user=user, result=result, keys=key_list)

# ─── PASSWORD GENERATOR ──────────────────────────────────────────────────────

@main.route('/password-generator')
@login_required
def password_generator():
    uid = session['user_id']
    db  = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    db.close()
    return render_template('dashboard/password_generator.html', user=user)

@main.route('/api/generate-password', methods=['POST'])
@login_required
def api_generate_password():
    data = request.get_json()
    mode = data.get('mode','password')
    if mode == 'passphrase':
        result = CryptoService.generate_passphrase(data.get('words',4))
    elif mode == 'pin':
        result = CryptoService.generate_pin(data.get('length',6))
    else:
        result = CryptoService.generate_password(
            length=data.get('length',16), use_upper=data.get('upper',True),
            use_lower=data.get('lower',True), use_digits=data.get('digits',True),
            use_symbols=data.get('symbols',True))
    return jsonify({'password': result})

# ─── VAULT ───────────────────────────────────────────────────────────────────

@main.route('/vault', methods=['GET','POST'])
@login_required
def vault():
    uid   = session['user_id']
    db    = get_db()
    user  = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    total = db.execute("SELECT COUNT(*) as c FROM password_vault WHERE user_id=?",(uid,)).fetchone()['c']
    db.close()
    master_key = request.form.get('master_key') or request.args.get('master_key','')
    items = []; unlocked = False
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add' and master_key:
            db2 = get_db()
            db2.execute("INSERT INTO password_vault (user_id,site_name,username_enc,password_enc,url) VALUES (?,?,?,?,?)",
                (uid, request.form.get('site_name',''),
                 CryptoService.encrypt_vault_item(request.form.get('username',''), master_key),
                 CryptoService.encrypt_vault_item(request.form.get('password',''), master_key),
                 request.form.get('url','')))
            db2.commit(); db2.close()
            log_action(uid,'VAULT_ADD',f'Added: {request.form.get("site_name","")}')
            flash('Entry added!','success')
            total += 1
        elif action == 'delete':
            eid = request.form.get('entry_id')
            db2 = get_db(); db2.execute("DELETE FROM password_vault WHERE id=? AND user_id=?",(eid,uid)); db2.commit(); db2.close()
            flash('Entry deleted.','warning')
    if master_key:
        unlocked = True
        db3 = get_db()
        rows = db3.execute("SELECT * FROM password_vault WHERE user_id=?",(uid,)).fetchall()
        db3.close()
        for row in rows:
            try:
                items.append({'id':row['id'],'site_name':row['site_name'],
                    'username':CryptoService.decrypt_vault_item(row['username_enc'],master_key),
                    'password':CryptoService.decrypt_vault_item(row['password_enc'],master_key),
                    'url':row['url'],'created_at':row['created_at']})
            except Exception:
                items.append({'id':row['id'],'site_name':row['site_name'],
                    'username':'[Wrong key]','password':'***','url':row['url'],'created_at':row['created_at']})
    return render_template('dashboard/vault.html', user=user, items=items,
                           unlocked=unlocked, master_key=master_key, total=total)

# ─── SECURE NOTES ────────────────────────────────────────────────────────────

@main.route('/notes', methods=['GET','POST'])
@login_required
def secure_notes():
    uid   = session['user_id']
    db    = get_db()
    user  = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    total = db.execute("SELECT COUNT(*) as c FROM secure_notes WHERE user_id=?",(uid,)).fetchone()['c']
    db.close()
    master_key = request.form.get('master_key') or request.args.get('master_key','')
    notes = []; unlocked = False
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add' and master_key:
            db2 = get_db()
            db2.execute("INSERT INTO secure_notes (user_id,title_enc,content_enc) VALUES (?,?,?)",
                (uid, CryptoService.encrypt_vault_item(request.form.get('title',''),master_key),
                 CryptoService.encrypt_vault_item(request.form.get('content',''),master_key)))
            db2.commit(); db2.close()
            flash('Note saved!','success')
        elif action == 'delete':
            nid = request.form.get('note_id')
            db2 = get_db(); db2.execute("DELETE FROM secure_notes WHERE id=? AND user_id=?",(nid,uid)); db2.commit(); db2.close()
            flash('Note deleted.','warning')
    if master_key:
        unlocked = True
        db3 = get_db()
        rows = db3.execute("SELECT * FROM secure_notes WHERE user_id=? ORDER BY created_at DESC",(uid,)).fetchall()
        db3.close()
        for row in rows:
            try:
                notes.append({'id':row['id'],
                    'title':CryptoService.decrypt_vault_item(row['title_enc'],master_key),
                    'content':CryptoService.decrypt_vault_item(row['content_enc'],master_key),
                    'created_at':row['created_at']})
            except Exception:
                notes.append({'id':row['id'],'title':'[Wrong key]','content':'***','created_at':row['created_at']})
    return render_template('dashboard/notes.html', user=user, notes=notes,
                           unlocked=unlocked, master_key=master_key, total=total)

# ─── SECURE SHARING ──────────────────────────────────────────────────────────

@main.route('/share', methods=['GET','POST'])
@login_required
def secure_share():
    from flask import current_app
    uid  = session['user_id']
    db   = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    shared_files = [dict(r) for r in db.execute(
        "SELECT * FROM shared_files WHERE user_id=? ORDER BY created_at DESC",(uid,)).fetchall()]
    db.close()
    if request.method == 'POST':
        f = request.files.get('file')
        if not f or f.filename=='':
            flash('No file selected.','error'); return redirect(request.url)
        password   = request.form.get('share_password','')
        days       = int(request.form.get('expiry_days',7))
        limit      = int(request.form.get('download_limit',10))
        data       = f.read()
        token      = secrets.token_urlsafe(32)
        filename   = token + '_' + f.filename
        filepath   = os.path.join(current_app.config['ENCRYPTED_FOLDER'], filename)
        pw_hash    = None
        if password:
            enc = CryptoService.aes_encrypt(data, password)
            with open(filepath,'w') as fp: json.dump({'protected':True,'data':enc,'original':f.filename},fp)
            pw_hash = hash_password(password)
        else:
            with open(filepath,'wb') as fp: fp.write(data)
        expiry = (datetime.utcnow() + timedelta(days=days)).isoformat()
        db2 = get_db()
        db2.execute("INSERT INTO shared_files (user_id,filename,original_name,share_token,password_hash,expiry_date,download_limit,file_size) VALUES (?,?,?,?,?,?,?,?)",
            (uid,filename,f.filename,token,pw_hash,expiry,limit,len(data)))
        db2.commit(); db2.close()
        log_action(uid,'FILE_SHARE',f'Shared: {f.filename}')
        flash(f'File shared! Token: {token}','success')
        return redirect(url_for('main.secure_share'))
    return render_template('dashboard/share.html', user=user, shared_files=shared_files)

@main.route('/share/download/<token>', methods=['GET','POST'])
def download_shared(token):
    from flask import current_app
    db = get_db()
    sf = db.execute("SELECT * FROM shared_files WHERE share_token=? AND is_active=1",(token,)).fetchone()
    db.close()
    if not sf: abort(404)
    sf = dict(sf)
    if sf['expiry_date'] and datetime.utcnow().isoformat() > sf['expiry_date']:
        return render_template('shared_expired.html')
    if sf['download_limit'] > 0 and sf['download_count'] >= sf['download_limit']:
        return render_template('shared_expired.html')
    if request.method == 'POST' or not sf['password_hash']:
        password = request.form.get('password','')
        filepath = os.path.join(current_app.config['ENCRYPTED_FOLDER'], sf['filename'])
        if sf['password_hash']:
            if not check_password(sf['password_hash'], password):
                flash('Incorrect password.','error')
                return render_template('dashboard/shared_download.html', sf=sf)
            with open(filepath) as fp: pkg = json.load(fp)
            try:
                enc = pkg['data']
                data = CryptoService.aes_decrypt(enc['ciphertext'],enc['salt'],enc['iv'],password)
            except Exception:
                flash('Decryption failed.','error')
                return render_template('dashboard/shared_download.html', sf=sf)
        else:
            with open(filepath,'rb') as fp: data = fp.read()
        db2 = get_db()
        db2.execute("UPDATE shared_files SET download_count=download_count+1 WHERE id=?",(sf['id'],))
        db2.commit(); db2.close()
        return send_file(io.BytesIO(data), as_attachment=True, download_name=sf['original_name'])
    return render_template('dashboard/shared_download.html', sf=sf)

@main.route('/share/<int:sf_id>/revoke', methods=['POST'])
@login_required
def revoke_share(sf_id):
    uid = session['user_id']
    db  = get_db()
    db.execute("UPDATE shared_files SET is_active=0 WHERE id=? AND user_id=?",(sf_id,uid))
    db.commit(); db.close()
    flash('Share link revoked.','warning')
    return redirect(url_for('main.secure_share'))

# ─── AUDIT LOGS ──────────────────────────────────────────────────────────────

@main.route('/audit-logs')
@login_required
def audit_logs():
    uid  = session['user_id']
    page = request.args.get('page',1,type=int)
    per  = 20
    db   = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    total = db.execute("SELECT COUNT(*) as c FROM audit_logs WHERE user_id=?",(uid,)).fetchone()['c']
    rows  = [dict(r) for r in db.execute(
        "SELECT * FROM audit_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT ? OFFSET ?",
        (uid, per, (page-1)*per)).fetchall()]
    db.close()
    pages = (total + per - 1) // per
    return render_template('dashboard/audit_logs.html', user=user, logs=rows,
                           page=page, pages=pages, total=total)

# ─── SETTINGS ────────────────────────────────────────────────────────────────

@main.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    uid = session['user_id']
    db  = get_db()
    user = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    db.close()
    if request.method == 'POST':
        r = change_password(uid, request.form.get('old_password',''), request.form.get('new_password',''))
        flash(r['message'], 'success' if r['success'] else 'error')
    return render_template('dashboard/settings.html', user=user)

# ─── ADMIN ───────────────────────────────────────────────────────────────────

@main.route('/admin')
@admin_required
def admin_panel():
    uid = session['user_id']
    db  = get_db()
    user  = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    users = [dict(r) for r in db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()]
    total_logs = db.execute("SELECT COUNT(*) as c FROM audit_logs").fetchone()['c']
    total_keys = db.execute("SELECT COUNT(*) as c FROM key_pairs").fetchone()['c']
    active_users = db.execute("SELECT COUNT(*) as c FROM users WHERE is_active=1").fetchone()['c']
    db.close()
    return render_template('admin/admin.html', user=user, users=users,
                           total_logs=total_logs, total_keys=total_keys, active_users=active_users)

@main.route('/admin/user/<int:uid>/toggle', methods=['POST'])
@admin_required
def toggle_user(uid):
    db = get_db()
    u  = db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone()
    if u:
        db.execute("UPDATE users SET is_active=? WHERE id=?",(0 if u['is_active'] else 1, uid))
        db.commit()
        flash(f'User {"disabled" if u["is_active"] else "enabled"}.','info')
    db.close()
    return redirect(url_for('main.admin_panel'))

@main.route('/admin/user/<int:uid>/delete', methods=['POST'])
@admin_required
def delete_user(uid):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?",(uid,))
    db.commit(); db.close()
    flash('User deleted.','warning')
    return redirect(url_for('main.admin_panel'))

# ─── ERROR HANDLERS ──────────────────────────────────────────────────────────

@main.app_errorhandler(404)
def not_found(e): return render_template('errors/404.html'), 404
@main.app_errorhandler(403)
def forbidden(e): return render_template('errors/403.html'), 403
@main.app_errorhandler(500)
def server_error(e): return render_template('errors/500.html'), 500
