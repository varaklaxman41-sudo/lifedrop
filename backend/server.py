"""
Lifedrop - REST API Server & Full-Stack Application Host
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add parent folder to sys.path so backend modules import properly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.db import init_db
from backend.models import (
    DonorModel,
    RequestModel,
    InventoryModel,
    StatsModel,
    AssistantModel,
    ChatModel,
    COMPATIBILITY_RULES
)

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
CORS(app)  # Enable Cross-Origin Resource Sharing for API

# Initialize SQLite database on startup
init_db()


# ==========================================
# 🌐 Static Frontend Routes
# ==========================================

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/download/presentation')
@app.route('/download/ppt')
def download_presentation():
    return send_from_directory(BASE_DIR, 'Lifedrop_Shivamogga_Project_Presentation.pptx', as_attachment=True)

@app.route('/download/document')
@app.route('/download/doc')
@app.route('/download/word')
def download_word_document():
    return send_from_directory(BASE_DIR, 'Lifedrop_Shivamogga_Project_Documentation.docx', as_attachment=True)

@app.route('/<path:path>')
def serve_static(path):
    # Exclude backend and hidden files from direct public static serving
    if path.startswith('backend') or path.startswith('.'):
        return jsonify({'error': 'Forbidden'}), 403
    if os.path.exists(os.path.join(BASE_DIR, path)):
        return send_from_directory(BASE_DIR, path)
    return jsonify({'error': 'Not found'}), 404


# ==========================================
# 📊 System Health & Stats APIs
# ==========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'online',
        'service': 'Lifedrop Emergency Network API',
        'version': '2.0.0',
        'database': 'SQLite3 (lifedrop.db)'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    overview = StatsModel.get_overview()
    return jsonify({'success': True, 'data': overview})


# ==========================================
# 🩸 Blood Compatibility & Inventory APIs
# ==========================================

@app.route('/api/compatibility', methods=['GET'])
def get_compatibility():
    return jsonify({
        'success': True,
        'data': COMPATIBILITY_RULES
    })

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    inventory = InventoryModel.get_all()
    return jsonify({'success': True, 'data': inventory})

@app.route('/api/inventory/<blood_group>', methods=['PATCH'])
def update_inventory(blood_group):
    data = request.get_json() or {}
    updated = InventoryModel.update(
        blood_group=blood_group,
        units=data.get('units_available', data.get('unitsAvailable')),
        daily_demand=data.get('daily_demand', data.get('dailyDemand')),
        status=data.get('status'),
        capacity_pct=data.get('capacity_pct', data.get('capacityPct'))
    )
    if not updated:
        return jsonify({'success': False, 'error': f"Blood group '{blood_group}' not found"}), 404
    return jsonify({'success': True, 'data': updated})


# ==========================================
# 👥 Donors APIs
# ==========================================

def clean_blood_group(bg):
    if not bg:
        return ''
    return bg.replace(' ', '+').strip().upper()

@app.route('/api/donors', methods=['GET'])
def list_donors():
    blood_group = clean_blood_group(request.args.get('bloodGroup'))
    city = request.args.get('city')
    available_only = request.args.get('available', '').lower() in ('true', '1')

    donors = DonorModel.get_all(blood_group=blood_group, city=city, available_only=available_only)
    return jsonify({'success': True, 'count': len(donors), 'data': donors})

@app.route('/api/donors', methods=['POST'])
def register_donor():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Missing JSON body'}), 400

    required_fields = ['name', 'bloodGroup', 'city', 'phone']
    # Accept both camelCase and snake_case
    for field in required_fields:
        alt_field = 'blood_group' if field == 'bloodGroup' else field
        if not data.get(field) and not data.get(alt_field):
            return jsonify({'success': False, 'error': f"Field '{field}' is required"}), 400

    try:
        new_donor = DonorModel.create(data)
        return jsonify({
            'success': True,
            'message': 'Donor successfully registered into Lifedrop network',
            'data': new_donor
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/donors/<donor_id>', methods=['GET'])
def get_donor(donor_id):
    donor = DonorModel.get_by_id(donor_id)
    if not donor:
        return jsonify({'success': False, 'error': 'Donor not found'}), 404
    return jsonify({'success': True, 'data': donor})

@app.route('/api/donors/<donor_id>/status', methods=['PATCH'])
def update_donor_status(donor_id):
    data = request.get_json() or {}
    available = data.get('available')
    increment_donations = data.get('incrementDonations', False)
    updated = DonorModel.update_status(donor_id, available=available, increment_donations=increment_donations)
    if not updated:
        return jsonify({'success': False, 'error': 'Donor not found'}), 404
    return jsonify({'success': True, 'data': updated})

@app.route('/api/donors/match', methods=['GET'])
def match_donors():
    blood_group = clean_blood_group(request.args.get('bloodGroup'))
    city = request.args.get('city')
    if not blood_group:
        return jsonify({'success': False, 'error': 'bloodGroup parameter is required'}), 400

    matching = DonorModel.find_compatible(blood_group, city)
    return jsonify({'success': True, 'count': len(matching), 'data': matching})


# ==========================================
# 🚨 Emergency Requests & Tracking APIs
# ==========================================

@app.route('/api/requests', methods=['GET'])
def list_requests():
    urgency = request.args.get('urgency')
    status = request.args.get('status')
    city = request.args.get('city')
    requests_list = RequestModel.get_all(urgency=urgency, status=status, city=city)
    return jsonify({'success': True, 'count': len(requests_list), 'data': requests_list})

@app.route('/api/requests', methods=['POST'])
def create_request():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Missing JSON body'}), 400

    required = ['bloodGroup', 'hospital', 'city', 'contactPhone']
    for field in required:
        alt_field = 'blood_group' if field == 'bloodGroup' else ('contact_phone' if field == 'contactPhone' else field)
        if not data.get(field) and not data.get(alt_field):
            return jsonify({'success': False, 'error': f"Field '{field}' is required"}), 400

    try:
        new_req = RequestModel.create(data)
        return jsonify({
            'success': True,
            'message': f"Emergency broadcast initiated for {new_req['blood_group']}",
            'data': new_req
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/requests/<request_id>', methods=['GET'])
def get_request(request_id):
    req_obj = RequestModel.get_by_id(request_id)
    if not req_obj:
        return jsonify({'success': False, 'error': 'Request not found'}), 404
    return jsonify({'success': True, 'data': req_obj})

@app.route('/api/requests/<request_id>', methods=['PATCH'])
def update_request(request_id):
    data = request.get_json() or {}
    status = data.get('status')
    confirmed_count = data.get('donorsConfirmed', data.get('donors_confirmed'))
    updated = RequestModel.update_status(request_id, status=status, confirmed_count=confirmed_count)
    if not updated:
        return jsonify({'success': False, 'error': 'Request not found'}), 404
    return jsonify({'success': True, 'data': updated})

@app.route('/api/requests/<request_id>/timeline', methods=['POST'])
def add_timeline_event(request_id):
    data = request.get_json() or {}
    event_text = data.get('event')
    if not event_text:
        return jsonify({'success': False, 'error': "Field 'event' is required"}), 400
    timeline_entry = RequestModel.add_timeline_event(request_id, event_text)
    return jsonify({'success': True, 'data': timeline_entry}), 201


# ==========================================
# 🤖 Lifedrop AI Assistant / Triage API
# ==========================================

@app.route('/api/assistant/chat', methods=['POST'])
def assistant_chat():
    data = request.get_json() or {}
    user_msg = data.get('message', data.get('prompt', data.get('user_message', ''))).strip()
    session_id = data.get('session_id', data.get('sessionId', 'default'))

    if not user_msg:
        return jsonify({
            'success': False,
            'error': 'Message cannot be empty',
            'reply': "Please type a query or choose one of the options below.",
            'actions': ['🚨 Urgent Blood Request', '❤️ Register as Donor', '🔍 Track Request REQ-1001', '🩸 Check Inventory']
        }), 400

    try:
        response_payload = AssistantModel.process_message(user_msg, session_id=session_id)
        return jsonify(response_payload)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'reply': "I encountered an error processing your request. Please try again or contact emergency hotline (108).",
            'intent': 'error',
            'actions': ['🚨 Urgent Blood Request', 'Restart Conversation']
        }), 500

@app.route('/api/assistant/history/<session_id>', methods=['GET'])
def get_assistant_history(session_id):
    limit = int(request.args.get('limit', 50))
    history = ChatModel.get_history(session_id, limit=limit)
    return jsonify({
        'success': True,
        'session_id': session_id,
        'count': len(history),
        'data': history
    })

@app.route('/api/assistant/reset', methods=['POST'])
def reset_assistant():
    data = request.get_json() or {}
    session_id = data.get('session_id', data.get('sessionId', 'default'))
    AssistantModel.reset_session(session_id)
    return jsonify({
        'success': True,
        'message': 'Assistant session reset successfully',
        'session_id': session_id
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"  Lifedrop Full-Stack Server Running on http://127.0.0.1:{port}")
    print(f"  Serving static frontend from {BASE_DIR}")
    print(f"  Database connected: lifedrop.db")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)
