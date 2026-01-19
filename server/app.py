import os
import datetime
from flask import Flask, request, jsonify
from database import db, LicenseKey, init_db
from utils import generate_key

app = Flask(__name__)
# Secret key for admin actions (in production, use environment variable)
ADMIN_SECRET = "super_secret_admin_key_123" 

init_db(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "time": datetime.datetime.now(datetime.timezone.utc).isoformat()})

# --- CLIENT ENDPOINTS ---

@app.route('/validate', methods=['POST'])
def validate_license():
    data = request.json
    key_code = data.get('key')
    hwid = data.get('hwid')

    if not key_code or not hwid:
        return jsonify({"valid": False, "message": "Missing key or HWID"}), 400

    key = LicenseKey.query.filter_by(key_code=key_code).first()

    if not key:
        return jsonify({"valid": False, "message": "Invalid Key"}), 404

    if key.is_banned:
        return jsonify({"valid": False, "message": "Key Banned"}), 403

    # Check HWID
    if key.hwid and key.hwid != hwid:
        return jsonify({"valid": False, "message": "HWID Mismatch. Key locked to another device."}), 403

    # Activation (First Use)
    now = datetime.datetime.now(datetime.timezone.utc)
    if not key.activated_at:
        key.activated_at = now
        key.hwid = hwid # Bind HWID
        
        if key.key_type == 'timed' and key.duration_seconds:
            key.expires_at = now + datetime.timedelta(seconds=key.duration_seconds)
        
        db.session.commit()

    # Expiration Check
    if not key.is_valid():
        # Auto-delete expired keys? User req says: "Expired keys: Automatically deleted from server."
        if key.expires_at and now > key.expires_at:
             db.session.delete(key)
             db.session.commit()
             return jsonify({"valid": False, "message": "Key Expired and Deleted"}), 403
        
        return jsonify({"valid": False, "message": "Key is invalid"}), 403

    # Success Response
    response = {
        "valid": True,
        "type": key.key_type,
        "expires_at": key.expires_at.isoformat() if key.expires_at else None,
        "server_time": now.isoformat()
    }
    return jsonify(response)

# --- ADMIN / BOT ENDPOINTS ---

def check_admin(req):
    token = req.headers.get("Authorization")
    return token == f"Bearer {ADMIN_SECRET}"

@app.route('/create_key', methods=['POST'])
def create_key():
    if not check_admin(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    duration_str = data.get('duration') # "1d", "30d", "lifetime"
    
    key_type = 'timed'
    duration_seconds = 0
    
    if duration_str.lower() == 'lifetime':
        key_type = 'lifetime'
        duration_seconds = None
    else:
        # Simple parser
        try:
            if duration_str.endswith('d'):
                days = int(duration_str[:-1])
                duration_seconds = days * 86400
            elif duration_str.endswith('h'):
                hours = int(duration_str[:-1])
                duration_seconds = hours * 3600
            elif duration_str.endswith('m'): # mins
                mins = int(duration_str[:-1])
                duration_seconds = mins * 60
            else:
                 # Default to days if just number
                 duration_seconds = int(duration_str) * 86400
        except:
             return jsonify({"error": "Invalid duration format. Use '1d', '24h', or 'lifetime'"}), 400

    new_key_code = generate_key()
    new_key = LicenseKey(
        key_code=new_key_code,
        key_type=key_type,
        duration_seconds=duration_seconds
    )
    
    db.session.add(new_key)
    db.session.commit()
    
    return jsonify({
        "key": new_key_code,
        "type": key_type,
        "duration": duration_str
    })

@app.route('/reset_hwid', methods=['POST'])
def reset_hwid():
    if not check_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    key_code = data.get('key')
    
    key = LicenseKey.query.filter_by(key_code=key_code).first()
    if not key:
        return jsonify({"error": "Key not found"}), 404
        
    key.hwid = None
    db.session.commit()
    
    return jsonify({"success": True, "message": "HWID Reset Successful"})

@app.route('/delete_key', methods=['POST'])
def delete_key():
    if not check_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    key_code = data.get('key')
    
    key = LicenseKey.query.filter_by(key_code=key_code).first()
    if not key:
        return jsonify({"error": "Key not found"}), 404
        
    db.session.delete(key)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Key Deleted"})

@app.route('/key_info', methods=['GET'])
def key_info():
    if not check_admin(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    key_code = request.args.get('key')
    key = LicenseKey.query.filter_by(key_code=key_code).first()
    
    if not key:
        return jsonify({"found": False}), 404
        
    return jsonify({"found": True, "data": key.to_dict()})

if __name__ == '__main__':
    # Localhost for now.
    app.run(host='0.0.0.0', port=5001, debug=True)
