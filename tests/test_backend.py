"""
Lifedrop - Automated Backend & Database Test Suite
"""

import os
import sys
import unittest
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.db import init_db, get_db_connection
from backend.models import DonorModel, RequestModel, InventoryModel, StatsModel
from backend.server import app

class LifedropBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_01_db_tables_exist(self):
        """Verify all SQLite tables were created."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()

        expected_tables = ['donors', 'requests', 'request_timeline', 'inventory', 'broadcast_notifications', 'chat_messages']
        for tbl in expected_tables:
            self.assertIn(tbl, tables, f"Table {tbl} should exist in database")

    def test_02_health_endpoint(self):
        """Test GET /api/health."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'online')

    def test_03_stats_endpoint(self):
        """Test GET /api/stats."""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('totalDonors', data['data'])

    def test_04_donor_crud_and_matching(self):
        """Test Donor registration and compatibility search."""
        # 1. Register test donor
        test_donor = {
            'name': 'Test Universal Donor',
            'bloodGroup': 'O-',
            'city': 'TestCity',
            'area': 'TestArea',
            'phone': '+91 99999 00000',
            'email': 'donor.test@example.com',
            'age': 28,
            'weight': 65.0
        }
        create_res = self.client.post('/api/donors', json=test_donor)
        self.assertEqual(create_res.status_code, 201)
        created_donor = json.loads(create_res.data)['data']
        donor_id = created_donor['id']

        # 2. Get by ID
        get_res = self.client.get(f'/api/donors/{donor_id}')
        self.assertEqual(get_res.status_code, 200)
        fetched = json.loads(get_res.data)['data']
        self.assertEqual(fetched['name'], 'Test Universal Donor')

        # 3. Compatible donor matching (O- is universal donor, should match recipient of type AB+)
        match_res = self.client.get('/api/donors/match?bloodGroup=AB+&city=TestCity')
        self.assertEqual(match_res.status_code, 200)
        matching = json.loads(match_res.data)['data']
        donor_ids = [d['id'] for d in matching]
        self.assertIn(donor_id, donor_ids, "O- donor should be in compatible matches for AB+ recipient")

    def test_05_emergency_request_lifecycle(self):
        """Test Request submission, automated donor alerts, and status update."""
        req_payload = {
            'patientName': 'Emergency Patient Test',
            'bloodGroup': 'A+',
            'units': 2,
            'hospital': 'City Care Hospital',
            'city': 'Mumbai',
            'urgency': 'Emergency',
            'contactName': 'Kin Contact',
            'contactPhone': '+91 98765 43210',
            'notes': 'Urgent requirement'
        }

        # 1. Submit Request
        post_res = self.client.post('/api/requests', json=req_payload)
        self.assertEqual(post_res.status_code, 201)
        req_data = json.loads(post_res.data)['data']
        req_id = req_data['id']
        self.assertTrue(len(req_data['timeline']) >= 1)

        # 2. Track Request by ID
        get_res = self.client.get(f'/api/requests/{req_id}')
        self.assertEqual(get_res.status_code, 200)
        tracked = json.loads(get_res.data)['data']
        self.assertEqual(tracked['blood_group'], 'A+')

        # 3. Update Status
        patch_res = self.client.patch(f'/api/requests/{req_id}', json={'status': 'Fulfilled', 'donorsConfirmed': 2})
        self.assertEqual(patch_res.status_code, 200)
        updated = json.loads(patch_res.data)['data']
        self.assertEqual(updated['status'], 'Fulfilled')
        self.assertEqual(updated['donors_confirmed'], 2)

    def test_06_inventory_apis(self):
        """Test GET and PATCH for blood inventory."""
        get_res = self.client.get('/api/inventory')
        self.assertEqual(get_res.status_code, 200)
        items = json.loads(get_res.data)['data']
        self.assertTrue(len(items) >= 8)

        patch_res = self.client.patch('/api/inventory/O+', json={'units_available': 150})
        self.assertEqual(patch_res.status_code, 200)
        updated = json.loads(patch_res.data)['data']
        self.assertEqual(updated['units_available'], 150)

    def test_07_assistant_emergency_request_flow(self):
        """Test AI Chatbot multi-step emergency blood request flow."""
        session_id = 'test_sess_req_01'

        # Step 1: User says emergency need blood
        res1 = self.client.post('/api/assistant/chat', json={
            'message': 'Emergency need blood for accident patient',
            'session_id': session_id
        })
        self.assertEqual(res1.status_code, 200)
        d1 = json.loads(res1.data)
        self.assertTrue(d1['success'])
        self.assertIn('blood group', d1['reply'].lower())

        # Step 2: Provide blood group
        res2 = self.client.post('/api/assistant/chat', json={
            'message': 'O-',
            'session_id': session_id
        })
        self.assertEqual(res2.status_code, 200)
        d2 = json.loads(res2.data)
        self.assertTrue(d2['success'])
        self.assertTrue('hospital' in d2['reply'].lower() or 'shivamogga' in d2['reply'].lower())

        # Step 3: Provide location
        res3 = self.client.post('/api/assistant/chat', json={
            'message': 'McGann Hospital',
            'session_id': session_id
        })
        self.assertEqual(res3.status_code, 200)
        d3 = json.loads(res3.data)
        self.assertTrue(d3['success'])
        self.assertIn('is that correct', d3['reply'].lower())

        # Step 4: Confirm request creation
        res4 = self.client.post('/api/assistant/chat', json={
            'message': 'Yes, proceed',
            'session_id': session_id
        })
        self.assertEqual(res4.status_code, 200)
        d4 = json.loads(res4.data)
        self.assertTrue(d4['success'])
        self.assertIn('requestId', d4['data'])
        self.assertTrue(d4['data']['requestId'].startswith('REQ-'))

    def test_08_assistant_donor_search(self):
        """Test AI Chatbot direct natural language donor search."""
        res = self.client.post('/api/assistant/chat', json={
            'message': 'Find O- donors in Shivamogga',
            'session_id': 'test_sess_search'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['intent'], 'donor_search')
        self.assertIn('donors', data['data'])
        self.assertTrue(len(data['data']['donors']) > 0)

    def test_09_assistant_status_check(self):
        """Test AI Chatbot request status lookup."""
        res = self.client.post('/api/assistant/chat', json={
            'message': 'Check status of REQ-1001',
            'session_id': 'test_sess_status'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['intent'], 'status_result')
        self.assertIn('REQ-1001', data['reply'])
        self.assertIn('McGann Teaching Hospital', data['reply'])

    def test_10_assistant_inventory_query(self):
        """Test AI Chatbot inventory and stock level queries."""
        res = self.client.post('/api/assistant/chat', json={
            'message': 'How much O- blood is available in blood bank?',
            'session_id': 'test_sess_inv'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['intent'], 'inventory_check')
        self.assertIn('O-', data['reply'])
        self.assertIn('units', data['reply'].lower())

    def test_11_assistant_compatibility_query(self):
        """Test AI Chatbot blood compatibility guide."""
        res = self.client.post('/api/assistant/chat', json={
            'message': 'Who can receive O- blood?',
            'session_id': 'test_sess_compat'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['intent'], 'compatibility')
        self.assertIn('O-', data['reply'])

    def test_12_assistant_donor_registration(self):
        """Test AI Chatbot multi-step donor registration flow."""
        session_id = 'test_sess_reg_01'

        # Step 1: Initiate
        res1 = self.client.post('/api/assistant/chat', json={
            'message': 'I want to register as a donor',
            'session_id': session_id
        })
        self.assertEqual(res1.status_code, 200)
        d1 = json.loads(res1.data)
        self.assertIn('name', d1['reply'].lower())

        # Step 2: Name
        res2 = self.client.post('/api/assistant/chat', json={
            'message': 'Kavya Rao',
            'session_id': session_id
        })
        self.assertEqual(res2.status_code, 200)
        d2 = json.loads(res2.data)
        self.assertIn('blood group', d2['reply'].lower())

        # Step 3: Blood Group
        res3 = self.client.post('/api/assistant/chat', json={
            'message': 'B+',
            'session_id': session_id
        })
        self.assertEqual(res3.status_code, 200)
        d3 = json.loads(res3.data)
        self.assertTrue('area' in d3['reply'].lower() or 'shivamogga' in d3['reply'].lower() or 'city' in d3['reply'].lower())

        # Step 4: City
        res4 = self.client.post('/api/assistant/chat', json={
            'message': 'Durgigudi',
            'session_id': session_id
        })
        self.assertEqual(res4.status_code, 200)
        d4 = json.loads(res4.data)
        self.assertIn('phone', d4['reply'].lower())

        # Step 5: Phone
        res5 = self.client.post('/api/assistant/chat', json={
            'message': '+91 98450 11223',
            'session_id': session_id
        })
        self.assertEqual(res5.status_code, 200)
        d5 = json.loads(res5.data)
        self.assertIn('confirm', d5['reply'].lower())

        # Step 6: Confirm
        res6 = self.client.post('/api/assistant/chat', json={
            'message': 'Yes, register me',
            'session_id': session_id
        })
        self.assertEqual(res6.status_code, 200)
        d6 = json.loads(res6.data)
        self.assertTrue(d6['success'])
        self.assertEqual(d6['intent'], 'donor_registered')
        self.assertIn('donor', d6['data'])
        self.assertTrue(d6['data']['donor']['id'].startswith('DON-'))

    def test_13_assistant_medical_safety_filter(self):
        """Test AI Chatbot clinical boundary filter for medical conditions."""
        res = self.client.post('/api/assistant/chat', json={
            'message': 'Can I donate blood if I have chemotherapy or HIV infection?',
            'session_id': 'test_sess_med'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['intent'], 'medical_safety')
        self.assertIn('physician', data['reply'].lower())
        self.assertIn('108', data['reply'])

    def test_14_assistant_chat_logging_and_history(self):
        """Test SQLite message logging and history retrieval."""
        session_id = 'test_sess_logging'
        self.client.post('/api/assistant/chat', json={'message': 'Need O- blood', 'session_id': session_id})
        
        hist_res = self.client.get(f'/api/assistant/history/{session_id}')
        self.assertEqual(hist_res.status_code, 200)
        data = json.loads(hist_res.data)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['data']) >= 2)  # User message + Assistant response

    def test_15_assistant_donor_health_benefits(self):
        """Test AI Chatbot response for donor health benefits queries."""
        queries = [
            'how helps donor when he donates blood',
            'what are the benefits of blood donation for the donor',
            'why should I donate blood and how does it help my health'
        ]
        for q in queries:
            res = self.client.post('/api/assistant/chat', json={
                'message': q,
                'session_id': 'test_sess_benefits'
            })
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['intent'], 'health_and_donor_benefits')
            self.assertIn('Screening', data['reply'])
            self.assertIn('Erythropoiesis', data['reply'])
            self.assertIn('Iron', data['reply'])
            self.assertIn('calories', data['reply'])

    def test_16_assistant_blood_science_and_nutrition(self):
        """Test AI Chatbot response for bone marrow replenishment, diet, and platelet donation."""
        # 1. Bone marrow replenishment
        res1 = self.client.post('/api/assistant/chat', json={
            'message': 'how does bone marrow produce new blood after donation',
            'session_id': 'test_sess_science'
        })
        d1 = json.loads(res1.data)
        self.assertEqual(d1['intent'], 'health_and_donor_benefits')
        self.assertIn('Biological Renewal Timeline', d1['reply'])
        self.assertIn('Platelets', d1['reply'])

        # 2. Nutrition and iron-rich diet
        res2 = self.client.post('/api/assistant/chat', json={
            'message': 'how to increase hemoglobin and what iron rich food to eat',
            'session_id': 'test_sess_science'
        })
        d2 = json.loads(res2.data)
        self.assertEqual(d2['intent'], 'health_and_donor_benefits')
        self.assertIn('Vitamin C Multiplier', d2['reply'])

        # 3. Platelet and plasma donation
        res3 = self.client.post('/api/assistant/chat', json={
            'message': 'what is platelet donation vs whole blood',
            'session_id': 'test_sess_science'
        })
        d3 = json.loads(res3.data)
        self.assertEqual(d3['intent'], 'health_and_donor_benefits')
        self.assertIn('Apheresis', d3['reply'])


if __name__ == '__main__':
    unittest.main()

