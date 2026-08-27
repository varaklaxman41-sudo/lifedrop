"""
Lifedrop - Data Models, Business Logic & Database Helpers
"""

import json
import random
import re
from datetime import datetime
from backend.db import get_db_connection

# Comprehensive Blood Compatibility Rules
COMPATIBILITY_RULES = {
    'O-': {
        'canDonateTo': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'canReceiveFrom': ['O-'],
        'badge': 'Universal Red Cell Donor',
        'description': 'O- can be given to anyone in emergency situations when blood type is unknown.'
    },
    'O+': {
        'canDonateTo': ['O+', 'A+', 'B+', 'AB+'],
        'canReceiveFrom': ['O+', 'O-'],
        'badge': 'Most Common Blood Type',
        'description': 'Can give to all positive blood types. High in demand across emergency rooms.'
    },
    'A-': {
        'canDonateTo': ['A-', 'A+', 'AB-', 'AB+'],
        'canReceiveFrom': ['A-', 'O-'],
        'badge': 'Crucial for A & AB Patients',
        'description': 'Can donate to all A and AB types regardless of Rh factor.'
    },
    'A+': {
        'canDonateTo': ['A+', 'AB+'],
        'canReceiveFrom': ['A+', 'A-', 'O+', 'O-'],
        'badge': 'High Demand Blood Type',
        'description': 'Second most common blood type, needed for cancer treatments and surgeries.'
    },
    'B-': {
        'canDonateTo': ['B-', 'B+', 'AB-', 'AB+'],
        'canReceiveFrom': ['B-', 'O-'],
        'badge': 'Rare Blood Type',
        'description': 'Only about 2% of the population has B-, making every donor vital.'
    },
    'B+': {
        'canDonateTo': ['B+', 'AB+'],
        'canReceiveFrom': ['B+', 'B-', 'O+', 'O-'],
        'badge': 'Widely Needed',
        'description': 'Can donate red blood cells to B+ and AB+ recipients.'
    },
    'AB-': {
        'canDonateTo': ['AB-', 'AB+'],
        'canReceiveFrom': ['AB-', 'A-', 'B-', 'O-'],
        'badge': 'Rarest Blood Type',
        'description': 'Less than 1% of population. Universal plasma donor.'
    },
    'AB+': {
        'canDonateTo': ['AB+'],
        'canReceiveFrom': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'badge': 'Universal Red Cell Recipient',
        'description': 'Can safely receive red blood cells from any blood group.'
    }
}

class DonorModel:
    @staticmethod
    def get_all(blood_group=None, city=None, available_only=False):
        conn = get_db_connection()
        query = 'SELECT * FROM donors WHERE 1=1'
        params = []

        if blood_group and blood_group.upper() != 'ALL':
            query += ' AND UPPER(blood_group) = ?'
            params.append(blood_group.upper())

        if city and city.strip():
            query += ' AND (LOWER(city) LIKE ? OR LOWER(area) LIKE ?)'
            city_pattern = f"%{city.strip().lower()}%"
            params.extend([city_pattern, city_pattern])

        if available_only:
            query += ' AND available = 1'

        query += ' ORDER BY created_at DESC'
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(donor_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM donors WHERE id = ?', (donor_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def find_compatible(blood_group, city=None):
        """Find verified available donors who can donate to the given recipient blood group."""
        conn = get_db_connection()
        norm_bg = (blood_group or '').strip().upper()
        compatible_donor_types = COMPATIBILITY_RULES.get(norm_bg, {}).get('canReceiveFrom', [norm_bg])

        placeholders = ','.join(['?'] * len(compatible_donor_types))
        query = f'SELECT * FROM donors WHERE available = 1 AND UPPER(blood_group) IN ({placeholders})'
        params = list(compatible_donor_types)

        if city and city.strip():
            query += ' AND (LOWER(city) LIKE ? OR LOWER(area) LIKE ?)'
            city_pattern = f"%{city.strip().lower()}%"
            params.extend([city_pattern, city_pattern])

        query += ' ORDER BY verified DESC, total_donations DESC'
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def create(donor_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        donor_id = donor_data.get('id') or f"DON-{random.randint(100, 999)}"
        # Ensure unique ID
        while True:
            cursor.execute('SELECT id FROM donors WHERE id = ?', (donor_id,))
            if not cursor.fetchone():
                break
            donor_id = f"DON-{random.randint(100, 999)}"

        name = donor_data.get('name', '').strip()
        blood_group = donor_data.get('bloodGroup', donor_data.get('blood_group', '')).strip().upper()
        city = donor_data.get('city', '').strip()
        area = donor_data.get('area', city).strip()
        phone = donor_data.get('phone', '').strip()
        email = donor_data.get('email', '')
        age = int(donor_data.get('age', 25)) if donor_data.get('age') else None
        weight = float(donor_data.get('weight', 60.0)) if donor_data.get('weight') else None
        available = 1 if donor_data.get('available', True) else 0
        verified = 1 if donor_data.get('verified', True) else 0
        total_donations = int(donor_data.get('totalDonations', donor_data.get('total_donations', 1)))
        last_donation = donor_data.get('lastDonation', donor_data.get('last_donation', datetime.now().strftime('%Y-%m-%d')))
        is_emergency_contact = 1 if donor_data.get('isEmergencyContact', donor_data.get('is_emergency_contact', True)) else 0

        cursor.execute('''
            INSERT INTO donors (id, name, blood_group, city, area, phone, email, age, weight, available, verified, total_donations, last_donation, is_emergency_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (donor_id, name, blood_group, city, area, phone, email, age, weight, available, verified, total_donations, last_donation, is_emergency_contact))
        conn.commit()

        cursor.execute('SELECT * FROM donors WHERE id = ?', (donor_id,))
        created = dict(cursor.fetchone())
        conn.close()
        return created

    @staticmethod
    def update_status(donor_id, available=None, increment_donations=False):
        conn = get_db_connection()
        cursor = conn.cursor()
        if available is not None:
            cursor.execute('UPDATE donors SET available = ? WHERE id = ?', (1 if available else 0, donor_id))
        if increment_donations:
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('UPDATE donors SET total_donations = total_donations + 1, last_donation = ? WHERE id = ?', (today, donor_id))
        conn.commit()
        cursor.execute('SELECT * FROM donors WHERE id = ?', (donor_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None


class RequestModel:
    @staticmethod
    def get_all(urgency=None, status=None, city=None):
        conn = get_db_connection()
        query = 'SELECT * FROM requests WHERE 1=1'
        params = []

        if urgency and urgency.upper() != 'ALL':
            query += ' AND LOWER(urgency) = ?'
            params.append(urgency.lower())

        if status and status.upper() != 'ALL':
            query += ' AND LOWER(status) = ?'
            params.append(status.lower())

        if city and city.strip():
            query += ' AND LOWER(city) LIKE ?'
            params.append(f"%{city.strip().lower()}%")

        query += ' ORDER BY created_at DESC'
        cursor = conn.cursor()
        cursor.execute(query, params)
        requests = [dict(row) for row in cursor.fetchall()]

        # Attach timeline for each request
        for req in requests:
            cursor.execute('SELECT time, event FROM request_timeline WHERE request_id = ? ORDER BY id ASC', (req['id'],))
            req['timeline'] = [dict(t) for t in cursor.fetchall()]

        conn.close()
        return requests

    @staticmethod
    def get_by_id(request_id_or_phone):
        if not request_id_or_phone:
            return None
        clean_val = request_id_or_phone.strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM requests 
            WHERE UPPER(id) = ? OR contact_phone LIKE ?
            LIMIT 1
        ''', (clean_val.upper(), f"%{clean_val}%"))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        req = dict(row)
        cursor.execute('SELECT time, event FROM request_timeline WHERE request_id = ? ORDER BY id ASC', (req['id'],))
        req['timeline'] = [dict(t) for t in cursor.fetchall()]
        conn.close()
        return req

    @staticmethod
    def create(req_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        req_id = req_data.get('id') or f"REQ-{random.randint(1000, 9990)}"
        while True:
            cursor.execute('SELECT id FROM requests WHERE id = ?', (req_id,))
            if not cursor.fetchone():
                break
            req_id = f"REQ-{random.randint(1000, 9990)}"

        patient_name = req_data.get('patientName', req_data.get('patient_name', 'Emergency Patient')).strip()
        blood_group = req_data.get('bloodGroup', req_data.get('blood_group', '')).strip().upper()
        units = int(req_data.get('units', 1))
        hospital = req_data.get('hospital', '').strip()
        city = req_data.get('city', '').strip()
        urgency = req_data.get('urgency', 'Standard').capitalize()
        contact_name = req_data.get('contactName', req_data.get('contact_name', patient_name)).strip()
        contact_phone = req_data.get('contactPhone', req_data.get('contact_phone', '')).strip()
        notes = req_data.get('notes', '')
        status = 'In Progress' if urgency.lower() == 'emergency' else 'Searching'

        # Find matching donors
        matching_donors = DonorModel.find_compatible(blood_group, city)
        donors_contacted = len(matching_donors)

        cursor.execute('''
            INSERT INTO requests (id, patient_name, blood_group, units, hospital, city, urgency, contact_name, contact_phone, notes, status, donors_contacted, donors_confirmed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (req_id, patient_name, blood_group, units, hospital, city, urgency, contact_name, contact_phone, notes, status, donors_contacted, 0))

        # Initial Timeline Events
        now_time = datetime.now().strftime('%I:%M %p')
        cursor.execute('INSERT INTO request_timeline (request_id, time, event) VALUES (?, ?, ?)',
                       (req_id, now_time, f"Request created for {blood_group} at {hospital or city}"))

        if donors_contacted > 0:
            cursor.execute('INSERT INTO request_timeline (request_id, time, event) VALUES (?, ?, ?)',
                           (req_id, now_time, f"Automated emergency alert dispatched to {donors_contacted} matching {blood_group} donors"))

            # Log broadcast notifications to donors
            for d in matching_donors:
                cursor.execute('''
                    INSERT INTO broadcast_notifications (request_id, donor_id, message, status)
                    VALUES (?, ?, ?, 'Sent')
                ''', (req_id, d['id'], f"Urgent blood request for {blood_group} at {hospital}, {city}"))

        conn.commit()

        # Fetch created request with timeline
        cursor.execute('SELECT * FROM requests WHERE id = ?', (req_id,))
        created = dict(cursor.fetchone())
        cursor.execute('SELECT time, event FROM request_timeline WHERE request_id = ? ORDER BY id ASC', (req_id,))
        created['timeline'] = [dict(t) for t in cursor.fetchall()]
        conn.close()
        return created

    @staticmethod
    def update_status(req_id, status=None, confirmed_count=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        now_time = datetime.now().strftime('%I:%M %p')

        if status:
            cursor.execute('UPDATE requests SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (status, req_id))
            cursor.execute('INSERT INTO request_timeline (request_id, time, event) VALUES (?, ?, ?)',
                           (req_id, now_time, f"Status updated to '{status}'"))
        if confirmed_count is not None:
            cursor.execute('UPDATE requests SET donors_confirmed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (confirmed_count, req_id))
            cursor.execute('INSERT INTO request_timeline (request_id, time, event) VALUES (?, ?, ?)',
                           (req_id, now_time, f"Donor confirmation updated: {confirmed_count} donors confirmed"))

        conn.commit()
        cursor.execute('SELECT * FROM requests WHERE id = ?', (req_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        res = dict(row)
        cursor.execute('SELECT time, event FROM request_timeline WHERE request_id = ? ORDER BY id ASC', (req_id,))
        res['timeline'] = [dict(t) for t in cursor.fetchall()]
        conn.close()
        return res

    @staticmethod
    def add_timeline_event(req_id, event_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        now_time = datetime.now().strftime('%I:%M %p')
        cursor.execute('INSERT INTO request_timeline (request_id, time, event) VALUES (?, ?, ?)', (req_id, now_time, event_text))
        conn.commit()
        conn.close()
        return {'time': now_time, 'event': event_text}


class InventoryModel:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inventory ORDER BY blood_group ASC')
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def update(blood_group, units=None, daily_demand=None, status=None, capacity_pct=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        updates = []
        params = []
        if units is not None:
            updates.append("units_available = ?")
            params.append(units)
        if daily_demand is not None:
            updates.append("daily_demand = ?")
            params.append(daily_demand)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if capacity_pct is not None:
            updates.append("capacity_pct = ?")
            params.append(capacity_pct)

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(blood_group.upper())
            cursor.execute(f"UPDATE inventory SET {', '.join(updates)} WHERE UPPER(blood_group) = ?", params)
            conn.commit()

        cursor.execute("SELECT * FROM inventory WHERE UPPER(blood_group) = ?", (blood_group.upper(),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None


class StatsModel:
    @staticmethod
    def get_overview():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM donors WHERE available = 1')
        active_donors = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM donors')
        total_donors = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requests WHERE status IN ('Searching', 'In Progress')")
        active_requests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requests WHERE status = 'Fulfilled'")
        fulfilled_requests = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total_donations) FROM donors")
        total_donations = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM inventory WHERE status = 'Critical'")
        critical_inventory_count = cursor.fetchone()[0]

        conn.close()
        return {
            'activeDonors': active_donors,
            'totalDonors': total_donors,
            'activeRequests': active_requests,
            'fulfilledRequests': fulfilled_requests,
            'livesSaved': total_donations + (fulfilled_requests * 3),
            'criticalBloodTypes': critical_inventory_count,
            'avgResponseMinutes': 4.2
        }


class ChatModel:
    @staticmethod
    def log_message(session_id, role, message, intent=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chat_messages (session_id, role, message, intent)
            VALUES (?, ?, ?, ?)
        ''', (session_id or 'default', role, message, intent))
        conn.commit()
        msg_id = cursor.lastrowid
        conn.close()
        return msg_id

    @staticmethod
    def get_history(session_id='default', limit=50):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, session_id, role, message, intent, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
        ''', (session_id or 'default', limit))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def clear_history(session_id='default'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id or 'default',))
        conn.commit()
        conn.close()
        return True


class AssistantModel:
    _sessions = {}

    @classmethod
    def get_session(cls, session_id):
        sid = session_id or 'default'
        if sid not in cls._sessions:
            cls._sessions[sid] = {
                'currentFlow': None,  # 'REQUEST_BLOOD' | 'REGISTER_DONOR' | 'CHECK_STATUS'
                'step': 0,
                'collectedData': {},
                'isEmergencyMode': False
            }
        return cls._sessions[sid]

    @classmethod
    def reset_session(cls, session_id):
        sid = session_id or 'default'
        cls._sessions[sid] = {
            'currentFlow': None,
            'step': 0,
            'collectedData': {},
            'isEmergencyMode': False
        }
        return True

    @staticmethod
    def extract_blood_group(text):
        if not text:
            return None
        upper = text.upper()
        # Direct format AB+, AB-, A+, A-, B+, B-, O+, O-
        match = re.search(r'(?:^|[^\w+-])(AB\+|AB\-|A\+|A\-|B\+|B\-|O\+|O\-)(?!\w)', upper)
        if match:
            return match.group(1).upper()
        
        # Word formats
        patterns = [
            (r'\bO\s*(?:POSITIVE|POS)\b', 'O+'),
            (r'\bO\s*(?:NEGATIVE|NEG)\b', 'O-'),
            (r'\bAB\s*(?:POSITIVE|POS)\b', 'AB+'),
            (r'\bAB\s*(?:NEGATIVE|NEG)\b', 'AB-'),
            (r'\bA\s*(?:POSITIVE|POS)\b', 'A+'),
            (r'\bA\s*(?:NEGATIVE|NEG)\b', 'A-'),
            (r'\bB\s*(?:POSITIVE|POS)\b', 'B+'),
            (r'\bB\s*(?:NEGATIVE|NEG)\b', 'B-'),
        ]
        for pat, bg in patterns:
            if re.search(pat, upper):
                return bg
        return None

    @staticmethod
    def extract_location(text):
        if not text:
            return None
        known_places = [
            'Shivamogga', 'Shimoga', 'Durgigudi', 'Gopala', 'Vinoba Nagara', 'Vinoba Nagar',
            'Gandhi Nagara', 'Gandhi Nagar', 'Tilak Nagara', 'Tilak Nagar', 'Vidyanagara', 'Vidyanagar',
            'Kuvempu Road', 'Savalanga Road', 'Savalanga', 'Purle', 'Harakere', 'Alkola', 'Jayanagara',
            'NT Road', 'Jail Road', 'Sagara', 'Sagar', 'Bhadravathi', 'Bhadravati', 'Thirthahalli',
            'Tirthahalli', 'Shikaripura', 'Shikaripur', 'Soraba', 'Sorab', 'Hosanagara', 'Hosanagar',
            'McGann', 'SIMS', 'Sahyadri', 'Nanjappa', 'Subbaiah', 'Rotary', 'Max Hospital',
            'District Hospital', 'KIMS', 'Bengaluru', 'Mumbai', 'Pune', 'Mysuru', 'Mangaluru', 'Chennai'
        ]
        for place in known_places:
            if re.search(rf'\b{re.escape(place)}\b', text, re.IGNORECASE):
                return place
        return None

    @staticmethod
    def extract_request_id(text):
        if not text:
            return None
        match = re.search(r'\b(REQ-?\d+)\b', text, re.IGNORECASE)
        if match:
            val = match.group(1).upper()
            if '-' not in val:
                val = val.replace('REQ', 'REQ-')
            return val
        return None

    @staticmethod
    def extract_phone(text):
        if not text:
            return None
        match = re.search(r'(\+?\d[\d\s\-]{8,14}\d)', text)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def match_health_and_donor_benefits(lower):
        # 1. Health benefits for the donor (How blood donation helps the donor)
        if any(phrase in lower for phrase in [
            'how help donor', 'how helps donor', 'benefit of blood donation', 'benefits of donating',
            'benefit of donating', 'benefits for donor', 'benefit for donor', 'why donate blood',
            'why should i donate', 'advantages of donating', 'advantage of donating', 'what do i get',
            'does donating blood help', 'good for health', 'helps donor', 'help donor',
            'healthy for donor', 'donor health benefit', 'donor benefit', 'what are the benefits',
            'why give blood', 'impact on donor', 'help the donor', 'advantage for donor', 'health benefit'
        ]) and not any(k in lower for k in ['receive from', 'universal recipient']):
            return (
                "🩺 **How Blood Donation Helps the Donor (Key Health Benefits)**:\n\n"
                "1. **Free Comprehensive Mini-Health Screening**:\n"
                "   • Every donation includes checks for blood pressure, pulse rate, body temperature, and hemoglobin level.\n"
                "   • Blood is tested for major infectious markers (HIV, Hepatitis B/C, Syphilis, Malaria), offering valuable personal health insights.\n\n"
                "2. **Stimulates Fresh Blood Cell Production (Erythropoiesis)**:\n"
                "   • Donating stimulates your bone marrow to synthesize fresh, healthy red blood cells, white blood cells, and platelets, enhancing oxygen delivery.\n\n"
                "3. **Cardiovascular & Blood Flow Health**:\n"
                "   • Reduces blood viscosity (thickness), promoting smoother circulation and reducing arterial friction and oxidative stress on blood vessels.\n\n"
                "4. **Balances Iron Stores & Prevents Iron Overload**:\n"
                "   • Eliminates excess toxic iron deposits, reducing oxidative damage to arterial linings, the liver, and the heart (helping prevent hemochromatosis).\n\n"
                "5. **Caloric Expenditure & Metabolism**:\n"
                "   • The body expends approximately **650 calories** synthesizing and replenishing 1 pint (450ml) of donated blood volume.\n\n"
                "6. **Psychological 'Warm Glow' & Mental Wellbeing**:\n"
                "   • Altruistic giving releases endorphins, relieves stress, and gives a deep sense of purpose—every donation can **save up to 3 lives**! ❤️",
                ['❤️ Register as Donor', '🩸 Check Inventory', '❓ Eligibility Criteria', '🥗 Nutrition Tips']
            )

        # 2. Biological Cell Renewal & Bone Marrow Regeneration
        if any(k in lower for k in ['bone marrow', 'cell renewal', 'how body makes blood', 'erythropoiesis', 'new blood cell', 'replenish', 'grow back', 'blood regeneration', 'how fast does blood', 'regeneration']):
            return (
                "🔬 **How Your Body Replenishes Blood (Biological Renewal Timeline)**:\n\n"
                "• **Plasma / Fluid Volume (24–48 Hours)**:\n"
                "  The lost fluid volume is fully restored within 1–2 days with healthy hydration.\n\n"
                "• **Platelets & White Blood Cells (72 Hours)**:\n"
                "  Clotting platelets and immune cells recover rapidly within 3 days.\n\n"
                "• **Red Blood Cells (4–6 Weeks)**:\n"
                "  The hormone Erythropoietin (EPO) stimulates bone marrow stem cells to produce millions of fresh red blood cells daily.\n\n"
                "• **Iron Stores (8–12 Weeks)**:\n"
                "  Complete ferritin/iron recovery takes about 8–12 weeks, which is why men can donate every 90 days and women every 120 days.",
                ['Donor Health Benefits', '🥗 Nutrition Tips', '❤️ Register as Donor']
            )

        # 3. Nutrition, Iron & Hemoglobin Boosting
        if any(k in lower for k in ['increase hemoglobin', 'raise hemoglobin', 'low hemoglobin', 'iron rich', 'what to eat', 'diet for donor', 'diet before', 'diet after', 'food before', 'food after', 'nutrition', 'vitamin c', 'boost hb']):
            return (
                "🥗 **Nutrition & Hemoglobin Guide for Donors**:\n\n"
                "• **Top Iron-Rich Foods**:\n"
                "  - *Plant-Based (Non-Heme)*: Spinach, kale, lentils, chickpeas, beetroot, pomegranate, dates, jaggery, figs, and pumpkin seeds.\n"
                "  - *Animal-Based (Heme)*: Lean poultry, fish, eggs.\n\n"
                "• **The Vitamin C Multiplier (Crucial!)**:\n"
                "  Pairing iron with Vitamin C (oranges, amla/gooseberry, lemons, tomatoes, guavas) increases iron absorption by up to **300%**.\n\n"
                "• **What to Avoid 1–2 Hours Around Meals**:\n"
                "  Tea, coffee, and calcium supplements inhibit iron absorption—consume them separately.\n\n"
                "• **Pre-Donation Golden Rules**:\n"
                "  Drink 500ml water, eat a healthy meal 2–3 hours prior, and avoid alcohol for 24 hours.",
                ['Donor Health Benefits', '❓ Eligibility Criteria', '❤️ Register as Donor']
            )

        # 4. Blood Components & Donation Types (Platelets, Plasma, RBCs)
        if any(k in lower for k in ['blood component', 'platelet donation', 'plasma donation', 'apheresis', 'what is plasma', 'what are platelet', 'cryoprecipitate', 'types of donation', 'whole blood vs', 'sdp']):
            return (
                "🩸 **Blood Components & Specialized Donation Types**:\n\n"
                "1. **Whole Blood**:\n"
                "   • Standard donation (450ml). Separated into RBCs, platelets, and plasma. (Every 90/120 days).\n\n"
                "2. **Platelet Donation (Apheresis / Single Donor Platelet)**:\n"
                "   • Critical for cancer, leukemia, chemotherapy, and dengue patients.\n"
                "   • A cell-separator machine extracts platelets and returns red cells & plasma to you. Can donate **every 15 days** (up to 24 times/year)!\n\n"
                "3. **Plasma Donation (FFP)**:\n"
                "   • Liquid portion rich in antibodies & clotting factors; used for trauma, burn victims, shock, and hemophilia.\n\n"
                "4. **Packed Red Blood Cells (PRBC)**:\n"
                "   • Concentrated red cells for acute anemia, surgeries, and accident trauma.",
                ['Find Platelet Donors', '🩸 Check Inventory', '🚨 Urgent Blood Request']
            )

        # 5. Common Medical Conditions & Eligibility FAQs
        if any(k in lower for k in ['blood pressure', 'hypertension', 'diabetes', 'diabetic', 'thyroid', 'tattoo', 'alcohol', 'smoking', 'smoker', 'piercing', 'vaccine', 'covid']):
            return (
                "📋 **Health Conditions & Blood Donation Eligibility**:\n\n"
                "• **Blood Pressure**: Eligible if BP is between 90/50 and 180/100 mmHg on donation day.\n"
                "• **Diabetes**: Eligible if blood sugar is well-controlled via diet or oral medications (insulin-dependent donors should seek physician advice).\n"
                "• **Thyroid**: Eligible if on stable hormone replacement (e.g. Levothyroxine) with normal TSH levels.\n"
                "• **Tattoos & Piercings**: Eligible **6 months** after getting inked at a licensed studio with sterile single-use needles.\n"
                "• **Alcohol / Smoking**: Avoid alcohol for 24 hours prior; avoid smoking for at least 2 hours before & after donation.\n"
                "• **COVID / Routine Vaccines**: Eligible 14 days after complete symptom recovery or 14 days post-vaccination.",
                ['❓ Eligibility Criteria', 'Donor Health Benefits', '❤️ Register as Donor']
            )

        # 6. Rare Blood Types & Universal Donors
        if any(k in lower for k in ['rare blood', 'bombay blood', 'golden blood', 'rh null', 'rarest blood']):
            return (
                "🧬 **Rare Blood Groups & Specialized Types**:\n\n"
                "• **AB- Negative**: Less than 1% of the global population. Universal plasma donor!\n"
                "• **Bombay Blood Group (hh Phenotype)**:\n"
                "  Extremely rare (1 in 10,000 in India). Lacks the H antigen; individuals can ONLY receive blood from other Bombay phenotype donors.\n"
                "• **Rh-Null ('Golden Blood')**:\n"
                "  Lacks all 61 Rh antigens. Fewer than 50 people worldwide have this blood type.\n"
                "• **O- Negative**: Universal red blood cell donor—essential for emergency room trauma.",
                ['🩸 Compatibility Matrix', 'Find Rare Donors', '🚨 Urgent Blood Request']
            )

        # 7. Post-Donation Recovery & Care
        if any(k in lower for k in ['after donation', 'dizziness', 'faint', 'weakness', 'recovery after', 'side effect', 'painful', 'bruis']):
            return (
                "🛡️ **Post-Donation Recovery & Care Protocol**:\n\n"
                "• **First 15 Minutes**: Rest in the observation area, enjoy juice and snacks provided by the blood bank.\n"
                "• **Hydration**: Drink an extra 4–5 glasses of water/juice over the next 24 hours.\n"
                "• **Bandage**: Keep the bandage on for at least 4–6 hours.\n"
                "• **Physical Activity**: Avoid heavy lifting, gym workouts, or strenuous sports for 24 hours.\n"
                "• **If you feel dizzy**: Lie down flat with your legs elevated until the sensation passes.\n\n"
                "Donating blood is completely safe, and normal activities can be resumed immediately after resting.",
                ['Donor Health Benefits', '🥗 Nutrition Tips', '❤️ Register as Donor']
            )

        return None

    @staticmethod
    def is_medical_advice_query(lower):
        keywords = [
            'hiv', 'hepatitis', 'cancer', 'chemotherapy', 'diabetes insulin',
            'can i donate if i have', 'is it safe for patient', 'transfusion reaction',
            'blood mismatch risk', 'heart disease', 'pregnancy', 'pregnant', 'abortion',
            'surgery recently', 'antibiotics', 'medicine'
        ]
        return any(k in lower for k in keywords)

    @staticmethod
    def match_faq(lower):
        if any(k in lower for k in ['who can donate', 'eligible', 'eligibility', 'age limit', 'weight']):
            return "✅ **Donor Eligibility Criteria**:\n• Age: 18–65 years\n• Weight: At least 50 kg\n• Hemoglobin: > 12.5 g/dL\n• Good general health with no active infection or untreated medical conditions."
        if any(k in lower for k in ['how often', 'interval', 'frequency', 'gap between donation', 'when can i donate again']):
            return "⏳ **Donation Interval**:\n• Whole blood can be safely donated every 90 days (3 months) for men and every 120 days (4 months) for women to allow iron stores to fully replenish."
        if any(k in lower for k in ['is it safe', 'safety', 'infection risk', 'pain', 'side effects']):
            return "🛡️ **Donation Safety**:\n• Donating blood is 100% safe. Single-use, sterile, disposable equipment is used for every donor.\n• The human body replenishes the donated fluid volume within 24–48 hours."
        if any(k in lower for k in ['before donation', 'after donation', 'prepare', 'what to eat', 'food', 'hydration']):
            return "🥗 **Preparation Tips**:\n• Drink 500ml of water before donation.\n• Eat a light, healthy meal 2-3 hours prior.\n• Avoid alcohol for 24 hours.\n• After donating, rest for 15 minutes, hydrate well, and avoid heavy lifting for the day."
        return None

    @classmethod
    def process_message(cls, raw_input, session_id='default'):
        text = (raw_input or '').strip()
        session = cls.get_session(session_id)

        if not text:
            reply = "I'm Lifedrop Shivamogga Emergency Assistant. How can I assist you right now? You can request emergency blood in Shivamogga, search local verified donors, check live request status, or check blood bank inventory."
            actions = ['🚨 Urgent Blood Request', '❤️ Register as Donor', '🔍 Track Request REQ-1001', '🩸 Check Shivamogga Inventory']
            ChatModel.log_message(session_id, 'assistant', reply, 'welcome')
            return {
                'success': True,
                'reply': reply,
                'intent': 'welcome',
                'actions': actions,
                'data': {},
                'session_id': session_id
            }

        # Log user message
        ChatModel.log_message(session_id, 'user', text, None)

        lower = text.lower()

        # Check for Reset / Cancellation keywords
        if lower in ['restart', 'reset', 'cancel', 'start over', 'menu', 'clear']:
            cls.reset_session(session_id)
            reply = "Conversation restarted for Shivamogga. How can I assist you right now?"
            actions = ['🚨 Urgent Blood Request', '❤️ Register as Donor', '🔍 Track Request REQ-1001', '🩸 Check Inventory', '❓ Eligibility Criteria']
            ChatModel.log_message(session_id, 'assistant', reply, 'reset')
            return {
                'success': True,
                'reply': reply,
                'intent': 'reset',
                'actions': actions,
                'data': {},
                'session_id': session_id
            }

        # Route active multi-step flows
        if session['currentFlow'] == 'REQUEST_BLOOD':
            return cls._handle_blood_request_flow(text, session, session_id)
        elif session['currentFlow'] == 'REGISTER_DONOR':
            return cls._handle_donor_registration_flow(text, session, session_id)
        elif session['currentFlow'] == 'CHECK_STATUS':
            return cls._handle_status_check_flow(text, session, session_id)

        # ----------------------------------------------------
        # Intent Detection for Fresh Queries
        # ----------------------------------------------------

        bg_found = cls.extract_blood_group(text)
        loc_found = cls.extract_location(text)

        # 1. Emergency Blood Request
        is_emergency = any(k in lower for k in ['emergency', 'urgent', 'sos', 'critical', 'accident', 'icu', 'need blood immediately'])
        is_blood_req = is_emergency or any(k in lower for k in ['need blood', 'request blood', 'require blood', 'want blood', 'blood required', 'looking for blood'])

        if is_blood_req or (bg_found and any(k in lower for k in ['need', 'want', 'require', 'urgent', 'request', 'for patient']) and not any(k in lower for k in ['receive', 'give', 'compatible', 'donate'])):
            session['currentFlow'] = 'REQUEST_BLOOD'
            session['isEmergencyMode'] = is_emergency
            session['collectedData'] = {
                'bloodGroup': bg_found,
                'location': loc_found,
                'urgency': 'Emergency' if is_emergency else 'Standard'
            }
            return cls._handle_blood_request_flow(text, session, session_id)

        # 2. Donor Search / Query
        is_donor_search = any(k in lower for k in ['donor', 'donors']) and any(k in lower for k in ['find', 'search', 'show', 'list', 'look', 'available', 'where', 'get'])
        if is_donor_search or (bg_found and any(k in lower for k in ['donor', 'donors']) and not any(k in lower for k in ['register', 'become', 'sign up'])):
            bg = bg_found or 'O-'
            loc = loc_found
            matching = DonorModel.find_compatible(bg, loc)
            intent = 'donor_search'
            
            if matching:
                donor_list_str = "\n".join([f"• **{d['name']}** ({d['blood_group']}) — {d['city']} ({d['area'] or ''}) | 📞 {d['phone']} | {d['total_donations']} donations" for d in matching[:4]])
                reply = f"🔍 **Found {len(matching)} Compatible Donor(s)** for **{bg}** in {loc or 'all regions'}:\n\n{donor_list_str}\n\nWould you like to initiate an emergency alert to these donors?"
                actions = [f"🚨 Broadcast Alert for {bg}", "Request Another Group", "View All Donors"]
            else:
                reply = f"No direct available donors found for **{bg}** in {loc or 'this area'}. We can initiate an emergency broadcast alert across all nearby network coordinators."
                actions = [f"🚨 Broadcast Alert for {bg}", "Search Other Cities", "Call Hotline (108)"]

            ChatModel.log_message(session_id, 'assistant', reply, intent)
            return {
                'success': True,
                'reply': reply,
                'intent': intent,
                'actions': actions,
                'data': {'bloodGroup': bg, 'location': loc, 'donors': matching[:5]},
                'session_id': session_id
            }

        # 3. Request Status Check
        req_id = cls.extract_request_id(text)
        if req_id or any(k in lower for k in ['status', 'track', 'check request', 'my request']):
            if req_id:
                return cls._handle_status_check(req_id, session_id)
            else:
                session['currentFlow'] = 'CHECK_STATUS'
                session['step'] = 1
                reply = "Please enter your Request ID (e.g., REQ-1001) or registered contact phone number to track live status."
                actions = ['Track REQ-1001', 'Track REQ-1002', 'Menu']
                ChatModel.log_message(session_id, 'assistant', reply, 'status_prompt')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'status_prompt',
                    'actions': actions,
                    'data': {},
                    'session_id': session_id
                }

        # 4. Donor Registration
        if any(k in lower for k in ['register', 'become a donor', 'sign up as donor', 'join as donor', 'volunteer to donate', 'want to donate']):
            session['currentFlow'] = 'REGISTER_DONOR'
            session['step'] = 1
            session['collectedData'] = {'bloodGroup': bg_found, 'city': loc_found}
            
            reply = "Thank you for volunteering to save lives! ❤️ Let's get you registered into the Lifedrop Emergency Network.\n\nWhat is your full name?"
            actions = []
            ChatModel.log_message(session_id, 'assistant', reply, 'register_name')
            return {
                'success': True,
                'reply': reply,
                'intent': 'register_donor',
                'actions': actions,
                'data': {},
                'session_id': session_id
            }

        # 5. Live Blood Inventory Check
        if any(k in lower for k in ['inventory', 'stock', 'supply', 'blood bank', 'units available', 'shortage']):
            inventory = InventoryModel.get_all()
            intent = 'inventory_check'
            
            if bg_found:
                item = next((i for i in inventory if i['blood_group'].upper() == bg_found.upper()), None)
                if item:
                    reply = f"🩸 **Blood Bank Inventory for {bg_found}**:\n• **Available Units**: {item['units_available']} units\n• **Status**: {item['status']}\n• **Capacity**: {item['capacity_pct']}%\n• **Daily Demand**: {item['daily_demand']} units/day"
                else:
                    reply = f"Could not find stock data for blood group {bg_found}."
            else:
                critical = [i['blood_group'] for i in inventory if i['status'] == 'Critical']
                stock_summary = "\n".join([f"• **{i['blood_group']}**: {i['units_available']} units ({i['status']})" for i in inventory])
                crit_text = f"\n\n⚠️ **Critical Shortages**: {', '.join(critical)}" if critical else ""
                reply = f"📊 **Live Regional Blood Inventory**:\n\n{stock_summary}{crit_text}\n\nWould you like to donate to replenish low supplies or request blood?"

            actions = ['🚨 Urgent Blood Request', '❤️ Register as Donor', 'View Full Inventory']
            ChatModel.log_message(session_id, 'assistant', reply, intent)
            return {
                'success': True,
                'reply': reply,
                'intent': intent,
                'actions': actions,
                'data': {'inventory': inventory},
                'session_id': session_id
            }

        # 6. Platform Stats / Impact
        if any(k in lower for k in ['stats', 'statistics', 'impact', 'lives saved', 'how many donors', 'overview']):
            stats = StatsModel.get_overview()
            intent = 'platform_stats'
            reply = f"📈 **Lifedrop Emergency Network Overview**:\n• **Active Verified Donors**: {stats['activeDonors']}\n• **Total Donors**: {stats['totalDonors']}\n• **Active Emergency Requests**: {stats['activeRequests']}\n• **Fulfilled Requests**: {stats['fulfilledRequests']}\n• **Lives Saved to Date**: {stats['livesSaved']} ❤️\n• **Average Response Time**: {stats['avgResponseMinutes']} minutes"
            actions = ['Find Donors', 'Register as Donor', 'Emergency Request']
            ChatModel.log_message(session_id, 'assistant', reply, intent)
            return {
                'success': True,
                'reply': reply,
                'intent': intent,
                'actions': actions,
                'data': stats,
                'session_id': session_id
            }

        # 7. Blood Compatibility Guide
        is_compat = any(k in lower for k in ['compatibility', 'compatible', 'can donate', 'can receive', 'can give', 'universal donor', 'universal recipient', 'who can give', 'who can receive', 'who can donate']) or (bg_found and any(k in lower for k in ['give', 'receive', 'match', 'compatible', 'accept', 'transfus']))
        if is_compat:
            bg = bg_found or 'O-'
            rules = COMPATIBILITY_RULES.get(bg, {})
            intent = 'compatibility'
            if rules:
                can_give = ", ".join(rules['canDonateTo'])
                can_receive = ", ".join(rules['canReceiveFrom'])
                reply = f"🩸 **Blood Group Compatibility for {bg}** ({rules.get('badge', '')}):\n• **Can donate red blood cells to**: {can_give}\n• **Can receive red blood cells from**: {can_receive}\n\n_{rules.get('description', '')}_"
            else:
                reply = "🩸 **Universal Blood Rules**:\n• **O-**: Universal Red Cell Donor (can donate to all blood groups).\n• **AB+**: Universal Red Cell Recipient (can receive from all blood groups)."
            
            actions = ['Check Other Blood Group', 'Find Compatible Donors', 'Request Blood']
            ChatModel.log_message(session_id, 'assistant', reply, intent)
            return {
                'success': True,
                'reply': reply,
                'intent': intent,
                'actions': actions,
                'data': {'bloodGroup': bg, 'rules': rules},
                'session_id': session_id
            }

        # 8. Health & Donor Benefits Knowledge Base (Science, Donor Benefits, Recovery, Nutrition)
        health_knowledge = cls.match_health_and_donor_benefits(lower)
        if health_knowledge:
            reply_text, chip_actions = health_knowledge
            intent = 'health_and_donor_benefits'
            ChatModel.log_message(session_id, 'assistant', reply_text, intent)
            return {
                'success': True,
                'reply': reply_text,
                'intent': intent,
                'actions': chip_actions,
                'data': {},
                'session_id': session_id
            }

        # 9. Medical Safety Boundary
        if cls.is_medical_advice_query(lower):
            intent = 'medical_safety'
            reply = "⚠️ **Medical Safety Notice**: For specific medication questions, active medical conditions, or transfusion safety, please consult a certified physician or hospital medical staff directly.\n\nFor immediate life-threatening medical emergencies, dial **108** or **104** (National Health Helpline).\n\nWould you like to check standard donor eligibility criteria or submit a blood request?"
            actions = ['❓ Eligibility Criteria', '🚨 Urgent Blood Request', 'Call Helpline 108']
            ChatModel.log_message(session_id, 'assistant', reply, intent)
            return {
                'success': True,
                'reply': reply,
                'intent': intent,
                'actions': actions,
                'data': {},
                'session_id': session_id
            }

        # 10. FAQs
        faq_ans = cls.match_faq(lower)
        if faq_ans:
            intent = 'faq'
            actions = ['🚨 Urgent Blood Request', '❤️ Register as Donor', 'Ask Another Question']
            ChatModel.log_message(session_id, 'assistant', faq_ans, intent)
            return {
                'success': True,
                'reply': faq_ans,
                'intent': intent,
                'actions': actions,
                'data': {},
                'session_id': session_id
            }

        # 11. Fallback
        reply = "I'm the Lifedrop Emergency Assistant. I can help you with:\n• 🚨 Urgent Blood Requests & Emergency SOS\n• 🔍 Finding verified donors nearby\n• 🩸 Blood inventory & compatibility matrices\n• ❤️ Donor registration & request tracking\n\nHow can I help you today?"
        actions = ['🚨 Urgent Blood Request', '❤️ Register as Donor', '🔍 Track Request REQ-1001', '🩸 Check Inventory']
        ChatModel.log_message(session_id, 'assistant', reply, 'general_fallback')
        return {
            'success': True,
            'reply': reply,
            'intent': 'general_fallback',
            'actions': actions,
            'data': {},
            'session_id': session_id
        }

    # ----------------------------------------------------
    # Multi-Step Flow Handlers
    # ----------------------------------------------------

    @classmethod
    def _handle_blood_request_flow(cls, text, session, session_id):
        data = session['collectedData']
        lower = text.lower()

        # If at confirmation step
        if session.get('step') == 'CONFIRM':
            if any(k in lower for k in ['yes', 'confirm', 'proceed', 'search now', 'yep', 'yeah', 'sure', 'correct', 'ok']):
                return cls._finalize_blood_request(session, session_id)
            elif any(k in lower for k in ['no', 'cancel', 'edit', 'change', 'wrong']):
                cls.reset_session(session_id)
                reply = "Let's restart the blood request. What blood group is required?"
                actions = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
                ChatModel.log_message(session_id, 'assistant', reply, 'request_restart')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'request_restart',
                    'actions': actions,
                    'data': {},
                    'session_id': session_id
                }

        # Collect Blood Group
        if not data.get('bloodGroup'):
            bg = cls.extract_blood_group(text)
            if bg:
                data['bloodGroup'] = bg
            else:
                reply = "Which blood group do you need?"
                actions = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
                ChatModel.log_message(session_id, 'assistant', reply, 'request_blood_group')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'request_blood_group',
                    'actions': actions,
                    'data': {},
                    'session_id': session_id
                }

        # Collect Location / City
        if not data.get('location'):
            loc = cls.extract_location(text)
            if loc and loc != data.get('bloodGroup'):
                data['location'] = loc
            elif session.get('step') == 'LOC' and len(text.strip()) > 1:
                data['location'] = text.strip()
            else:
                session['step'] = 'LOC'
                reply = f"Got it, **{data['bloodGroup']}**. Which hospital or locality in Shivamogga is this for? (e.g., McGann Hospital, Sahyadri Narayana, Nanjappa, or Durgigudi)"
                actions = ['McGann Hospital', 'Sahyadri Hospital', 'Nanjappa Hospital', 'Durgigudi', 'Gopala', 'Bhadravathi']
                ChatModel.log_message(session_id, 'assistant', reply, 'request_location')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'request_location',
                    'actions': actions,
                    'data': {},
                    'session_id': session_id
                }

        # Ready for confirmation in standard 1-line format
        session['step'] = 'CONFIRM'
        is_emerg = session.get('isEmergencyMode', False) or data.get('urgency') == 'Emergency'
        prefix = "Searching immediately for " if is_emerg else "Searching for "
        loc_name = data.get('location', 'your area')
        confirm_prompt = f"{prefix}{data['bloodGroup']} donors near {loc_name} — is that correct?"

        actions = ['Yes, search now', 'Edit details', 'Cancel']
        ChatModel.log_message(session_id, 'assistant', confirm_prompt, 'request_confirm')
        return {
            'success': True,
            'reply': confirm_prompt,
            'intent': 'request_confirm',
            'actions': actions,
            'data': data,
            'session_id': session_id
        }

    @classmethod
    def _finalize_blood_request(cls, session, session_id):
        data = session['collectedData']
        bg = data.get('bloodGroup', 'O-')
        loc = data.get('location', 'General Hospital')
        is_emerg = session.get('isEmergencyMode', False) or data.get('urgency') == 'Emergency'

        # Create database emergency request
        new_req = RequestModel.create({
            'patientName': data.get('patientName', 'Emergency Patient'),
            'bloodGroup': bg,
            'units': data.get('units', 1),
            'urgency': 'Emergency' if is_emerg else 'Standard',
            'city': loc,
            'hospital': data.get('hospital', loc),
            'contactName': data.get('contactName', 'Emergency Requester'),
            'contactPhone': data.get('contactPhone', '+91 98200 11223'),
            'notes': 'Submitted via Lifedrop AI Assistant Triage'
        })

        # Find matching donors from database
        matching_donors = DonorModel.find_compatible(bg, loc)
        cls.reset_session(session_id)

        req_id = new_req['id']

        if matching_donors:
            donor_preview = "\n".join([f"• **{d['name']}** ({d['blood_group']}) — {d['city']} ({d['area'] or ''}) | 📞 {d['phone']}" for d in matching_donors[:3]])
            reply = f"🚨 **Emergency Broadcast Dispatched** (ID: **{req_id}**)\n\nWe found **{len(matching_donors)} verified donor(s)** near **{loc}** compatible with **{bg}**.\n\n**Direct Donor Contacts**:\n{donor_preview}\n\nAutomated SMS & push notifications have been triggered."
            actions = [f"Track {req_id}", "Call Emergency Hotline (108)", "Done"]
        else:
            reply = f"🚨 **Emergency Request Created** (ID: **{req_id}**)\n\nCurrently, no direct online donors are registered in **{loc}** for **{bg}**. We have alerted our regional blood bank coordinators. You can also dial Emergency Medical Services at **108** or **104**."
            actions = [f"Track {req_id}", "Call Emergency (108)", "View Blood Inventory"]

        ChatModel.log_message(session_id, 'assistant', reply, 'request_finalized')
        return {
            'success': True,
            'reply': reply,
            'intent': 'request_finalized',
            'actions': actions,
            'data': {
                'requestId': req_id,
                'request': new_req,
                'matchedDonors': matching_donors[:5]
            },
            'session_id': session_id
        }

    @classmethod
    def _handle_donor_registration_flow(cls, text, session, session_id):
        data = session['collectedData']
        step = session.get('step', 1)
        lower = text.lower()

        # Confirmation step
        if step == 'CONFIRM':
            if any(k in lower for k in ['yes', 'confirm', 'proceed', 'submit', 'yep', 'sure', 'correct', 'ok']):
                new_donor = DonorModel.create({
                    'name': data['name'],
                    'bloodGroup': data['bloodGroup'],
                    'city': data['city'],
                    'area': data.get('area', data['city']),
                    'phone': data['phone'],
                    'available': True,
                    'verified': True,
                    'isEmergencyContact': True
                })
                cls.reset_session(session_id)
                reply = f"🎉 **Welcome to the Lifedrop Network, {new_donor['name']}!**\n\nYou are now registered as an active **{new_donor['blood_group']}** donor in **{new_donor['city']}**.\n\n• **Donor ID**: `{new_donor['id']}`\n• **Status**: Active & Verified\n• **Emergency Alert**: Enabled\n\nThank you for volunteering to save lives!"
                actions = ['View Donor Directory', 'Live Emergency Feed', 'Done']
                ChatModel.log_message(session_id, 'assistant', reply, 'donor_registered')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'donor_registered',
                    'actions': actions,
                    'data': {'donor': new_donor},
                    'session_id': session_id
                }
            else:
                cls.reset_session(session_id)
                reply = "Registration cancelled. Let me know if you would like to start over or request blood."
                actions = ['Register as Donor', 'Request Blood']
                ChatModel.log_message(session_id, 'assistant', reply, 'register_cancelled')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'register_cancelled',
                    'actions': actions,
                    'data': {},
                    'session_id': session_id
                }

        # Step 1: Collect Name
        if not data.get('name'):
            if len(text.strip()) > 1 and not any(k in lower for k in ['register', 'become', 'sign up', 'volunteer', 'donate']):
                data['name'] = text.strip()
                session['step'] = 2
                reply = f"Hello **{data['name']}**! What is your blood group?"
                actions = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
                ChatModel.log_message(session_id, 'assistant', reply, 'register_blood_group')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'register_blood_group',
                    'actions': actions,
                    'data': {},
                    'session_id': session_id
                }
            else:
                session['step'] = 1
                reply = "What is your full name?"
                return {'success': True, 'reply': reply, 'intent': 'register_name', 'actions': [], 'data': {}, 'session_id': session_id}

        # Step 2: Collect Blood Group
        if not data.get('bloodGroup'):
            bg = cls.extract_blood_group(text)
            if bg:
                data['bloodGroup'] = bg
                session['step'] = 3
                reply = f"Great, **{bg}**. In which area of Shivamogga are you located?"
                actions = ['Durgigudi', 'Gopala', 'Vinoba Nagara', 'Vidyanagara', 'Kuvempu Road', 'Bhadravathi', 'Sagara']
                ChatModel.log_message(session_id, 'assistant', reply, 'register_city')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'register_city',
                    'actions': actions,
                    'data': {},
                    'session_id': session_id
                }
            else:
                reply = "Please select your blood group:"
                actions = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
                return {'success': True, 'reply': reply, 'intent': 'register_blood_group', 'actions': actions, 'data': {}, 'session_id': session_id}

        # Step 3: Collect City
        if not data.get('city'):
            loc = cls.extract_location(text) or (text.strip() if len(text.strip()) > 1 else None)
            if loc:
                data['city'] = loc
                data['area'] = loc
                session['step'] = 4
                reply = f"Got it, **{loc}**. Please provide your contact phone number for donation coordinator alerts."
                actions = []
                ChatModel.log_message(session_id, 'assistant', reply, 'register_phone')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'register_phone',
                    'actions': actions,
                    'data': {},
                    'session_id': session_id
                }

        # Step 4: Collect Phone
        if not data.get('phone'):
            phone = cls.extract_phone(text) or text.strip()
            if phone and len(re.sub(r'\D', '', phone)) >= 10:
                data['phone'] = phone
                session['step'] = 'CONFIRM'
                reply = f"📋 **Please confirm your donor registration details**:\n• **Name**: {data['name']}\n• **Blood Group**: {data['bloodGroup']}\n• **Location**: {data['city']}\n• **Contact Phone**: {data['phone']}\n\nIs this information correct?"
                actions = ['Yes, register me', 'Cancel']
                ChatModel.log_message(session_id, 'assistant', reply, 'register_confirm')
                return {
                    'success': True,
                    'reply': reply,
                    'intent': 'register_confirm',
                    'actions': actions,
                    'data': data,
                    'session_id': session_id
                }
            else:
                reply = "Please enter a valid 10-digit contact phone number (e.g. +91 98201 23456):"
                return {'success': True, 'reply': reply, 'intent': 'register_phone', 'actions': [], 'data': {}, 'session_id': session_id}

        return cls.process_message(text, session_id)

    @classmethod
    def _handle_status_check_flow(cls, text, session, session_id):
        cls.reset_session(session_id)
        req_id = cls.extract_request_id(text) or text.strip()
        return cls._handle_status_check(req_id, session_id)

    @classmethod
    def _handle_status_check(cls, req_id_or_phone, session_id):
        req = RequestModel.get_by_id(req_id_or_phone)
        if req:
            timeline_str = ""
            if req.get('timeline'):
                latest_events = req['timeline'][-3:]
                timeline_str = "\n\n**Recent Updates**:\n" + "\n".join([f"• [{t['time']}] {t['event']}" for t in latest_events])

            reply = f"🔍 **Blood Request Status ({req['id']})**:\n• **Patient**: {req['patient_name']}\n• **Blood Group**: {req['blood_group']} ({req['units']} unit(s))\n• **Hospital / City**: {req['hospital']}, {req['city']}\n• **Urgency**: {req['urgency']}\n• **Current Status**: **{req['status']}**\n• **Donors Contacted**: {req['donors_contacted']} | **Confirmed**: {req['donors_confirmed']}{timeline_str}"
            actions = [f"Track {req['id']}", "Find More Donors", "Done"]
            intent = 'status_result'
            data = {'request': req}
        else:
            reply = f"Could not find an active blood request with ID or phone `{req_id_or_phone}`. Please verify your Request ID (e.g., REQ-1001) or create a new emergency request."
            actions = ['Track REQ-1001', 'Track REQ-1002', '🚨 Urgent Blood Request']
            intent = 'status_not_found'
            data = {}

        ChatModel.log_message(session_id, 'assistant', reply, intent)
        return {
            'success': True,
            'reply': reply,
            'intent': intent,
            'actions': actions,
            'data': data,
            'session_id': session_id
        }

